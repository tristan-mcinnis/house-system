# House System repository contract

This repository is an independent child of the `house` group. It is the
architecture and presentation home for House. It owns description and shared
conventions; it owns no product, no task store and no product state.

## Local facts

- This repository is documentation only. No code, no registry, no generated files.
- Gate: `make check` runs the scrub gate (`tests/scrub.sh`). Run it before every
  commit. It fails on absolute home paths, personal email addresses, key
  material and the private tokens in the gitignored `.scrub-private`.
- The project graph is `../atlas.yaml`, rendered by `code-atlas.py` into the
  code directory's `CLAUDE.md` and the vault code index. `docs/system-map.md`
  says so and holds no inventory.

## Rules for this repository

1. **Do not duplicate authority.** `house/atlas.yaml` owns project-to-project
   relationships and child roles. The code atlas owns portfolio purpose, tier
   and activity. `design-system` owns visual values and the Swift rule. A
   product owns its own state. Reference the owning record; never restate it.
   Do not add a project list, catalog or registry here.
2. **Keep the docs descriptive.** They describe layers, maturity and exposure.
   They do not create work, change exposure, or claim that something is
   released.
3. **Never add private material.** No absolute machine paths, no email
   addresses, no credentials or tokens, no private identity content, no client
   names or client material, no secrets of any kind. `tests/scrub.sh` scans for
   the machine-checkable cases; the rest is a review responsibility.
4. **State maturity honestly.** Use `current`, `experimental` or `aspirational`.
   A component that is built but not relied on is `experimental`, not `current`.
5. **New shared interaction needs a design-system registration.** A component
   must exist in design-system's registry before the docs call it shared.
6. **No publishing from this repository beyond the repository itself.** It
   publishes no site and no release. Any change to its exposure follows a full
   history, licence, secret and path audit.
7. **Work and commit here, not in the group directory.** `house/` is not a Git
   repository and must stay that way.

## Layout

```
docs/                       vision, principles, architecture, capabilities, trust, and the rest
docs/system-map.md          pointer to house/atlas.yaml and the rendered views
tests/scrub.sh              the scrub gate
Makefile                    check
```

## House rules this repository follows

- `../design-system/DESIGN.md` is the visual rule for House apps. This
  repository has no UI, so it only inherits the documentation tone.
- `../design-system/SWIFT.md` is the Swift rule. Not applicable here (no Swift).
- Cross-project dependencies belong in `../atlas.yaml`; this repository does not
  restate them.
