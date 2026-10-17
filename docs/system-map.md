# System map

The map is `house/atlas.yaml`. It lists every House project, its role, and which
projects it builds on. It is hand-edited, and it is the only place those
relationships live.

`code-atlas.py` renders it into the code directory's `CLAUDE.md` and into the
vault code index, next to each project's purpose, tier and activity. Those
rendered views are disposable. Edit the atlas, then re-render. Portfolio purpose
and tier are owned by `code-atlas.yaml` one level above.

This repository keeps no second graph. For the reasoning behind the layers, see
[architecture](architecture.md). For the outbound lanes, see
[capabilities](capabilities.md).

```
  surfaces           apps, menu-bar panels, CLIs, the agent surface
  shared interaction one visual rule and one Swift rule (design-system)
  orchestration      sessions, subagents, goals, the control plane
  execution fabric   tools, skills, extensions, hooks, workflows, policies
  capabilities       connectors to external services and local organs
  sources            one owning record per fact, referenced not copied
  personal context   private identity and daily context, outside this repo
```
