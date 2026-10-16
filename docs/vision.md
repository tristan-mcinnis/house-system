# Vision

House is a private family of native Apple apps that run on the user's own
machine and share one visual rule, one code rule and one local computing layer.
The apps are not features of a platform; they are small tools with one verb
each, built to the same standard so that learning one means learning them all.

House System is the readable description of that family: what exists, how the
pieces fit, and where each fact lives.

## The problem

Working software tends to fail its user in one of two ways. Either it is too
generic to fit how the user actually works, or it is so bespoke that every new
tool repeats the same decisions about how to look, how to store data, and how to
run a model. The first produces friction; the second produces drift.

House takes a middle path. There is exactly one answer to each recurring
question, owned by exactly one place, and each product is small enough to stay
honest about what it does:

- One visual rule, owned by `design-system`, expressed as values in a token file
  and components in a registry.
- One code rule, owned by `design-system`, covering concurrency, tests and
  platform floors.
- One local serving layer, owned by `local-models`, so an app does not ship its
  own inference story. The named exceptions: Local Dictation runs its models in
  the app, a deliberate choice for latency (decided 2026-09-26; weights still
  live in the shared store), and `local-tts` is its own voice service on its own
  port, registered in the same store.
- One execution fabric, the agent runtime, so the same tools, policies and
  verification apply to every task.

## The stance

**Local first.** Dictation, completion, vision, speech and memory run on the
machine by default. A hosted service is a deliberate exception, named as such
in the catalog's connectors, never the quiet default. The largest exceptions
today: RTI's live meeting transcription goes to hosted Soniox and its assistant
to a hosted LLM, and every Pi agent, including the Chief of Staff, calls a
hosted model.

**Private by default.** Capture stays on the machine. Communication lanes are
draft-only until a person says send. Nothing is published, purchased or made
public without an explicit human decision.

**One fact, one owning record.** A derived view is never hand-edited, and a
session cache never becomes truth. The system prefers a single authoritative
record, referenced from everywhere else, over copies that drift.

**Maturity is stated, not implied.** Every component is `current`,
`experimental` or `aspirational`. Calling a built thing current when it is not
relied on is a lie the system should not tell itself.

**Small and composable.** Each app owns one verb. Shared behaviour moves into an
organ with a named owner, not into a copy.

## What House System is for

This repository answers four questions without reading eleven repositories:

1. What are the parts, and which layer does each belong to?
2. How mature is each part, and is it public or private?
3. Where does a given fact live, and who may change it?
4. What are the shared conventions an app must follow?

It does this with a hand-edited catalogue, a deterministic validator, and a
generated map. The map is disposable output; the catalogue is the input; the
owning records remain the authority.

## What success looks like

A person states a rough request and gets the result they intended with less
clarification, correction and chasing, while the quality bar holds. For the apps
that means one installable, signed, updatable tool per verb with no cloud
dependency. For the system overall it means a new app can be started by
following a rule instead of inventing one.

## Non-goals

- House System is not a platform, a framework, a monorepo or a marketplace.
- It does not ship code, own releases or run a service.
- It does not host a public site.
- It does not become the registry of record for any product's state.
- It does not enforce architecture by tooling beyond catalog validation. The
  rules are enforced where the work happens, and reviewed by a fresh reader.

## Maturity

House System starts `experimental` as a repository. The catalogue it holds is
descriptive and much of the family it describes is `current`. Treat the map as
accurate at its last commit, and the record it points to as the authority.
