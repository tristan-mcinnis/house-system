# The catalog

`catalog/catalog.yaml` is the machine-readable inventory of House components,
their layers, maturity and exposure. `docs/system-map.md` is generated from it.
`tools/validate_catalog.py` gates it.

## Scope

The catalog is descriptive. It answers: what exists, which layer it belongs to,
how mature it is, how exposed it is, and which other records it depends on.

It explicitly does **not** own:

- project-to-project relationships or a child repository's role, which
  `house/atlas.yaml` owns;
- portfolio purpose, tier or activity, which the code atlas owns;
- product state, tasks, decisions or identity, which their own records own;
- permission to release, publish or change exposure.

A record is a statement about a component, not a decision about it. Adding a
record changes the map; it changes nothing in the world.

## Shape

Top-level keys:

| Key | Meaning |
| --- | --- |
| `schema_version` | Catalog format version. Currently `1` |
| `catalog` | Repository name |
| `scope` | Plain-language statement of what the catalog covers |
| `authority` | Pointers to the files that own facts the catalog references |
| `surfaces` | Person-facing entry points |
| `shared_interaction` | Rules and registered components |
| `orchestration` | Sessions, roles, goals, control plane |
| `execution_fabric` | Tools, skills, extensions, hooks, workflows, policies |
| `connectors` | Outbound lanes to services, hosts and devices |
| `organs` | Shared local capabilities with owning repositories |
| `sources` | Sources of truth, each with one owner and one authority |
| `relationships` | Inter-layer edges the atlas does not model |

## Record fields

Every record has `id`, `name`, `status`, `visibility` and `description`. Records
also carry the fields their collection requires, such as `kind` for a surface,
`repo` for a component in a child repository, and `enforced_by` for a hook or a
policy.

- `id` is globally unique and stable. Use the layer prefix (`sfc-`, `si-`, `org-`,
  `conn-`, `src-`, `rel-`, `xd-`).
- `status` is `current`, `experimental` or `aspirational`. A relationship
  may omit it (it is then current); an edge that is not built yet says
  `aspirational`, and the map draws it dashed.
- `visibility` is `public` or `private`. Every record is private today.
  `public_candidate: true` is allowed on a private record and states an
  intention only.
- `repo` names a project slug that must exist in `house/atlas.yaml`.
- `uses`, `used_by`, `organ`, `from`, `to` are references. Every target must be
  an id that exists in the catalog.

## What the catalog must never contain

- Absolute machine paths, including home directories.
- Email addresses, credentials or tokens of any kind.
- Private identity content, personal memory content or session transcripts.
- Client names or client material.
- A restatement of a fact owned by another record.

The validator fails on the machine-checkable cases in the first two lines. The
rest is enforced by review and stated in the repository contract.

## Adding a record

1. Decide the layer. If the component is a person-facing entry point it is a
   surface; if it is used rather than met, it is an organ or a capability.
2. Give it an id with the layer prefix.
3. State status honestly. Built but not relied on is `experimental`.
4. Reference the owning records rather than copying their content.
5. If it is a shared component, register it in `design-system` first.
6. Run `make check`, then `make map` if validation passes, then commit both.

## The relationship split

Two files describe relationships and they must not overlap.

- `house/atlas.yaml` (local authority): which child repositories exist, what
  role each plays, and which of them build on which.
- This catalog's `relationships` list: inter-layer edges the atlas does not
  model, such as a surface owning a shared library organ, a policy gating a
  connector, or a hook reading a generated view.

When an edge belongs in the atlas, put it in the atlas. The catalog's validator
cross-checks project slugs against the atlas, so a slug that drifts apart is a
build failure rather than a silent divergence.

## Validation rules

- schema version is `1`; scope and authority are present
- every collection is present and populated
- every record has its required fields
- `status` and `visibility` are from their enums
- ids are globally unique
- every reference resolves
- no two sources claim the same authority
- every `repo` slug exists in `house/atlas.yaml`
- no absolute home path, email address or credential shape in the file

The generated map is additionally checked for freshness and re-scanned for the
same unsafe text before it is written.
