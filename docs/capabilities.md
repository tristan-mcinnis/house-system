# Capabilities

A capability is what House can do, and how it reaches the thing that does it:
an organ on the machine or a named connector. This document is the human list,
and the only list. Which repository provides each organ is in `house/atlas.yaml`.

Status words: `current` is relied on, `experimental` is built but not yet
relied on, `aspirational` is designed but not built.

## Capture

- **Dictation** (`current`): hold a key, speak, release, and the text lands at
  the cursor. Transcription and optional cleanup run on device inside the app
  (its weights sit in the shared model store, but the daemon does no dictation
  work), with a recovery detail for retained audio and text versions.
- **Screen context** (`retired` 2026-10-18): House keeps no screen history.
  `screenctx` was sunset unused; a screenshot reaches a chat only when asked for.
- **Meeting capture** (`current`): system and microphone audio recorded,
  transcribed in real time, and archived; the recorder can answer questions
  against the session.
- **Quick capture** (`current`): save a thought in seconds from Quick Launch's
  Capture to Memory action. It hands the text to `recall capture`, which writes into the memory repository's triage queue.

## Local intelligence

- **Text and chat** (`current`): the shared local serving layer answers launcher
  and copilot requests, with an answer detail naming the model and sources used.
- **Completion** (`experimental`): a menu-bar app inserts accepted ghost text
  streamed from the local model daemon; its in-process engine is a legacy
  fallback.
- **Vision** (`current`): local image analysis, OCR and schema-validated JSON
  for screenshots and documents.
- **Speech** (`retired` 2026-10-18): the localhost voice service (`local-tts`)
  was sunset unused. House synthesizes no audio today.

## Memory

- **Recall** (`current`): a CLI that captures thoughts into the memory repository and
  searches it with the open tasks, also reachable from the launcher. It reads no screen data.

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

## Lanes that leave the machine

These are the named exceptions to local first. Anything not listed here stays on
the machine.

- **RTI**: live audio for both legs goes to hosted Soniox by default. Retained
  audio goes to Soniox's file API for the transcript upgrade. Assistant turns go
  to the chosen LLM provider. OCR stays on the Mac.
- **Quick Launch**: an answer goes to a hosted provider only when the chosen
  model is hosted. The answer detail names the destination. Keys live in the
  macOS Keychain.
- **Usage**: reads quota and balance from each provider. It sends no prompt and
  no content. Antigravity is read through its local CLI.
- **Pi**: every agent call reaches a hosted model.
- **Notices**: Telegram is send-only, to the owner's phone through the Mac's
  notifier. Two-way replies are not built.
- **Hosted by request**: web search, social data, transcription and the
  repository host (private by default) run per task, never as a background sync.

## Not yet built

- **Shared release pipeline** (`aspirational`): a House-wide convention for
  signed, notarized direct distribution. Designed in
  [distribution](distribution.md); each app applies it locally.
- **iOS surfaces** (`aspirational`): the rules exist; no iOS app has shipped.
