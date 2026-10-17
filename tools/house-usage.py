#!/usr/bin/env python3
"""Print how much each House app was used in the last N days. Read-only; counts and dates only."""

import argparse
import json
import sqlite3
import subprocess
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

APPLE_EPOCH = 978307200
NO_STORE = "no store"
LOCAL_MODELS_HEALTH = "http://127.0.0.1:8078/health"


@dataclass(frozen=True)
class Row:
    app: str
    metric: str
    count: Optional[int]
    last_seen: Optional[float]
    source: str


@dataclass
class Ctx:
    home: Path
    since: float
    now: float
    http_get: Callable[[str], Optional[dict]]
    process_names: Callable[[], list]
    support: Path = field(init=False)

    def __post_init__(self):
        self.support = self.home / "Library" / "Application Support"

    def running(self, needle):
        return any(needle in name for name in self.process_names())


def missing(app, metric, source):
    return Row(app, metric, None, None, f"{NO_STORE}: {source}")


def open_ro(path):
    return sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True, timeout=2)


def sql_one(path, query, params=()):
    conn = open_ro(path)
    try:
        return conn.execute(query, params).fetchone()
    finally:
        conn.close()


def read_dictation(ctx):
    db = ctx.home / ".config" / "local-dictation" / "history.db"
    if not db.exists():
        return [missing("Local Dictation", "dictations", "history.db")]
    count, last = sql_one(db, "SELECT COUNT(*), MAX(created_at) FROM dictations WHERE created_at >= ?", (ctx.since,))
    if not count:
        (last,) = sql_one(db, "SELECT MAX(created_at) FROM dictations")
    return [Row("Local Dictation", "dictations", count, last, "history.db")]


def load_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def parse_iso(text):
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError):
        return None


def read_quick_launch(ctx):
    root = ctx.support / "Quick Launch"
    rows = []
    journal = load_json(root / "interaction-journal.json")
    if journal is None:
        rows.append(missing("Quick Launch", "journal events", "interaction-journal.json"))
    else:
        by_kind, last_by_kind = {}, {}
        for event in journal.get("events", []):
            stamp = event.get("date")
            if isinstance(stamp, (int, float)) and stamp + APPLE_EPOCH >= ctx.since:
                kind = event.get("kind", "unknown")
                by_kind[kind] = by_kind.get(kind, 0) + 1
                last_by_kind[kind] = max(last_by_kind.get(kind, 0), stamp + APPLE_EPOCH)
        for kind in sorted(by_kind):
            rows.append(Row("Quick Launch", f"event {kind}", by_kind[kind], last_by_kind[kind], "interaction-journal.json"))
        if not by_kind:
            rows.append(Row("Quick Launch", "journal events", 0, None, "interaction-journal.json"))
    chats = root / "chats"
    if not chats.is_dir():
        rows.append(missing("Quick Launch", "chat turns", "chats/"))
        return rows
    turns, last = 0, None
    for path in chats.glob("*.json"):
        conv = (load_json(path) or {}).get("conversation", {})
        updated = parse_iso(conv.get("updatedAt"))
        if updated is not None and updated >= ctx.since:
            turns += len(conv.get("turns", []))
            last = max(last or 0, updated)
    rows.append(Row("Quick Launch", "chat turns (chats updated in window)", turns, last, "chats/"))
    return rows


def rti_transcripts_dir(ctx):
    config = load_json(ctx.home / ".config" / "rti" / "config.json")
    value = config.get("transcripts_dir") if isinstance(config, dict) else None
    return Path(value).expanduser() if value else None


def files_in_window(root, since):
    stamps = []
    for path in root.rglob("*"):
        try:
            if path.is_file() and path.stat().st_mtime >= since:
                stamps.append(path.stat().st_mtime)
        except OSError:
            continue
    return len(stamps), max(stamps, default=None)


def read_rti(ctx):
    folder = rti_transcripts_dir(ctx)
    if folder is None:
        return [missing("RTI", "sessions archived", "transcripts_dir in ~/.config/rti/config.json")]
    if not folder.is_dir():
        return [missing("RTI", "sessions archived", "configured transcripts_dir")]
    stamps = [p.stat().st_mtime for p in folder.glob("rti-session-*-transcript.txt")]
    recent = [t for t in stamps if t >= ctx.since]
    return [Row("RTI", "sessions archived", len(recent), max(stamps, default=None), "transcripts_dir rti-session-*-transcript.txt")]


def read_cotype(ctx):
    root = ctx.support / "Cotype"
    if not root.is_dir():
        return [missing("Cotype", "accepted completions", "Cotype/")]
    rows = []
    metrics_file = root / "privacy-metrics.json"
    metrics = load_json(metrics_file)
    if metrics is None:
        rows.append(missing("Cotype", "accepted completions (all-time)", "privacy-metrics.json"))
    else:
        mtime = metrics_file.stat().st_mtime
        for key in ("accepted", "shown"):
            if isinstance(metrics.get(key), int):
                rows.append(Row("Cotype", f"{key} completions (all-time, not windowed)", metrics[key], mtime, "privacy-metrics.json"))
    pers = root / "personalization.json"
    if pers.exists():
        stamp = pers.stat().st_mtime
        rows.append(Row("Cotype", "personalization updated in window", int(stamp >= ctx.since), stamp, "personalization.json mtime"))
    return rows


def vision_stamp_column(db):
    conn = open_ro(db)
    try:
        columns = {r[1] for r in conn.execute("PRAGMA table_info(vision)")}
    finally:
        conn.close()
    return next((c for c in ("ts", "created_at", "captured_at", "started_at") if c in columns), None)


def read_screenctx(ctx):
    db = ctx.support / "screenctx" / "context.sqlite3"
    if not db.exists():
        return [missing("memory-screenctx", "blocks captured", "context.sqlite3")]
    blocks, last_block = sql_one(db, "SELECT COUNT(*), MAX(started_at) FROM block WHERE started_at >= ?", (ctx.since,))
    ticks, last_tick = sql_one(db, "SELECT COUNT(*), MAX(ts) FROM tick_log WHERE ts >= ?", (ctx.since,))
    rows = [
        Row("memory-screenctx", "blocks captured", blocks, last_block, "block"),
        Row("memory-screenctx", "collector ticks", ticks, last_tick, "tick_log"),
    ]
    column = vision_stamp_column(db)
    if column:
        count, last = sql_one(db, f"SELECT COUNT(*), MAX({column}) FROM vision WHERE {column} >= ?", (ctx.since,))
        rows.append(Row("memory-screenctx", "vision rows", count, last, "vision"))
    return rows


def read_local_models(ctx):
    metric = "daemon running (no request stats exposed)"
    health = ctx.http_get(LOCAL_MODELS_HEALTH)
    if health is None:
        return [Row("local-models", metric, 0, None, "127.0.0.1:8078/health unreachable")]
    loaded = sum(1 for b in health.get("backends", {}).values() if b.get("loaded_model"))
    log = ctx.home / "Library" / "Logs" / "local-models.log"
    stamp = log.stat().st_mtime if log.exists() else None
    return [
        Row("local-models", metric, 1, stamp, "127.0.0.1:8078/health, log mtime"),
        Row("local-models", "backends with a model loaded", loaded, None, "127.0.0.1:8078/health"),
    ]


def read_usage(ctx):
    log = ctx.support / "Usage" / "events.log"
    if not log.exists():
        return [missing("Usage", "app launches", "Usage/events.log")]
    launches, last = 0, None
    for line in log.read_text(errors="replace").splitlines():
        stamp, _, rest = line.partition(" ")
        when = parse_iso(stamp)
        if when is not None and when >= ctx.since and rest.startswith("launch"):
            launches += 1
            last = when
    return [Row("Usage", "app launches (no panel-open signal)", launches, last, "Usage/events.log")]


def read_memory_menubar(ctx):
    status = ctx.support / "House" / "commands" / "memory.status.json"
    stamp = status.stat().st_mtime if status.exists() else None
    return [Row("Memory menu bar", "process running (no usage signal)", int(ctx.running("memory-bar")), stamp, "process list, memory.status.json mtime")]


def read_local_tts(ctx):
    log = ctx.home / "Library" / "Logs" / "local-tts.log"
    stamp = log.stat().st_mtime if log.exists() else None
    return [Row("local-tts", "process running (no usage signal)", int(ctx.running("pocket-tts")), stamp, "process list, log mtime includes health polls")]


READERS = {
    "Local Dictation": read_dictation,
    "Quick Launch": read_quick_launch,
    "RTI": read_rti,
    "Cotype": read_cotype,
    "memory-screenctx": read_screenctx,
    "local-models": read_local_models,
    "Usage": read_usage,
    "Memory menu bar": read_memory_menubar,
    "local-tts": read_local_tts,
}


def collect(ctx):
    rows = []
    for app, reader in READERS.items():
        try:
            rows.extend(reader(ctx))
        except (OSError, sqlite3.Error, ValueError) as err:
            rows.append(Row(app, "read failed", None, None, type(err).__name__))
    return rows


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return json.loads(response.read())
    except (OSError, ValueError):
        return None


def list_processes():
    out = subprocess.run(["ps", "-axo", "comm"], capture_output=True, text=True, check=False).stdout
    return out.splitlines()


def fmt_time(stamp):
    if stamp is None:
        return "-"
    return datetime.fromtimestamp(stamp, timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def render_table(rows):
    header = ("app", "metric", "count", "last seen", "source")
    body = [(r.app, r.metric, "-" if r.count is None else str(r.count), fmt_time(r.last_seen), r.source) for r in rows]
    widths = [max(len(line[i]) for line in [header, *body]) for i in range(5)]
    return "\n".join("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(line)).rstrip() for line in [header, *body])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="window length in days (default 7)")
    parser.add_argument("--json", action="store_true", help="print rows as JSON")
    args = parser.parse_args(argv)
    now = time.time()
    ctx = Ctx(Path.home(), now - args.days * 86400, now, fetch_json, list_processes)
    rows = collect(ctx)
    if args.json:
        print(json.dumps({"days": args.days, "rows": [asdict(r) for r in rows]}, indent=2))
    else:
        print(f"House usage, last {args.days} days")
        print(render_table(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
