# Distribution

House apps are distributed directly, outside any app store. This document is the
shared convention. Each app owns its own bundle identity, signing, notarization,
update key, appcast and release artifacts; this repository owns the convention
and the reasoning.

Nothing here is a release. The pipeline below becomes real only after the human
gates at the end of this document are cleared.

## What each app owns

- Its bundle identifier and version, stated in its own contract file.
- Its entitlements and hardened-runtime configuration.
- Its release scripts, appcast and update channel document.
- Its third-party notices and its own licence position.
- The decision to ship a build, which is a human decision.

House System owns the shared shape: the stages, their order, what each one
proves, and what must never be committed.

## The pipeline

1. **Build and test.** The app's own test suite passes at the commit being
   released, and the design lint is clean on touched files.
2. **Version.** A monotonically increasing marketing version and build number,
   recorded in the app's own changelog.
3. **Sign with a Developer ID Application certificate** and the hardened
   runtime enabled. The certificate lives in the login Keychain; it never enters
   the repository.
4. **Notarize** the signed artifact with the notary service and wait for
   acceptance. A rejected submission is a release stop, not a retry loop.
5. **Staple** the notarization ticket to the artifact so first launch works
   offline.
6. **Verify** the release artifact itself: signature, hardened runtime flag,
   notarization and stapling, on a clean path.
7. **Package** the distributable archive.
8. **Sign the update** with the EdDSA key for the app's updater. The private key
   lives in the Keychain; the public key is embedded in the app.
9. **Publish the appcast** over HTTPS, then the archive. The appcast names the
   version, the minimum system version, the archive URL, the archive length and
   the EdDSA signature.
10. **Confirm** that an unmodified installed copy updates to the new version and
    that the app launches after the update.

## Update policy

- **Channel**: a single stable channel per app unless a beta channel is
  deliberately created and documented.
- **Monotonic**: a client never downgrades silently. An update is only applied
  when the appcast offers a higher build number.
- **Minimum system version**: stated in the appcast; a client below it is not
  offered the update.
- **Rollback**: withdraw or pin the appcast entry. The updater serves the last
  good build. A rollback is a release action and is recorded like one.
- **No silent major migrations**: an update that changes user-visible behavior
  states it in the changelog.
- **Privacy**: the appcast carries no user identifier. Update checks do not
  report who is running what.

## Security rules

- Signing and update keys live in the Keychain. Never in a repository, an
  environment file that is committed, or a script argument in shell history.
- The appcast and archive are served over HTTPS only.
- A release artifact is signed before it is signed for update; the notarization
  ticket is stapled before packaging.
- The update key is per app and rotatable. Rotation is a documented operation
  with a plan for existing installs.
- Hardened runtime and the smallest entitlement set that works. An entitlement
  added for convenience is a review item.

## Licensing and notices

Each app ships with an accurate third-party notice file and its own licence
position. A dependency's licence is checked before it is added, not before a
release. An app whose components cannot be redistributed is not a distribution
candidate.

## Human gates

These cannot be completed by an agent, and none of them is a formality:

1. Join the developer program and pay for it.
2. Provision a Developer ID certificate and a notarization credential in the
   Keychain.
3. Decide that an app should be public at all, after a full history, licence,
   secret and personal-path audit.
4. Approve the first externally published release and its update feed.
5. Approve each later release.

## Pilot

Local Dictation is the first candidate for this pipeline because it is small,
self-contained, and entirely on device. Its public-readiness audit, release
scripts and dry-run path live in its own repository. This document defines what
that plumbing must satisfy; it does not contain the plumbing and it does not
claim the app is ready.

The `public_candidate` flag in the catalog marks the intention. It grants
nothing.
