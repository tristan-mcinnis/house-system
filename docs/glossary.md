# Glossary

House uses a small vocabulary. These definitions are the ones the House docs rely on. When a word here contradicts casual usage, this file
wins.

**Surface** — somewhere a person meets the system. A macOS app, a menu-bar
panel, a terminal CLI, or the agent session itself. A surface has one verb and
is owned by one repository.

**Shared interaction** — the parts every surface reuses: the visual rule, the
Swift rule, and the registered components and patterns built from them. Owned by
`design-system`.

**Orchestration** — who does the work and in what shape: the parent session, the
subagent roster, plan and goal lifecycles, the session checklist, the control
plane.

**Execution fabric** — what can actually be run: tools, skills, extensions,
hooks, workflows and policies. The fabric is the agent runtime, described by
capability rather than by file, because file paths are machine-specific.

**Tool** — one callable operation exposed to an agent, for example read, bash,
or a web search. A tool is the smallest unit of action.

**Skill** — a named procedure that loads on demand when its description matches
the task. A skill carries judgment and a documented method, not credentials.

**Extension** — a runtime module that registers tools, commands or hook handlers.
Extensions are where enforcement lives.

**Hook** — a point in the request lifecycle where an extension may act: before a
request starts, before a tool call, at session start, or at render time.

**Workflow** — a named, multi-step way of working with a lifecycle and a gate,
such as plan mode, goal mode, or the document work modes.

**Policy** — a rule that must hold across turns, expressed by an extension and
enforced mechanically where possible. Examples: destructive shell protection,
one browser route per turn, draft-only communication.

**Connector** — a lane to something outside the machine: a service, a hosted
model, a cloud host or a device. [Capabilities](capabilities.md) names every outbound lane so
privacy claims stay checkable.

**Organ** — a shared local capability with an owning repository: the design
system, the local model service, the voice service, the screen-context collector,
the recall CLI, the shared chat core.

**Source (of truth)** — the record that owns a fact. The README has a table of
them, each with exactly one owner.

**Personal context** — the private layer House serves: identity, preferences,
direction, and the daily context handed to an agent. It lives outside this
repository and is never mirrored here. See [personal-context](personal-context.md).

**Atlas** — `house/atlas.yaml`, the hand-edited project and relationship map
for the house group. The code atlas generator renders it into the code
directory's `CLAUDE.md` and the vault code index. Those rendered views are
disposable output.

**Status** — `current`, `experimental` or `aspirational`. A statement of
maturity, not quality and not release.

**Visibility** — `public` or `private`, describing current exposure. All House
records are private today. `public_candidate: true` states an intention only.

**Atlas** — `house/atlas.yaml`, the local relationship map that owns the
project-to-project graph and each child repository's role. The code atlas above
it owns portfolio purpose, tier and activity.

**Organ vs surface** — an organ is used; a surface is met. Quick Launch is a
surface; `local-models` is an organ. RTI's shared chat core is a library organ
owned by Quick Launch.

**Face** — a surface whose job is to show and steer an organ it does not own.
Memory is the face of `screenctx` and `recall`; the Local Models menu bar is the face of the
`local-models` daemon. A face reads the organ's state and acts only through the
organ's own commands.

**Capture vs remember** — capture records something for later sorting: the
screen, automatically (`screenctx`), or one typed thought into the memory repositorytriage queue (`recall capture`). Remember has one meaning: keep a durable fact,
through `memory-remember.py` in the memory repository. Which tool holds what:

| Tool | Holds | How it gets there |
| --- | --- | --- |
| `screenctx` | Screen text and stills | The one screen-history collector; Memory switches it on and off |
| `recall capture` | One thought in the the memory repository triage queue | Typed, or sent from Memory or Quick Launch (`recall remember` still works as a hidden alias) |
| `memory-remember.py` | One durable fact in the memory repository | A deliberate write through the memory repository's own CLI |
| RTI | Meeting transcript and audio | Recorded, archived to the vault on stop |

Quick Launch no longer has a screen-history collector of its own (retired
2026-09-26); screen history means `screenctx`.

**Seat** — a `rig` address, `role@project`: one tmux session running one Pi
agent, with its state in a sidecar file the rig dashboard reads.
