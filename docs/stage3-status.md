# Current stage 3 status

See [the current evidence report](rustdesk-upstream-automation-test-report-2026-10-01.md).

Stable automation, Standard/SOS Windows x86_64 and test prerelease: PASS (actual run).
v1 frozen and stable source regression: PASS locally; patch bytes/hash unchanged.
v2 development generation: Common/SOS/API, Rust fast check, Bridge and Flutter analyze ACTIONS PASS — [run 36828069170](https://github.com/billradar/rustdesk-custom-test/actions/runs/36828069170). Optional full development Windows builds NOT RUN.
Release deduplication: ACTIONS PASS — [run 36827239365](https://github.com/billradar/rustdesk-custom-test/actions/runs/36827239365); already_processed=true, build_needed=false, publish_needed=false; build/prerelease SKIPPED.
Failure gate: ACTIONS PASS — [run 36827438848](https://github.com/billradar/rustdesk-custom-test/actions/runs/36827438848); simulated conflict detected, bridge/Windows/prerelease SKIPPED; diagnostic artifact preserved.
Schedule: CONFIGURED / NOT OBSERVED.
Overall stage acceptance: PENDING.

Build Reproduction: PASS.
Runtime/UI Validation: SKIPPED BY USER.
Real Remote Session: NOT TESTED.
Code Signing: NOT ENABLED.
Configuration: TEST ONLY.
