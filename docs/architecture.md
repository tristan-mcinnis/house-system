# Architecture

House is a stack of small layers with one owner each. This document states what
each layer is responsible for, what it is not, and how work flows through it.
The [system map](system-map.md) is the generated inventory; this document is the
reasoning behind it.

## Layers

### Surfaces

A surface is where a person meets House: a macOS app with one verb, a menu-bar
panel, a terminal CLI, or the agent session. Surfaces are owned by their own
repositories and released independently.

The apps today are Quick Launch (launcher and AI overlay), RTI (meeting recorder
and copilot), Local Dictation (push-to-talk dictation), Cotype (menu-bar
completion), Memory (memory capture and search), Usage (quota of hosted metered
AI), and Local Models (which local models are warm; the daemon's face).
Terminal surfaces are `recall`, `screenctx` and `rig` (agent seats and their
dashboard). The agent session is a surface too, and it is the one that carries
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
parallel store. Two things show running agents today: `rig`'s dashboard, a
tmux session outside every Pi session that lists the seats (`role@project`),
and the older in-Pi `/dash` control plane, which is no longer grown and retires once
rig covers it.

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

- Connectors are outbound lanes. Every one is named in the catalog so a privacy
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

Every fact has exactly one owning record. The catalog's sources table lists them
with an owner and a one-line authority statement. The important ones:

- Project relationships: `house/atlas.yaml`, hand-edited.
- Portfolio purpose, tier and activity: the code atlas, above the group.
- Visual values: `design-system` tokens.
- The Swift rule: `design-system` `SWIFT.md`.
- A product's objective and state: that product's own status record.
- Open work: the project's canonical task store.
- Decisions: the owning decision record.
- Identity: the private identity store, human-gated and never mirrored here.

The catalog references these and never restates them. Validation cross-checks
project slugs against the atlas, so a rename that lands in one place and not the
other fails the gate.

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
are regenerated from their source, not edited. If the change alters the catalog,
the catalog is edited, `make check` runs, and the map is regenerated and
committed.

## Boundaries

| Boundary | Meaning |
| --- | --- |
| Repository | Each product builds, tests and releases in its own repository |
| Authority | One owning record per fact; derived views are disposable |
| Machine | Local by default; every outbound lane is named in the catalog |
| Human | Publishing, spending, signing, sending and exposure changes are gated |
| This repository | Describes and validates; ships nothing and owns no product state |

## Extension points

A new app follows the same path: state its floor and link the two rules in its
own contract file, register any new shared component in `design-system` first,
use the local serving layer rather than a bespoke model path, and add a catalog
record with honest status. Nothing about the family's shape changes when a new
member joins; the map just gains a row.
