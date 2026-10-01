# Stage 3 implementation and validation status

Project: TEST / DEVELOPMENT only. Old repositories remain read-only.

| Validation | Status |
|---|---|
| Phase 1 build reproduction (official SHA 005a8b4a04fd906c707eefd69c4898aa2c696202) | PASS |
| Runtime/UI Validation | SKIPPED BY USER |
| Real Remote Session Validation | NOT TESTED |
| Phase 3 local stable 1.4.9 patch + structural/config checks | PASS |
| Phase 3 automation regression tests | PASS (6 tests) |
| Phase 3 GitHub compatibility execution | NOT RUN |
| Phase 3 stable Windows Standard/SOS builds | NOT RUN |
| Phase 3 test prereleases | NOT CREATED |
| Actual scheduled execution | NOT OBSERVED |

Phase 1 evidence: https://github.com/billradar/rustdesk-custom-test/actions/runs/36812800414

Official stable release model inspected 2026-10-01: `1.4.9` is non-draft/non-prerelease;
`1.5.0` and `nightly` are prereleases. Discovery uses API flags and numeric version ordering,
not the newest tag or a name-only guess. Manual stable builds require an official stable release.

The first stable automation target is `1.4.9`, SHA
`6c578292e8ebbbec708b76986ba8c4bc7c509747`. This is **not** the Phase 1 post-tag SHA.
It excludes the two upstream commits in that historical build (Windows clipboard hardening
and Korean translation); custom patches are unchanged. Runtime equivalence is not claimed.

## Required execution evidence before completion

1. Run `TEST - Upstream development compatibility` manually. A genuine upstream patch/API
   failure is an expected diagnostic FAIL, never a claimed compatibility PASS.
2. Run `TEST - Stable discovery and paired prerelease`: upstream_ref `1.4.9`, force false,
   simulate_failure false. Record both Windows builds, artifacts, manifests and test prereleases.
3. Run the same stable workflow again: verify discovery exits with no build/release jobs.
4. Run it with simulate_failure true: synthetic nonexistent-file patch must fail preflight;
   bridge/Windows/prerelease jobs must be skipped. Tracked patches are never modified.
5. Observe cron runs separately. A manual run does not prove the schedule actually ran.

Only after actual evidence may these NOT RUN statuses be changed. This implementation
has no production repository/release/configuration path.

## Observed development-branch incompatibility

2026-10-01 local source check at official master
`fada664df7a294d1d1a9ca3e7cd3637069122f17`: Common patches clean apply, but
`hbb_common::config::keys::OPTION_ALLOW_REMOTE_CONFIG_MODIFICATION` no longer exists.
The upstream constant moved to `libs/base/src/config/keys.rs`; the historical helper
still references hbb_common config::keys. Structural API gate correctly FAILS.
This is a real upcoming API incompatibility, not a patch apply conflict. No automatic
patch rewrite was performed. The tested stable 1.4.9 still has the required constant.

Build-system snapshot also detects changes in workflows, Cargo, Flutter lockfiles,
build.py/build.rs and vcpkg; these are warnings unless the pinned adapter path is broken.
