# House System

House System is the architecture and presentation home for House: the family of
native Apple apps and shared organs that run on one design rule, one Swift rule,
and one local computing layer.

This repository exists so that the shape of House can be read in one place. It
describes the layers, how mature each one is, and where authority for every
fact lives. It is prose, not a product and not a registry of truth.

- Read the [system map](docs/system-map.md) to find the project graph.
- Read the [architecture](docs/architecture.md) for the layer model.
- Read the [glossary](docs/glossary.md) before using House terms loosely.

## What this repository is

- The canonical description of the House layers: surfaces, shared interaction,
  orchestration, the Pi execution fabric, connectors, organs and sources.
- The record of House conventions that are shared across apps, including direct
  distribution.

## What this repository is not

- It is not a monorepo. Every House product stays in its own repository and is
  built, tested and released there.
- It is not the relationship authority. Project-to-project relationships and
  each child repository's role are owned by `house/atlas.yaml`, which
  `code-atlas.py` renders into the code directory's `CLAUDE.md` and the vault
  code index. Portfolio
  purpose, tier and activity are owned by the code atlas. This repository
  references both and never restates them.
- It is not a source of truth for any product's state, tasks, decisions or
  identity. Those stay with their owning records.
- It holds no secrets, credentials, private identity content, client material or
  absolute machine paths. The scrub gate fails the build if the machine-checkable
  cases appear.

## Layout

| Path | What it holds |
| --- | --- |
| `docs/system-map.md` | Pointer to `house/atlas.yaml` and the views rendered from it |
| `docs/` | Vision, principles, architecture, personal context, trust, capabilities, distribution, glossary |
| `tools/house-usage.py` | Read-only usage counts for each House app |
| `tests/scrub.sh` | The scrub gate: no home paths, personal emails, key material or private tokens |
| `Makefile` | `check` |

## The layer model in one screen

```
  surfaces           apps, menu-bar panels, CLIs, the agent surface
  shared interaction the one visual rule and the one Swift rule
  orchestration      sessions, subagents, goals, the control plane
  execution fabric   tools, skills, extensions, hooks, workflows, policies
  capabilities       connectors to services and the local organs they use
  sources            one owning record per fact, referenced and not copied
  personal context   private identity and daily context, outside this repository
```

A surface is what a person touches. Shared interaction is what makes every
surface feel like the same product family. Orchestration decides who does the
work. The execution fabric is what can actually be run. Capabilities are how the
work reaches a service or a model. Sources are where a fact lives. Personal
context is the private layer that House serves and deliberately does not copy.

## Maturity

Every component the docs mention is `current` (in use), `experimental` (built,
not yet relied on), or `aspirational` (designed, not built). Maturity is a
statement, not a quality verdict, and it never authorises a release.

## Check

```
make check    # run the scrub gate (prints SCRUB_CLEAN) and the usage tool tests
```

## Usage counts

```
python3 tools/house-usage.py            # last 7 days, aligned table
python3 tools/house-usage.py --days 30  # a different window
python3 tools/house-usage.py --json     # rows as JSON
```

The tool reads each app's own store read-only and prints counts and dates, never
content. A row that says `no store` means the store was not found. Rows labelled
`all-time` or `no usage signal` are not windowed counts. It uses the Python
standard library only.

## Authority

| Fact | Owner |
| --- | --- |
| Project-to-project relationships, child roles | `house/atlas.yaml` |
| Portfolio purpose, tier, activity | the code atlas |
| Every visual value | design-system `tokens.json` |
| Swift concurrency, tests, platform floors | design-system `SWIFT.md` |
| A product's objective and state | that product's own status record |
| Open work | the project's canonical task store |
| Identity, preferences, direction | the private identity store, human-gated |

These docs describe the owners; they do not override any of them. This
repository keeps no project list, so it cannot drift from `house/atlas.yaml`.

## Retired

Dated 2026-10-17. House captures, makes recallable, and assists in the moment;
synthesis and decisions belong downstream in the vault and the agent runtime.

- `chief-of-staff` (the proactive card loop and its Quick Launch AI Chat face)
  and `ledger` (the commitments ledger) are retired. Both did synthesis. Their
  repositories are archived private on GitHub, and their relationships
  and Quick Launch code are removed.
- RTI keeps capture (recording, live transcript, screenshots, raw session
  archive to the vault), Live Notes and the in-meeting copilot. The rest of
  its in-app analysis is removed: discussion guide, findings ledger,
  end-of-session summary and generated titles, and saved-meeting outputs. The opt-in
  hand-off of the canonical transcript to the vault stays.

## Licence

All rights reserved. No licence is granted by its presence here. Third-party
components keep their own licences in their owning repositories.
