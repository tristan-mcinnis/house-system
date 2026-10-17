# House System

House System is the architecture and presentation home for House: the family of
native Apple apps and shared organs that run on one design rule, one Swift rule,
and one local computing layer.

This repository exists so that the shape of House can be read in one place. It
describes the layers, the components in each layer, how mature each one is, and
where authority for every fact lives. It is a catalogue and a map, not a product
and not a registry of truth.

- Read the [system map](docs/system-map.md) for the generated inventory.
- Read the [architecture](docs/architecture.md) for the layer model.
- Read the [glossary](docs/glossary.md) before using House terms loosely.

## What this repository is

- The canonical description of the House layers: surfaces, shared interaction,
  orchestration, the Pi execution fabric, connectors, organs and sources.
- The machine-readable catalogue at [`catalog/catalog.yaml`](catalog/catalog.yaml),
  validated and rendered by the tools in [`tools/`](tools).
- The record of House conventions that are shared across apps, including direct
  distribution.

## What this repository is not

- It is not a monorepo. Every House product stays in its own repository and is
  built, tested and released there.
- It is not the relationship authority. Project-to-project relationships and
  each child repository's role are owned by `house/atlas.yaml`. Portfolio
  purpose, tier and activity are owned by the code atlas. This repository
  references both and never restates them.
- It is not a source of truth for any product's state, tasks, decisions or
  identity. Those stay with their owning records.
- It holds no secrets, credentials, private identity content, client material or
  absolute machine paths. Validation fails the build if the machine-checkable
  cases appear.

## Layout

| Path | What it holds |
| --- | --- |
| `catalog/catalog.yaml` | The machine-readable inventory: records, status, visibility, references |
| `docs/system-map.md` | Generated human-readable map. Never hand-edited |
| `docs/` | Vision, principles, architecture, personal context, trust, capabilities, distribution, glossary, catalog schema |
| `tools/` | Deterministic validator, map builder and `house_status.py` (standard library plus PyYAML) |
| `tests/` | Unit tests for validation, safety scanning and map freshness |
| `Makefile` | `validate`, `map`, `test`, `check`, `status` |

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

## Status and visibility

Every catalog record carries two independent facts.

- **Status**: `current` (in use), `experimental` (built, not yet relied on), or
  `aspirational` (designed, not built).
- **Visibility**: `public` or `private`. Every record today is private. A record
  may also carry `public_candidate: true`, which states an intention only; it
  is not a decision and does not change exposure.

Status is a statement of maturity, not a quality verdict, and it never
authorises a release.

## Validate

```
make check    # validate the catalog, prove the map is current, run the tests
make map      # regenerate docs/system-map.md after a catalog change
make status   # Git state of every child in ../atlas.yaml; exit 1 if work exists only on this machine
```

`make status` marks a child with uncommitted files as `DIRTY`, never plain
`ok`. Dirty alone does not change the exit status.

The group file `../atlas.yaml` is outside this repository (the `house/` folder
is not a Git repository). Both tools take `--atlas PATH`, then the `HOUSE_ATLAS`
environment variable, then fall back to `../atlas.yaml`. On a fresh clone with
no parent file, `make validate` warns and skips the slug cross-check, and
`make status` prints one error line and exits 2. The tests read the committed
copy `tests/fixtures/atlas.yaml`, so `make check` passes anywhere. When a
catalog record names a new child, add its slug to the fixture.

`make check` is the gate. It fails on a missing field, an unknown status, a
duplicate id, a dangling reference, two records claiming the same authority, a
project slug that is not in `house/atlas.yaml`, or any absolute path, email
address or credential shape in the catalog.

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

The catalog describes these; it does not override any of them. The validator
cross-checks project slugs against `house/atlas.yaml` so the two cannot drift
apart silently.

## Retired

Dated 2026-10-17. House captures, makes recallable, and assists in the moment;
synthesis and decisions belong downstream in the vault and the agent runtime.

- `chief-of-staff` (the proactive card loop and its Quick Launch AI Chat face)
  and `ledger` (the commitments ledger) are retired. Both did synthesis. Their
  repositories are archived private on GitHub, and their catalog records,
  relationships and Quick Launch code are removed.
- RTI keeps capture (recording, live transcript, screenshots, raw session
  archive to the vault) and the in-meeting copilot. Its in-app analysis is
  removed: live notes, discussion guide, findings ledger, end-of-session
  summary and generated titles, and saved-meeting outputs. The opt-in
  hand-off of the canonical transcript to the vault stays.

## Licence

All rights reserved. No licence is granted by its presence here. Third-party
components keep their own licences in their owning repositories.
