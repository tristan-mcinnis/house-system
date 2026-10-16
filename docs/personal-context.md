# Personal context

House serves one person's work, so it depends on personal context. That context
is also the most sensitive material in the system. This document states what
personal context is, how it reaches a session, and the boundary this repository
holds.

## What personal context is

- **Identity**: who the person is, how they prefer to work, and what they are
  trying to move toward. Human-gated and edited deliberately, never inferred
  silently from a session.
- **Project truth**: the objective, state, tasks and decisions of each project,
  owned by that project's own records.
- **Working context**: the bounded set of facts a fresh agent request needs to
  be useful today: what is open, what is due, what changed.
- **Captures**: thoughts, screen context and meeting archives produced by the
  capture surfaces.

These are four different things with four different owners. Treating them as one
blob is how a system starts writing guesses into the record.

## How context reaches a session

A session does not read the personal store. It receives a bounded, generated
daily packet, supplied fresh at the start of each request. The packet is:

- **generated**, so it is never hand-edited;
- **read-only**, so nothing in a session writes back to it;
- **bounded**, so it drops rather than grows without limit;
- **per-request**, so it is not accumulated into session history.

Alongside it, deterministic hooks load the exact service lane a request needs,
so an ops task gets the right connector rather than a guessed one. Nothing about
this path is a memory write.

Session transcripts are an archive of what happened, under their own privacy
rules. They are evidence; they are not promoted to truth automatically, and a
session cache is never canonical identity, preference, decision, task or project
state.

## What this repository records

The catalog records *that* a personal context layer exists, which record owns
which kind of fact, and where the boundary is. It records categories only.

It does not record names, preferences, identity content, memory content,
transcripts, client material, or any file location inside the private store. The
validator rejects absolute paths, email addresses and credential shapes; the
repository contract rejects the rest.

## Boundary rules

1. Personal context lives in the private store, not in this repository.
2. A generated packet is a view, not a source.
3. Identity changes are deliberate and human-gated.
4. A session may read context to do its work; it may not silently rewrite the
   records that own the facts.
5. An artifact that leaves the private store is audited for personal-path and
   personal-content exposure first.

## Why the boundary is documented

Because a privacy claim is only checkable if the lanes are named. The catalog's
`connectors` table names every outbound lane and marks which are read-only or
draft-only, so "local by default" is a statement someone can verify rather than
a slogan. The `sources` table names who owns each kind of fact, so "one record,
one owner" is likewise checkable.
