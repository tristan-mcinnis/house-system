# Architecture

House is a stack of small layers with one owner each. This document states what
each layer is responsible for, what it is not, and how work flows through it.
The [system map](system-map.md) says where the project graph lives; this document
is the reasoning behind it.

## Layers

### Surfaces

A surface is where a person meets House: a macOS app with one verb, a menu-bar
panel, a terminal CLI, or the agent session. Surfaces are owned by their own
repositories and released independently.

The apps today are Quick Launch (launcher and AI overlay), RTI (meeting recorder
and copilot), Local Dictation (push-to-talk dictation), Cotype (menu-bar
completion, parked since 2026-10-18), Usage (quota of hosted metered AI), and
Local Models (which local models are warm; the daemon's face). The terminal
surface is `recall`. The agent session is a surface too, and it is the one that carries
the execution fabric.

A surface owns its own permissions, onboarding, persistence and bundle identity.
It does not own a shared capability and it does not own a rule.

### Shared interaction

Two rules and one registry, all owned by `design-system`:

- The visual rule (`DESIGN.md`): monochrome warm neutrals, one status dot as the
  only chroma, one radius, spacing and type scale, and one glass treatment for
  floating panels.
- The Swift rule (`SWIFT.md`): I/O services are actors, UI state is main-actor,
  new concurrency is structured, new test targets use Swift Testing, and the
  deployment target beats any advice.
- The component registry (`components.json`): every shared surface is registered
  and render-proven before it ships.

Values live in `tokens.json`; generators emit the Swift and Rust files that apps
consume. An app commits generated output and never retypes a value. The design
lint refuses a repository that gains a hard-coded radius, colour or size.

### Orchestration

Orchestration decides who does the work. The parent session owns decomposition,
decision, integration and the final answer. It chooses the smallest workflow
that fits and delegates within a fixed roster of roles, each with its own tool
allowlist. A child works on one assignment and its report is evidence for the
parent, not acceptance.

Plan mode, goal mode and the session checklist are orchestration lifecycle
tools. A goal binds to an existing canonical task record; it never creates a
parallel store. The in-Pi `/dash` control plane shows running agents. (`rig`,
its planned replacement, was retired unused on 2026-10-21.)

### Execution fabric

The fabric is what can be run. It has six kinds of member: tools, skills,
extensions, hooks, workflows and policies. It is described by capability rather
than by file path, because paths are machine-specific.

Extensions are where enforcement lives. A hook point lets an extension act in
the lifecycle: load fresh context before a request, gate a tool call, decide a
route, render a status footer. Policies are the rules those hooks enforce:
destructive shell protection, one browser route per turn, search lane by script,
draft-only communication, one authority per fact, no silent publish.

The fabric is not versioned in this repository. This repository documents its
shape and current membership; the runtime owns the implementation.

### Capabilities

A capability is how House reaches something: a connector to a service, or an
organ on the machine.

- Connectors are outbound lanes. Every one is named in [capabilities](capabilities.md) so a privacy
  claim stays checkable, including the lanes an app opens itself (`in-app`):
  RTI's hosted transcription and assistant, Quick Launch's hosted providers,
  Usage's quota reads, and the hosted models every Pi call reaches. Several are
  read-only by construction (personal mail, personal Google documents, Usage),
  two are draft-only (work mail, Slack), and a few stay on the machine (the
  local model daemon, the voice service).
- Organs are shared local capabilities with an owning repository: the design
  system, the local model service, the voice service, the screen-context
  collector, the recall CLI, and the shared chat core owned by Quick
  Launch and consumed by RTI.

A capability has one owner. A second consumer references the organ; it does not
fork it. When two apps genuinely need different behaviour, that is a signal the
organ needs a seam, not a copy.

### Sources

Every fact has exactly one owning record. The important ones:

- Project relationships: `house/atlas.yaml`, hand-edited.
- Portfolio purpose, tier and activity: the code atlas, above the group.
- Visual values: `design-system` tokens.
- The Swift rule: `design-system` `SWIFT.md`.
- A product's objective and state: that product's own status record.
- Open work: the project's canonical task store.
- Decisions: the owning decision record.
- Identity: the private identity store, human-gated and never mirrored here.

This repository references these and never restates them. It keeps no project
list of its own, so a rename lands in `house/atlas.yaml` once.

### Personal context

Personal context is the private layer House serves: identity, preferences,
direction, and the bounded daily context a fresh agent request receives. It
lives outside this repository. This repository states the boundary and copies
none of the content. See [personal-context](personal-context.md).

## How work flows

**Dictation.** A hotkey press captures audio, Local Dictation transcribes it
with its own in-process models (the shared layer only stores their weights),
and the text lands at the cursor. Audio and text stay on the machine; the
recovery detail lets the user replay and re-run it.

**A meeting.** The recorder captures the session, transcription runs, the result
is archived to the private knowledge store, and the recorder's copilot answers
questions against the same sources. The archive record owns the outcome. RTI's
chats, including a standalone one with no recording, stay grounded in its
sessions and the vault; general chat lives in Quick Launch AI Chat. The two apps share the chat core, not the conversations.

**A launcher request.** The overlay collects a prompt and optional context, the
local model layer or a named hosted provider answers, and the answer detail
states which model and which sources were used.

**A system change.** A change lands in the owning repository. Generated files
are regenerated from their source, not edited. A change to which project builds
on which goes into `house/atlas.yaml`, and the code atlas generator re-renders
the views. A change to the reasoning goes into these docs, and `make check` runs
the scrub gate.

## Boundaries

| Boundary | Meaning |
| --- | --- |
| Repository | Each product builds, tests and releases in its own repository |
| Authority | One owning record per fact; derived views are disposable |
| Machine | Local by default; every outbound lane is named in capabilities |
| Human | Publishing, spending, signing, sending and exposure changes are gated |
| This repository | Describes; ships nothing and owns no product state |

## Extension points

A new app follows the same path: state its floor and link the two rules in its
own contract file, register any new shared component in `design-system` first,
use the local serving layer rather than a bespoke model path, and add a project
entry to `house/atlas.yaml`. Nothing about the family's shape changes when a new
member joins; the atlas just gains an entry.

## Edges the atlas does not model

`house/atlas.yaml` holds project-to-project `builds_on` edges. These facts cut
across layers and are not project edges, so they live here.

- **Ownership of the chat core.** HouseChatCore is its own package in
  `house-chat-core`, extracted from Quick Launch. Quick Launch and RTI both build
  it. RTI keeps its own sources and tests.
- **Local Dictation and the Swift rule.** Local Dictation is a Rust app, so it
  follows the design rule and its own crate conventions, not the Swift rule.
- **Local Dictation and the model store.** Its weights live in the shared
  model store, but its models run in the app, not through the daemon. Daemon
  transcription is a later phase.
- **Cotype and the daemon.** Completions stream from the daemon-managed
  `llama-server` (gemma-it). The daemon owns the weights and their load and
  unload. The in-process engine is an opt-in legacy fallback.
- **Goals and tasks.** A bound goal names an existing canonical task record. It
  never creates a parallel store.
- **Day packet.** A hook reads the generated packet into each request and writes
  nothing back.
- **Route policies.** The browser policy decides whether the interactive lane may
  be used this turn. Chinese-script queries go to the Chinese-first search lane.
- **Terminal surfaces.** CLIs express the design rule as text discipline.

## Execution fabric membership

Hooks: day packet loading, ops-skill triggering for mail, calendar, Slack and
files, browser and search route classification, the destructive-shell guard,
document work mode, the effort budget, the status footer and session titles.
Workflows: plan mode, goal mode with its cooperative bridge, document modes,
maker-checker, quick images, and prewalk (`experimental`: a strong model plans
and lands the first edit, a cheaper one continues). Tool, skill and extension
inventories are owned by the runtime that loads them and change too often to
list here. Orchestration also includes interactive subagents in dedicated tmux
panes and a session checklist that is never a canonical task store.
