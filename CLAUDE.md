# House System repository contract

This repository is an independent child of the `house` group. It is the
architecture and presentation home for House. It owns description and shared
conventions; it owns no product, no task store and no product state.

## Local facts

- Language and tooling: Python 3 standard library plus PyYAML. No other
  dependency, no network access, no writes outside this repository.
- Gate: `make check` (validate the catalog, prove the generated map is current,
  run the unit tests). Run it before every commit.
- `docs/system-map.md` is generated from `catalog/catalog.yaml` by
  `tools/build_system_map.py`. Never hand-edit it; run `make map`.
- `catalog/catalog.yaml` is hand-edited and is the only source of the map.

## Rules for this repository

1. **Do not duplicate authority.** `house/atlas.yaml` owns project-to-project
   relationships and child roles. The code atlas owns portfolio purpose, tier
   and activity. `design-system` owns visual values and the Swift rule. A
   product owns its own state. Reference the owning record; never restate it.
2. **Keep the catalogue descriptive.** A record describes a component's layer,
   maturity and exposure. It does not create work, change exposure, or claim
   that something is released.
3. **Never add private material.** No absolute machine paths, no email addresses,
   no credentials or tokens, no private identity content, no client names or
   client material, no secrets of any kind. `tools/catalog_lib.py` scans for the
   machine-checkable cases; the rest is a review responsibility.
4. **State maturity honestly.** Use `current`, `experimental` or `aspirational`.
   A component that is built but not relied on is `experimental`, not `current`.
5. **New shared interaction needs a design-system registration.** A component
   added to `shared_interaction` must exist in design-system's registry first.
6. **No publishing from this repository.** This repository is private and
   stays private unless a deliberate human decision changes that, after a full
   history, licence, secret and path audit. It publishes no site and no release.
7. **Work and commit here, not in the group directory.** `house/` is not a Git
   repository and must stay that way.

## Layout

```
catalog/catalog.yaml        machine-readable inventory (hand-edited)
docs/                       vision, principles, architecture, and the rest
docs/system-map.md          generated view (never hand-edited)
tools/catalog_lib.py        shared load, validate and render logic
tools/validate_catalog.py   validator CLI
tools/build_system_map.py   map builder CLI
tools/house_status.py       read-only Git state of every child (make status)
tests/                      unit tests
tests/fixtures/atlas.yaml   committed copy of the group atlas project list (tests use it, never the live parent)
Makefile                    validate, map, test, check, status
```

## House rules this repository follows

- `../design-system/DESIGN.md` is the visual rule for House apps. This
  repository has no UI, so it only inherits the documentation tone.
- `../design-system/SWIFT.md` is the Swift rule. Not applicable here (no Swift).
- Cross-project dependencies belong in `../atlas.yaml`; this repository's
  catalog cross-checks against that file rather than restating it.
