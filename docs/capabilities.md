# Capabilities

A capability is what House can do, and how it reaches the thing that does it:
an organ on the machine or a named connector. This document is the human
summary. The machine list, with ids, status and exposure, is the catalog's
`connectors` and `organs` tables.

Status uses the catalog's meaning: `current` is relied on, `experimental` is
built but not yet relied on, `aspirational` is designed but not built.

## Capture

- **Dictation** (`current`): hold a key, speak, release, and the text lands at
  the cursor. Transcription and optional cleanup run on device inside the app
  (its weights sit in the shared model store, but the daemon does no dictation
  work), with a recovery detail for retained audio and text versions.
- **Screen context** (`current`): accessibility-first text capture plus
  frame-on-change stills, enriched locally and stored for query. `screenctx` is
  the one screen-history collector.
- **Meeting capture** (`current`): system and microphone audio recorded,
  transcribed in real time, and archived; the recorder can answer questions
  against the session.
- **Quick capture** (`current`): save a thought in seconds from the Memory menu
  bar or from Quick Launch's Capture to Memory action. Both hand the text to
  `recall capture`, which writes into the memory repository's triage queue.

## Local intelligence

- **Text and chat** (`current`): the shared local serving layer answers launcher
  and copilot requests, with an answer detail naming the model and sources used.
- **Completion** (`experimental`): a menu-bar app inserts accepted ghost text
  streamed from the local model daemon; its in-process engine is a legacy
  fallback.
- **Vision** (`current`): local image analysis, OCR and schema-validated JSON
  for screenshots and documents.
- **Speech** (`current`): an always-on localhost voice service synthesizes audio
  from text for reading and for audiobook assembly.

## Memory

- **Collector** (`current`): the screen-context store, captured and enriched
  locally.
- **Recall** (`current`): a CLI that captures thoughts into the memory repository and
  searches it with the open tasks, also reachable from the launcher and the
  Memory panel. It reads no screen data.
- **Ledger** (`experimental`): a commitments ledger with a disposable index
  over the file store, in shadow trial.

## Work surfaces

- **Launcher and AI overlay** (`current`): keyboard-first actions, search, and
  an instant AI answer surface.
- **Copilot** (`current`): meeting-grounded answers in a window that stays out
  of other apps' captures. General chat is Quick Launch AI Chat.
- **Usage meter** (`current`): every metered hosted AI source on one
  percent-used axis.
- **Local model panel** (`current`): the Local Models menu bar shows which local
  models are warm and loads or unloads them. It is the daemon's face; Usage is
  the hosted side.
- **Chief of Staff** (`experimental`): proposal cards (Do it, Edit, Later, No)
  from new mail, Slack, Ledger and the calendar, shown in Quick Launch AI Chat's
  pinned conversation. Nothing acts before a tap unless Tristan chose "Always
  do this" for that action on that project.
- **Agent seats** (`experimental`): `rig` runs one Pi agent per tmux seat
  (`role@project`) with one shared dashboard that also fits a phone, plus
  snapshot and restore.

## Services and data

- **Work mail** (`current`, draft-only): read, search and draft.
- **Personal mail** (`current`, read-only): search and read, no write path.
- **Personal documents** (`current`, read-only): documents, sheets, slides and
  file metadata.
- **Team chat** (`current`, draft-only): read, search and draft.
- **Calendar** (`current`): agenda, free slots, holds, invitations and responses.
- **Resource planning** (`current`): availability, allocations and time off.
- **Files** (`current`): search, download, read, upload, move and rename.
- **Repository hosting** (`current`): private repository creation and push.

## Search and external data

- **Global web search** (`current`): one tool over an ordered provider chain that
  reports which provider served.
- **Chinese web search** (`current`): a Chinese-first index for local sources.
- **Images** (`current`): search and download by theme from social and general
  sources.
- **Public social and marketplace data** (`current`): posts, listings and venue
  details.

## Devices and remote

- **Interactive browser** (`current`): automation of the person's own logged-in
  browser session.
- **Private local browser execution** (`current`): a bounded, exact-label
  executor against an already-open window, with no navigation and no free-form
  page read, for work that must not leave the machine.
- **Phone** (`current`): a real iPhone driven for apps that have no other route.
- **Remote workspace** (`current`): a bounded job run on a private host with
  verified artifact retrieval.

## Research and delivery

- **Research operations** (`current`): briefs, proposals, screeners, discussion
  guides, costings and synthesis.
- **Deliverables** (`current`): deck and document pipelines, rendering, audit
  and formatting.
- **Transcripts** (`current`): transcription, speaker recovery, QA, formatting
  and research-grade translation.
- **Knowledge and writing** (`current`): case studies, artifact management, and
  a deterministic prose-quality gate.

## Not yet built

- **Shared release pipeline** (`aspirational`): a House-wide convention for
  signed, notarized direct distribution. Designed in
  [distribution](distribution.md); each app applies it locally.
- **iOS surfaces** (`aspirational`): the rules exist; no iOS app has shipped.
