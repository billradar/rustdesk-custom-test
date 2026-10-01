# RustDesk upstream automation report — 2026-10-01

Status: stable automatic build/test-prerelease path PASS; multi-generation compatibility, dedup and failure blocking
verified in Actions; acceptance PENDING an actual scheduled event. Entire Phase 3 is NOT yet accepted.

## Verified Stable pipeline

Official stable 1.4.9 SHA `6c578292e8ebbbec708b76986ba8c4bc7c509747`.
Maintenance commit `2a126a2f3e3776dd9a3f12750cad47ea2c24cc42`.
[Run 36819181305](https://github.com/billradar/rustdesk-custom-test/actions/runs/36819181305):
preflight/Rust, Bridge/Flutter analyze, Standard/SOS Windows AMD64 full builds and final
paired provenance/checksum/architecture gates all PASS.

[Standard prerelease](https://github.com/billradar/rustdesk-custom-test/releases/tag/v1.4.9-custom-test.1)
[ SOS prerelease](https://github.com/billradar/rustdesk-custom-test/releases/tag/v1.4.9-sos-test.1)
Both contain client ZIP, build-info.json and SHA256SUMS. Both are prerelease=true, draft=false.
No asset, manifest, checksum or release note was modified by the generation migration.

## Patch generation architecture

`patchsets/v1` contains the six original patches moved without changing a byte; integrity
metadata freezes canonical hashes. Both known historical exact upstream SHAs map to v1.
`patchsets/v2` implements the same design contract on the new API generation. It retains
Common then optional SOS layering, official gitlinks and only small source/UI diffs.
No full source tree is committed and hbb_common is not vendored.

v1 common hash: `87b7fb949b3bbc55c6d1e166909e167ebb8e0b6586630c0269f6440ba0542531`.
v1 SOS hash: `d752022800a8008b10aedd1a79412a00af027464b1754b068c35a0b5b439ea34`.
v1 metadata status: validated, backed by the actual stable run above; runtime validation
is not part of that status. v2 status: compatibility_validated, backed by real Rust/Flutter/Bridge run 36828069170. This is not full Windows-build or runtime validation.

## API migration

[API migration report and behavior contracts](api-migration-v1-to-v2.md).
Current queried upstream default branch master at
`fada664df7a294d1d1a9ca3e7cd3637069122f17`.
The configuration key moved from hbb_common config::keys to base::config::keys.
Upstream also removed plugin home/settings entries and changed general/printer guards.
v2 adopts the new key, retains upstream current UI predicates and adds historical SOS
restrictions to remaining entries. No native controller prohibition or password V2.

Original development detection [run 36819199270](https://github.com/billradar/rustdesk-custom-test/actions/runs/36819199270)
correctly failed API checks and skipped further jobs. This detection is functioning; it
is not a compatibility PASS. New v2 Actions execution PASS: [run 36828069170](https://github.com/billradar/rustdesk-custom-test/actions/runs/36828069170). Resolver reports v1 incompatible, v2 selected/COMPATIBLE, overall PASS at upstream fada664df7a294d1d1a9ca3e7cd3637069122f17.

## Resolver / regression evidence

Local actual independent clean clone/submodule probes:

| Case | Result |
|---|---|
| Stable 1.4.9 exact SHA | fixed v1; Common + SOS apply/config/API PASS |
| Current development SHA | v1 INCOMPATIBLE; v2 Common + SOS PREFLIGHT_COMPATIBLE; select v2 |
| Synthetic incompatible Git source | both rejected; NO COMPATIBLE PATCH SET; no fallback |

All six v1 migrated patches compare byte-for-byte equal to the original Git blobs.
Eight local regression tests PASS, plus Python compile, YAML and embedded Bash syntax.
These do not substitute for real compile/analyze/Bridge Actions tests.

Resolver probes are static/config selection gates in fresh separate clones. Selected
candidate still requires actual Rust check, Bridge and Flutter analyze downstream; the
aggregate report promotes to COMPATIBLE only when those jobs succeed. Real Rust probes
compile the helper against hbb_common for v1 or base + hbb_common for v2. Full Windows
build is separate and optional for the development branch, with artifacts only.

build-info and new test release notes record patchset. Historical 1.4.9 notes lack this
field; only its exact validated SHA/v1/frozen hashes admit legacy-format dedup. Nothing
is backfilled into old releases. New unknown releases require explicit Patch Set notes.

## Remaining Actions acceptance

Release deduplication: ACTIONS PASS — [run 36827239365](https://github.com/billradar/rustdesk-custom-test/actions/runs/36827239365); already_processed=true, build_needed=false, publish_needed=false; build/prerelease SKIPPED.
Synthetic patch failure gate: ACTIONS PASS — [run 36827438848](https://github.com/billradar/rustdesk-custom-test/actions/runs/36827438848); expected preflight FAIL at nonexistent-simulation, bridge/Windows/prerelease SKIPPED, diagnostic report uploaded.
New development v2 Rust/Flutter/Bridge: ACTIONS PASS — [run 36828069170](https://github.com/billradar/rustdesk-custom-test/actions/runs/36828069170). All preflight, native compilation, bridge and Flutter checks passed; generation report downloaded and inspected. The earlier fixture failure is resolved; release validation remains strict.
New development Windows Standard/SOS: NOT RUN (optional artifact-only deep validation).
Scheduled execution: CONFIGURED / NOT OBSERVED. No schedule PASS is inferred from manual runs.

No manual rerun is currently required for compatibility, dedup or failure blocking.
The expected simulated-failure run remains red by design, with costly jobs/release skipped.
Windows build job in development compatibility is skipped by design; no development release.
All observed runs are workflow_dispatch, not schedule. Final stage acceptance still waits
for a real scheduled event; it is not inferred or marked PASS prematurely.

## Security / limitations / repository safety

Normal jobs contents:read, only final test prerelease job contents:write/GITHUB_TOKEN.
No PAT, production credentials, untrusted PR workflow, floating third-party Action refs
or automatic patch rewriting. Official custom Flutter engine main download remains a
reproducibility risk, as do hosted runners/apt packages. Two GitHub releases cannot be
atomically exposed; partial final API failure requires manual recovery, never overwrite.

Build Reproduction: PASS.
Runtime/UI Validation: SKIPPED BY USER.
Real Remote Session Validation: NOT TESTED.
Code Signing: NOT ENABLED.
Configuration: TEST ONLY.
Windows x86_64 only. Password Security V2 deferred; embedded preset remains extractable.
SOS is historical UI hiding, not native Level 3 controller disablement.

All writes target only billradar/rustdesk-custom-test. Old billradar/rustdesk and
billradar/rustdesk-sos receive zero writes/triggers. Existing releases untouched.
No production repository, production config/release, old Actions deletion/archive,
signing or platform expansion performed.
