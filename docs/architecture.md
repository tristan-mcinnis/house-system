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
Terminal surfaces are `recall`, `screenctx`, `ledger`, `rig` (agent seats and
their dashboard) and `cos` (the Chief of Staff organ's own CLI). The agent session is a surface too, and it is the one
that carries the execution fabric. Chief of Staff (experimental) is the one
organ that starts work on its own: see Initiative below. Its only face is the
pinned conversation in Quick Launch AI Chat. The separate ChiefOfStaff.app was
retired on 2026-09-26; Git keeps its history.

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
  collector, the recall CLI, the ledger, and the shared chat core owned by Quick
  Launch and consumed by RTI.

A capability has one owner. A second consumer references the organ; it does not
fork it. When two apps genuinely need different behaviour, that is a signal the
organ needs a seam, not a copy.

### Initiative

Every other flow in this document starts with a person: a hotkey, a meeting, a
launcher request. Initiative is the layer that starts work without one, and it is
owned by one organ, `chief-of-staff` (`cos`), so no app grows its own background
agent.

- **Trigger.** New records the ingest jobs already write (work mail, Slack) and
  changes in Ledger (a sent mail that closes a commitment, a commitment due soon). No
  model runs in the trigger.
- **Brain.** A model with no tools reads one event plus its project's status and
  open tasks, and proposes the smallest next step, or stays quiet.
- **Thread.** One HouseChatCore conversation holds every card and chat turn, so any
  House chat surface can show it.
- **Tiers.** Cards are ranked, not listed: decide, today, waiting, later, FYI and
  system. Only decide interrupts. Long projects are a strip, not cards.
- **Hands.** On Do it, only the vault's gated writers run (status note, task,
  task close, Outlook draft). Nothing is sent. Later hides a card until a time;
  No records a no.
- **Charter.** A plain-words policy in the vault (what to watch, who matters, what
  to ignore, style, quiet hours). Every model call reads it. More or Less on a
  card appends a learned rule, so a correction becomes a rule, not a repeat.
- **Clock.** A heartbeat adds a weekday morning card and a card 10 to 20 minutes
  before each meeting with someone. The morning card is built from 05:00 once
  morning-prep's block exists (its one ring waits for 07:00), else at or after
  07:45, and not after 11:00. It may say nothing.
- **Reviewer.** A second, stronger model checks every task close and reply draft;
  it passes, blocks, or raises the card to Decide. A reviewer failure never passes.
- **Trust.** Nothing acts before a tap, until Tristan says "Always do this" for one
  action type on one project. Replies and Decide cards never run by themselves;
  every run records Undo steps. The verdict log is the acceptance ledger.
- **Phone.** A send-only doorbell today; two-way replies need the Chief of
  Staff's own Telegram bot, because Ava reads the shared one.
- **Health.** One live card says when a background job, a login or an ingest turns
  red, with the fix.

Commitments belong to Ledger. The Chief of Staff is their face, not a second store.

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
sessions and the vault; general chat and the Chief of Staff live in Quick
Launch AI Chat. The two apps share the chat core, not the conversations.

**A launcher request.** The overlay collects a prompt and optional context, the
local model layer or a named hosted provider answers, and the answer detail
states which model and which sources were used.

**A proactive card.** Mail ingest writes a client reply to the vault. The
Chief of Staff trigger sees it on its next run, the brain proposes "log the
decision", the card lands in the thread under Today, and a notification (and the
phone doorbell) points at it. Tristan presses Do it; the status writer appends
the Log line; the verdict is recorded. If a later sent mail shows the work was
already done, the card closes on its own.

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
