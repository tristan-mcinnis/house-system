# Trust

House runs on a personal machine, holds personal material and acts on the
person's behalf. This document states what is trusted, what is not, and which
decisions are reserved to a human.

## Trust boundaries

**On the machine.** Inference, transcription, speech, screen capture and memory
are local by default. The local model service and the voice service are the
shared serving layer. A hosted service is a named exception, visible in
[capabilities](capabilities.md), never the quiet default.

**At the edge.** Every outbound lane is named and classified:

- Draft-only: work email and Slack. The lane can read, search and draft. It
  cannot send without an explicit instruction.
- Read-only by construction: personal mail, personal Google documents and file
  metadata. These lanes have no write path at all.
- Local: the model daemon, the voice service, the browser and phone agents, all
  against resources the person already controls.
- Hosted by request: search, transcription, social data. Used for a task, not as
  a background sync.

**In an artifact.** No credential, token, private identity content, client
material or absolute machine path belongs in a repository. Secrets live in the
Keychain or a permission-restricted file, never in source. This repository's
scrub gate (`make check`) mechanically rejects the machine-checkable cases.

## What is not trusted

- A generated view. It is disposable by definition; the record it derives from is
  the authority.
- A session cache. Useful for resuming one session, never a canonical store.
- A subagent report. Evidence for the parent, not acceptance.
- A skill description. It is a discovery hint, which is why the important lanes
  are loaded by deterministic hooks instead.
- A model's statement that work is done. Done is a command run and a result
  observed.

## Enforcement

Rules are enforced mechanically where a machine can decide, and by review where
it cannot.

| Rule | Enforced by |
| --- | --- |
| Destructive shell commands and protected-root searches | The shell guard, fail closed |
| One browser route per turn, and a private lane for private work | The browser route classifier |
| Chinese sources go to the Chinese-first lane | The search route classifier |
| Email and Slack stay draft-only | The ops hook and the lane's own CLI |
| No hand edits to a generated view | The code atlas generator, which rewrites its views |
| One owner per fact | The atlas, the repository contracts and review |
| No credential, client name or absolute path in this repository | The scrub gate (`make check`) |

Where a check aborts, the alternative is proposed. The same command is not
retried.

## Human gates

These wait for an explicit decision, and a plan is not a decision:

- Making any repository public.
- Signing, notarizing or publishing a release.
- Purchasing anything, including a developer membership.
- Sending or posting communication.
- Deleting, or taking any other irreversible action.

## Verification

Verification is a fresh pass, separate from the builder. It runs an executable
check against the artifact and records the exact command and its result. Static
review and executable verification are different jobs and are reported as such.
A claim without a recorded command is a claim, not evidence.

## Failure posture

Access is a capability, not a permission. A logged-in browser session or an
available credential grants reach, not authority to act. Where the system cannot
tell whether an action is permitted, it stops and asks rather than proceeding,
and it says what it could not check.
