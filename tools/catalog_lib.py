"""Shared load, validate and render logic for the House System catalog.

The catalog (`catalog/catalog.yaml`) is the machine-readable inventory of the
House components and their layers. This module is the single implementation used
by both `validate_catalog.py` and `build_system_map.py`, so the validator and the
generated view can never drift apart.

Standard library plus PyYAML only. No network, no writes outside the repo.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Iterator

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "catalog" / "catalog.yaml"
DEFAULT_ATLAS = REPO_ROOT.parent / "atlas.yaml"
ATLAS_ENV = "HOUSE_ATLAS"
DEFAULT_MAP = REPO_ROOT / "docs" / "system-map.md"

class AtlasError(Exception):
    """The group relationship file is missing or unreadable. The message is one line."""


def resolve_atlas(explicit: str | Path | None = None) -> tuple[Path, bool]:
    """Return the atlas path and whether the caller chose it.

    Order: an explicit path (the --atlas flag), then the HOUSE_ATLAS
    environment variable, then the parent group file. The last is the default
    and may be absent on a fresh clone; a path the caller chose may not be.
    """
    if explicit:
        return Path(explicit), True
    env = os.environ.get(ATLAS_ENV, "").strip()
    if env:
        return Path(env), True
    return DEFAULT_ATLAS, False


def read_atlas(path: Path) -> dict[str, Any]:
    """Load an atlas file, or raise AtlasError with a one-line reason."""
    path = Path(path)
    if not path.is_file():
        raise AtlasError(
            f"atlas not found: {path} (pass --atlas PATH or set {ATLAS_ENV}; "
            "the group file is ../atlas.yaml next to this repository)"
        )
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        reason = " ".join(str(exc).split())
        raise AtlasError(f"atlas unreadable: {path} ({reason})") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise AtlasError(f"atlas unreadable: {path} (top level is not a mapping)")
    return data


STATUSES = ("current", "experimental", "aspirational")
VISIBILITIES = ("public", "private")

# Top-level list collections: name -> (required fields, extra fields allowed)
LIST_COLLECTIONS = {
    "surfaces": (("id", "name", "kind", "status", "visibility", "description"), ("repo", "uses", "public_candidate")),
    "shared_interaction": (("id", "name", "kind", "status", "visibility", "description"), ("source", "used_by")),
    "orchestration": (("id", "name", "status", "visibility", "description"), ("repo", "uses")),
    "connectors": (("id", "name", "service", "status", "visibility", "description"), ("organ", "lane")),
    "organs": (("id", "name", "kind", "status", "visibility", "description"), ("repo", "uses")),
    "sources": (("id", "name", "kind", "owner", "authority", "status", "visibility", "description"), ()),
    # An edge without a status is current; an edge not yet built says so.
    "relationships": (("id", "from", "to", "kind", "description"), ("status",)),
}

FABRIC_COLLECTIONS = {
    "tools": (("id", "name", "status", "visibility", "description"), ()),
    "skills": (("id", "name", "group", "status", "visibility", "description"), ()),
    "extensions": (("id", "name", "status", "visibility", "description"), ("package",)),
    "hooks": (("id", "name", "event", "enforced_by", "status", "visibility", "description"), ()),
    "workflows": (("id", "name", "status", "visibility", "description"), ()),
    "policies": (("id", "name", "enforced_by", "status", "visibility", "description"), ()),
}

# Fields whose values must resolve to a record id elsewhere in the catalog.
REFERENCE_FIELDS = {
    "surfaces": ("uses",),
    "shared_interaction": ("used_by",),
    "orchestration": ("uses",),
    "connectors": ("organ", "holds"),
    "organs": ("uses",),
    "relationships": ("from", "to"),
}

# Deliberately narrow: patterns that are never legitimate in House System text.
# Absolute home paths, email addresses and credential shapes. No generic
# "api key:" heuristic, which produces false positives in prose.
SAFETY_PATTERNS = (
    ("absolute home path", re.compile(r"/Users/[A-Za-z0-9_.-]+")),
    ("absolute Linux home path", re.compile(r"/home/[A-Za-z0-9_.-]+")),
    ("email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("OpenAI-style key", re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9]{16,}")),
    ("GitHub token", re.compile(r"\bgh[opsur]_[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{16,}")),
)


def load_catalog(path: Path | str = DEFAULT_CATALOG) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: catalog root must be a mapping")
    return data


def load_yaml(path: Path | str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def iter_records(catalog: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield (collection_path, record) for every record in the catalog."""
    for name, (fields, _extra) in LIST_COLLECTIONS.items():
        for record in catalog.get(name) or []:
            if isinstance(record, dict):
                yield name, record
    fabric = catalog.get("execution_fabric") or {}
    for name, (fields, _extra) in FABRIC_COLLECTIONS.items():
        for record in fabric.get(name) or []:
            if isinstance(record, dict):
                yield f"execution_fabric.{name}", record


def _schemas() -> dict[str, tuple[tuple[str, ...], tuple[str, ...]]]:
    schema = dict(LIST_COLLECTIONS)
    for name, spec in FABRIC_COLLECTIONS.items():
        schema[f"execution_fabric.{name}"] = spec
    return schema


def all_ids(catalog: dict[str, Any]) -> dict[str, str]:
    """id -> collection path. Raises on a duplicate id."""
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for collection, record in iter_records(catalog):
        rid = record.get("id")
        if not isinstance(rid, str) or not rid:
            continue
        if rid in seen:
            duplicates.append(f"duplicate id {rid!r} in {collection} (already in {seen[rid]})")
        else:
            seen[rid] = collection
    if duplicates:
        raise ValueError("; ".join(duplicates))
    return seen


def scan_text(text: str, origin: str) -> list[str]:
    findings = []
    for label, pattern in SAFETY_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(f"{origin}: {label} found: {match.group(0)!r}")
    return findings


def validate(catalog: dict[str, Any], catalog_text: str = "", atlas_path: Path | None = None) -> dict[str, list[str]]:
    """Return {'errors': [...], 'warnings': [...], 'notes': [...]}."""
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    if catalog.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    scope = catalog.get("scope")
    if not isinstance(scope, str) or len(scope.strip()) < 40:
        errors.append("scope must be a descriptive string of at least 40 characters")
    authority = catalog.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority mapping is required")
    else:
        if "local_relationships" not in authority:
            errors.append("authority.local_relationships is required")
        if "note" not in authority:
            errors.append("authority.note is required")

    # Structural checks.
    for collection, (required, extra) in _schemas().items():
        if collection.startswith("execution_fabric."):
            records = (catalog.get("execution_fabric") or {}).get(collection.split(".", 1)[1])
        else:
            records = catalog.get(collection)
        if records is None:
            errors.append(f"missing collection: {collection}")
            continue
        if not isinstance(records, list) or not records:
            errors.append(f"collection {collection} must be a non-empty list")
            continue
        for index, record in enumerate(records):
            where = f"{collection}[{index}]"
            if not isinstance(record, dict):
                errors.append(f"{where}: record must be a mapping")
                continue
            for field in required:
                value = record.get(field)
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"{where}: missing required field {field}")
            for field in record:
                if field not in required and field not in extra:
                    warnings.append(f"{where}: unknown field {field}")
            for field in ("status", "visibility"):
                if field in record and record[field] not in (STATUSES if field == "status" else VISIBILITIES):
                    errors.append(f"{where}: {field} {record[field]!r} is not one of {STATUSES if field == 'status' else VISIBILITIES}")
            if "public_candidate" in record and record.get("visibility") != "private":
                errors.append(f"{where}: public_candidate only applies to a private record")

    # Ids and references.
    try:
        ids = all_ids(catalog)
    except ValueError as exc:
        errors.append(str(exc))
        ids = {}
    for collection, record in iter_records(catalog):
        for field in REFERENCE_FIELDS.get(collection.split(".")[-1], ()):
            value = record.get(field)
            if value is None:
                continue
            targets = value if isinstance(value, list) else [value]
            for target in targets:
                if target not in ids:
                    errors.append(f"{collection}:{record.get('id', '?')}: {field} references unknown id {target!r}")

    # One authority per fact: no two source records may claim the same authority.
    authority_scopes: dict[str, str] = {}
    for record in catalog.get("sources") or []:
        if not isinstance(record, dict):
            continue
        claimed = record.get("authority")
        owner = record.get("owner")
        if isinstance(claimed, str) and claimed:
            if claimed in authority_scopes:
                errors.append(f"sources:{record.get('id')}: authority {claimed!r} already claimed by {authority_scopes[claimed]}")
            else:
                authority_scopes[claimed] = record.get("id", "?")
        if not isinstance(owner, str) or not owner.strip():
            errors.append(f"sources:{record.get('id')}: owner must name the writer")

    # Safety scan of the raw catalog file.
    for finding in scan_text(catalog_text or yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False), "catalog"):
        errors.append(finding)

    # External cross-check: project slugs must exist in the local relationship map.
    project_slugs = sorted({record["repo"] for _c, record in iter_records(catalog) if isinstance(record.get("repo"), str)})
    if atlas_path and Path(atlas_path).exists():
        try:
            atlas = read_atlas(Path(atlas_path))
        except AtlasError as exc:
            return {"errors": [*errors, str(exc)], "warnings": warnings, "notes": notes}
        known = set((atlas.get("projects") or {}).keys())
        for slug in project_slugs:
            if slug not in known:
                errors.append(f"repo {slug!r} is not a project in {Path(atlas_path).name}")
        catalog_projects = {
            (record.get("repo") or record.get("id"))
            for collection, record in iter_records(catalog)
            if collection == "organs"
        }
        missing = sorted(known - set(project_slugs) - {""})
        notes.append(f"atlas cross-check: {len(project_slugs)} catalog project slugs, {len(known)} atlas projects, {len(missing)} atlas-only ({', '.join(missing)})")
    else:
        warnings.append(f"atlas not found at {atlas_path}; skipped project-slug cross-check")

    notes.append(f"records: {len(ids)} ids across {len(_schemas())} collections")
    return {"errors": errors, "warnings": warnings, "notes": notes}


def render_system_map(catalog: dict[str, Any]) -> str:
    """Deterministic Markdown system map. No timestamps, no random ordering."""
    ids = all_ids(catalog)
    lines: list[str] = []
    add = lines.append

    add("# House System map")
    add("")
    add("> Generated from `catalog/catalog.yaml` by `tools/build_system_map.py`.")
    add("> Do not hand-edit. Run `make map` and commit the result.")
    add("")
    add("Relationships between child repositories are owned by `house/atlas.yaml`;")
    add("this map shows the catalog's layer inventory and the inter-layer edges the")
    add("catalog is allowed to hold. See `docs/architecture.md` for the layer model.")
    add("")

    counts: dict[str, dict[str, int]] = {}
    for collection, record in iter_records(catalog):
        bucket = counts.setdefault(collection, {"total": 0, STATUSES[0]: 0, STATUSES[1]: 0, STATUSES[2]: 0})
        bucket["total"] += 1
        bucket[record.get("status", "current")] = bucket.get(record.get("status", "current"), 0) + 1

    add("## Inventory")
    add("")
    add("| Layer | Records | Current | Experimental | Aspirational |")
    add("| --- | ---: | ---: | ---: | ---: |")
    for collection in list(LIST_COLLECTIONS) + [f"execution_fabric.{n}" for n in FABRIC_COLLECTIONS]:
        if collection not in counts:
            continue
        bucket = counts[collection]
        add(f"| {_label(collection)} | {bucket['total']} | {bucket.get('current', 0)} | {bucket.get('experimental', 0)} | {bucket.get('aspirational', 0)} |")
    add(f"| **Total** | **{sum(b['total'] for b in counts.values())}** | | | |")
    add("")

    add("## Layer stack")
    add("")
    add("```")
    add("  surfaces          apps, menu-bar panels, CLIs, this repo's map")
    add("  shared interaction one visual and Swift rule (design-system)")
    add("  orchestration     sessions, subagents, goals, control plane")
    add("  execution fabric  tools, skills, extensions, hooks, workflows, policies")
    add("  capabilities      connectors to external services + local organs")
    add("  sources           one owning record per fact, referenced not copied")
    add("  personal context  private day packet and identity, outside this repo")
    add("```")
    add("")

    for collection in list(LIST_COLLECTIONS) + [f"execution_fabric.{n}" for n in FABRIC_COLLECTIONS]:
        records = _records_for(catalog, collection)
        # Edges have no name or visibility; they get their own section below.
        if not records or collection == "relationships":
            continue
        add(f"## {_label(collection)}")
        add("")
        add("| Id | Name | Status | Visibility | Description |")
        add("| --- | --- | --- | --- | --- |")
        for record in records:
            add(
                "| `{id}` | {name} | {status} | {visibility} | {description} |".format(
                    id=record.get("id", ""),
                    name=_escape(record.get("name", "")),
                    status=_badge(record.get("status", "")),
                    visibility=record.get("visibility", ""),
                    description=_escape(record.get("description", "")),
                )
            )
        add("")

    edges = [r for r in (catalog.get("relationships") or []) if isinstance(r, dict)]
    if edges:
        add("## Inter-layer relationships")
        add("")
        add("```mermaid")
        add("flowchart LR")
        for edge in edges:
            arrow = "-->" if edge.get("status", "current") == "current" else "-.->"
            add(f"  {_mermaid(edge.get('from', ''))} {arrow}|{edge.get('kind', '')}| {_mermaid(edge.get('to', ''))}")
        add("```")
        add("")
        add("| Id | From | To | Kind | Description |")
        add("| --- | --- | --- | --- | --- |")
        for edge in edges:
            add(
                "| `{id}` | `{from_}` | `{to}` | {kind} | {description} |".format(
                    id=edge.get("id", ""),
                    from_=edge.get("from", ""),
                    to=edge.get("to", ""),
                    kind=edge.get("kind", "") + ("" if edge.get("status", "current") == "current" else f" ({edge['status']})"),
                    description=_escape(edge.get("description", "")),
                )
            )
        add("")

    fabric = catalog.get("execution_fabric") or {}
    if (fabric.get("policies") or []) and (fabric.get("hooks") or []):
        add("## Enforcement")
        add("")
        add("| Policy | Enforced by | Event |")
        add("| --- | --- | --- |")
        for policy in fabric["policies"]:
            enforcer = policy.get("enforced_by", "")
            events = sorted({h.get("event", "") for h in fabric["hooks"] if h.get("enforced_by") == enforcer})
            add(f"| {_escape(policy.get('name', ''))} | `{enforcer}` | {', '.join(events) or '-'} |")
        add("")

    add("## References")
    add("")
    for record in catalog.get("sources") or []:
        add(f"- **{_escape(record.get('name', ''))}** (`{record.get('id', '')}`) — owner: {_escape(record.get('owner', ''))}; authority: {_escape(record.get('authority', ''))}")
    add("")
    return "\n".join(lines)


def _records_for(catalog: dict[str, Any], collection: str) -> list[dict[str, Any]]:
    if collection.startswith("execution_fabric."):
        return (catalog.get("execution_fabric") or {}).get(collection.split(".", 1)[1]) or []
    return catalog.get(collection) or []


def _label(collection: str) -> str:
    return collection.replace("execution_fabric.", "execution fabric / ").replace("_", " ").title()


def _badge(status: str) -> str:
    return {"current": "current", "experimental": "experimental", "aspirational": "aspirational"}.get(status, status)


def _escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _mermaid(token: Any) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", str(token))
