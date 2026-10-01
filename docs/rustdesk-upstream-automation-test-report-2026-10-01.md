# RustDesk upstream automation — implementation checkpoint, 2026-10-01

**Status: implementation uploaded; Phase 3 GitHub execution/acceptance still pending.**
This is not a completed test report. No Phase 3 build or test prerelease is claimed.

Test repository: https://github.com/billradar/rustdesk-custom-test

## Architecture

`upstream-compatibility.yml`: daily UTC 03:23 and manual → query default_branch →
freeze commit SHA → reusable test-build validation_only → patch/config/API/native
mock + real hbb_common Rust check + generated-bridge Flutter analysis → reports.
No Windows client jobs or release writes on this path.

`release-check.yml`: UTC 05:41/17:41 and manual → official stable Release metadata →
freeze tag/SHA → dedup revision → test-build preflight → bridge/analyze → independent
Standard/SOS Windows x86_64 jobs → metadata/checksum/architecture pair gate → two
staged drafts → test prereleases only. Both client artifacts must exist and match provenance.

Patch files were not modified. Official submodules are initialized at gitlink SHAs.
Source code remains temporary and is not committed to this maintenance repository.

## Actual local tests

- Two separate clean official `1.4.9` source trees initialized with official submodules,
  SHA `6c578292e8ebbbec708b76986ba8c4bc7c509747`.
- Common clean apply: PASS. Common + SOS clean apply: PASS.
- Configuration wiring/static contracts: PASS for both. No rejected hunks.
- Standard/SOS structural separation: PASS.
- Build-system hashes against historical profile: no differences at 1.4.9.
- Six Python regression tests: PASS. They cover API release flags, prerelease exclusion,
  no-new dedup, new-stable decision, forced artifact-only rebuild, required paired provenance,
  checksum corruption, wrong PE architecture and a false Runtime PASS status.
- Synthetic nonexistent-file `git apply --check` refusal: PASS locally.
- YAML parsing, embedded Bash syntax and Python compilation: PASS.
- Local Rust/Flutter compilation: NOT RUN (these toolchains are not installed here).
  They are required in GitHub preflight; no green build claim substitutes for their execution.

## Actual development branch finding

Upstream default_branch API returns `master` at inspection time; the workflow queries
this dynamically. Current SHA `fada664df7a294d1d1a9ca3e7cd3637069122f17`.
Common patches clean apply, but the interface dependency check fails:
`hbb_common::config::keys::OPTION_ALLOW_REMOTE_CONFIG_MODIFICATION` was moved to
`libs/base/src/config/keys.rs`. The preserved helper still uses the historical path.
Thus current development compatibility is **FAIL at the API layer**, not a patch conflict.
The old stable 1.4.9 still supports the dependency. No automatic patch change was performed.
Upstream build-file changes are also detected as warnings.

## Stable detection / version deduplication

Official Release API flags inspected: 1.4.9 stable, 1.5.0 prerelease, nightly prerelease.
Only non-draft, non-prerelease numeric versions are eligible; numeric sorting selects
latest stable. Manual upstream_ref must identify one of those official releases.

Tags: `v1.4.9-custom-test.1`, `v1.4.9-sos-test.1` for revision 1.
Internal upstream Cargo/Flutter/Windows versions remain unchanged.
An existing complete pair must match upstream SHA, canonical LF patch hashes and expected
assets. It exits without builds. force_rebuild produces artifacts only for an already
published revision. Partial/different existing releases fail for manual review; never overwrite.

## Standard / SOS / test prereleases

Phase 1 full build PASS evidence:
https://github.com/billradar/rustdesk-custom-test/actions/runs/36812800414
This used post-tag SHA `005a8b4a04fd906c707eefd69c4898aa2c696202`.

Phase 3 official stable 1.4.9 Windows Standard build: **NOT RUN**.
Phase 3 official stable 1.4.9 Windows SOS build: **NOT RUN**.
Phase 3 client artifacts/metadata/checksum/architecture: **NOT RUN**.
Phase 3 test prereleases: **NOT CREATED**.
GitHub failure-path blocking and no-new cheap exit: **NOT RUN** (unit/local tests only).
Actual cron execution: **NOT OBSERVED** (schedule configured, not execution evidence).

Official stable tag is two upstream commits before Phase 1: clipboard hardening and
Korean translation are absent. This is an explicit source baseline difference, not a
custom behavior rewrite. Runtime comparison was waived; no functional equivalence claim.

## Security / limitations

All normal jobs contents:read; only test prerelease job contents:write, GITHUB_TOKEN.
No PAT, production Variables/Secrets, new secret storage, untrusted PR trigger or
pull_request_target. Inputs enter quoted env variables/Python APIs, never shell code.
Third-party Actions stay pinned to full commit SHAs. Downloads use the already proven
upstream path. Floating official custom Flutter engine `main` remains a reproducibility risk.

The release validator checks all payload checksums, every root PE binary machine type,
exact upstream tag/SHA/run/maintenance SHA, variant and canonical patch hashes. Artifacts
are downloaded from the same workflow run only. Both draft assets must upload before exposure.
GitHub cannot atomically expose two releases: a final API failure can leave partial exposure;
the job fails and subsequent dedup blocks automatic overwrite until manual recovery.

Rust quick check compiles the actual helper against real hbb_common via a temporary binary
in the temporary submodule, not the full native codec app. Flutter analyze covers the four
patch-related pages; error severity fails, upstream warning/info remain in diagnostic logs.
Full Windows Rust/Flutter builds remain required before publishing. Static SOS guards do
not prove native controller denial, navigation closure, or remote-session behavior.

- Build Reproduction: **PASS (Phase 1 only)**
- Runtime/UI Validation: **SKIPPED BY USER**
- Real Remote Session Validation: **NOT TESTED**
- Unsigned binaries; TEST ONLY fictional configuration; Windows x86_64 only.
- Password Security V2 deferred; old embedded plaintext preset is extractable.
- No production repository/release, production configuration, platform expansion or old Actions changes.

## Old repository safety

No write call or workflow dispatch was made to `billradar/rustdesk` or
`billradar/rustdesk-sos`. All this phase's remote write operations target only
`billradar/rustdesk-custom-test` (normal forward commits; no force push).

## Next execution evidence

Run both new workflows manually in the test repo. Stable input: upstream_ref `1.4.9`,
force_rebuild false, simulate_failure false. Record exact jobs and artifacts; repair only
minimal necessary build-adapter issues if execution fails. After a complete pair exists,
rerun for dedup and separately run simulate_failure true to prove early blocking.
Then update this report with real run/prerelease links and observed schedule evidence.
