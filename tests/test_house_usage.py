import importlib.util
import json
import plistlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("house_usage", Path(__file__).resolve().parent.parent / "tools" / "house-usage.py")
hu = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hu)

NOW = 1_800_000_000.0
DAY = 86400
SINCE = NOW - 7 * DAY
RECENT = NOW - DAY
OLD = NOW - 30 * DAY


def iso(stamp):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(stamp, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class ReaderCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.support = self.home / "Library" / "Application Support"
        self.support.mkdir(parents=True)
        self.health = None
        self.procs = []

    def ctx(self):
        return hu.Ctx(self.home, SINCE, NOW, lambda url: self.health, lambda: self.procs)

    def run_reader(self, app):
        return hu.READERS[app](self.ctx())

    def by_metric(self, rows):
        return {r.metric: r for r in rows}


class MissingStores(ReaderCase):
    def test_every_reader_reports_no_store_on_an_empty_home(self):
        for app in ("Local Dictation", "Quick Launch", "RTI", "Cotype", "memory-screenctx", "Usage"):
            rows = self.run_reader(app)
            self.assertTrue(rows, app)
            self.assertTrue(all(r.count is None and r.source.startswith("no store") for r in rows), app)

    def test_unreachable_daemon_is_zero_not_a_crash(self):
        (row,) = self.run_reader("local-models")
        self.assertEqual(row.count, 0)

    def test_collect_covers_every_registered_app(self):
        apps = {r.app for r in hu.collect(self.ctx())}
        self.assertEqual(apps, set(hu.READERS))


class Dictation(ReaderCase):
    def test_counts_only_rows_in_window(self):
        path = self.home / ".config" / "local-dictation"
        path.mkdir(parents=True)
        db = sqlite3.connect(path / "history.db")
        db.execute("CREATE TABLE dictations (id INTEGER PRIMARY KEY, text TEXT, created_at INTEGER)")
        db.executemany("INSERT INTO dictations (text, created_at) VALUES ('x', ?)", [(int(RECENT),), (int(RECENT) + 5,), (int(OLD),)])
        db.commit()
        db.close()
        (row,) = self.run_reader("Local Dictation")
        self.assertEqual((row.count, row.last_seen), (2, int(RECENT) + 5))

    def test_store_is_not_modified(self):
        path = self.home / ".config" / "local-dictation"
        path.mkdir(parents=True)
        db = sqlite3.connect(path / "history.db")
        db.execute("CREATE TABLE dictations (id INTEGER PRIMARY KEY, text TEXT, created_at INTEGER)")
        db.commit()
        db.close()
        before = (path / "history.db").read_bytes()
        self.run_reader("Local Dictation")
        self.assertEqual((path / "history.db").read_bytes(), before)


class QuickLaunch(ReaderCase):
    def test_events_by_kind_and_chat_turns(self):
        root = self.support / "Quick Launch"
        (root / "chats").mkdir(parents=True)
        events = [
            {"kind": "aiSucceeded", "date": RECENT - hu.APPLE_EPOCH},
            {"kind": "aiSucceeded", "date": RECENT - hu.APPLE_EPOCH},
            {"kind": "directHotkeyUse", "date": RECENT - hu.APPLE_EPOCH},
            {"kind": "aiSucceeded", "date": OLD - hu.APPLE_EPOCH},
        ]
        (root / "interaction-journal.json").write_text(json.dumps({"version": 2, "events": events}))
        fresh = {"conversation": {"updatedAt": iso(RECENT), "turns": [{}, {}, {}]}}
        stale = {"conversation": {"updatedAt": iso(OLD), "turns": [{}]}}
        (root / "chats" / "a.json").write_text(json.dumps(fresh))
        (root / "chats" / "b.json").write_text(json.dumps(stale))
        got = self.by_metric(self.run_reader("Quick Launch"))
        self.assertEqual(got["event aiSucceeded"].count, 2)
        self.assertEqual(got["event directHotkeyUse"].count, 1)
        self.assertEqual(got["chat turns (chats updated in window)"].count, 3)


class Rti(ReaderCase):
    def test_sessions_and_configured_corpus(self):
        sessions = self.support / "RTI" / "sessions"
        (sessions / "2026 one").mkdir(parents=True)
        corpus = self.home / "corpus"
        (corpus / "sub").mkdir(parents=True)
        (corpus / "sub" / "note.md").write_text("x")
        prefs = self.home / "Library" / "Preferences"
        prefs.mkdir(parents=True)
        (prefs / "com.tristan.rti.plist").write_bytes(plistlib.dumps({"rti.corpus.path": str(corpus)}))
        import os
        os.utime(sessions / "2026 one", (RECENT, RECENT))
        os.utime(corpus / "sub" / "note.md", (RECENT, RECENT))
        got = self.by_metric(self.run_reader("RTI"))
        self.assertEqual(got["session folders"].count, 1)
        self.assertEqual(got["corpus files written"].count, 1)

    def test_configured_but_missing_corpus_is_no_store(self):
        prefs = self.home / "Library" / "Preferences"
        prefs.mkdir(parents=True)
        (prefs / "com.tristan.rti.plist").write_bytes(plistlib.dumps({"rti.corpus.path": str(self.home / "gone")}))
        got = self.by_metric(self.run_reader("RTI"))
        self.assertTrue(got["corpus files written"].source.startswith("no store"))


class Cotype(ReaderCase):
    def test_all_time_metrics_and_personalization_mtime(self):
        root = self.support / "Cotype"
        root.mkdir()
        (root / "privacy-metrics.json").write_text(json.dumps({"accepted": 4, "shown": 9}))
        (root / "personalization.json").write_text("{}")
        got = self.by_metric(self.run_reader("Cotype"))
        self.assertEqual(got["accepted completions (all-time, not windowed)"].count, 4)
        self.assertEqual(got["shown completions (all-time, not windowed)"].count, 9)
        self.assertIn("personalization updated in window", got)


class ScreenCtx(ReaderCase):
    def test_window_counts_and_vision_table(self):
        root = self.support / "screenctx"
        root.mkdir()
        db = sqlite3.connect(root / "context.sqlite3")
        db.execute("CREATE TABLE block (id INTEGER PRIMARY KEY, started_at REAL)")
        db.execute("CREATE TABLE tick_log (ts REAL, outcome TEXT)")
        db.execute("CREATE TABLE vision (id INTEGER PRIMARY KEY, ts REAL, summary TEXT)")
        db.executemany("INSERT INTO block (started_at) VALUES (?)", [(RECENT,), (OLD,)])
        db.executemany("INSERT INTO tick_log VALUES (?, 'ok')", [(RECENT,), (RECENT + 1,), (OLD,)])
        db.execute("INSERT INTO vision (ts, summary) VALUES (?, 's')", (RECENT,))
        db.commit()
        db.close()
        got = self.by_metric(self.run_reader("memory-screenctx"))
        self.assertEqual(got["blocks captured"].count, 1)
        self.assertEqual(got["collector ticks"].count, 2)
        self.assertEqual(got["vision rows"].count, 1)


class LocalModels(ReaderCase):
    def test_healthy_daemon_counts_loaded_backends(self):
        self.health = {"backends": {"a": {"loaded_model": "m"}, "b": {"loaded_model": None}}}
        got = self.by_metric(self.run_reader("local-models"))
        self.assertEqual(got["daemon running (no request stats exposed)"].count, 1)
        self.assertEqual(got["backends with a model loaded"].count, 1)


class Usage(ReaderCase):
    def test_launches_in_window(self):
        root = self.support / "Usage"
        root.mkdir()
        lines = [f"{iso(RECENT)} launch pid=1", f"{iso(RECENT)} terminate pid=1", f"{iso(OLD)} launch pid=2"]
        (root / "events.log").write_text("\n".join(lines))
        (row,) = self.run_reader("Usage")
        self.assertEqual(row.count, 1)


class ProcessOnly(ReaderCase):
    def test_running_flags(self):
        self.procs = ["/Applications/Memory.app/Contents/MacOS/memory-bar", "/x/pocket-tts"]
        self.assertEqual(self.run_reader("Memory menu bar")[0].count, 1)
        self.assertEqual(self.run_reader("local-tts")[0].count, 1)
        self.procs = []
        self.assertEqual(self.run_reader("local-tts")[0].count, 0)


class Output(ReaderCase):
    def test_table_and_json_hold_no_content_columns(self):
        rows = [hu.Row("A", "m", 3, NOW, "s"), hu.missing("B", "m", "x")]
        table = hu.render_table(rows)
        self.assertIn("no store: x", table)
        self.assertEqual(len(table.splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
