# Phase 1 handoff — 21 October 2026

Status: COMPLETE for foundation scope. No online site deployed.

## Implemented

- Preserved Update35.2 source as `offline_baseline/`; 140 source/fixture files
  recorded in `baseline_manifest.json` and verified against the cumulative ZIP
  working source. No financial implementation changed.
- Created the eight-phase PC-only web migration plan and architecture decision.
- Implemented internal user-to-private-workspace registry and tested independent
  use of the existing Store/settings. Unknown/disabled identities, corrupt
  mappings, duplicate provisioning and workspace symlinks are guarded.
- Stored configurable quota metadata without inventing a user limit. Quota
  enforcement, accounts and public API authorization are NOT implemented yet.
- Implemented pure retention candidate planning, default 60 days; saved records,
  linked files, active jobs and backups are excluded. No deletion or automation
  has been enabled.

## Checks actually run

- Full preserved baseline Python suite: 332 tests, OK, 1 skipped (331 passed),
  85.224 seconds. The optional actual-PDF regression was skipped because its
  private input was not supplied. See `verification/offline_regression.txt`.
- New foundation: all 10 tests passed, including independent real Store settings,
  workspace scope/disabled/corrupt/symlink guards and retention exclusions.
  See `verification/foundation.txt`.
- Baseline checksum verification and deliverable ZIP integrity.

No new browser checks: Phase 1 contains no new web UI. Existing offline Windows
acceptance is not marked complete. The full web workflow has not been tested or
claimed operational.

## Next — Phase 2

Implement server-authenticated sessions/admin account lifecycle and a single
permission service used by every new API action. No open registration by default.
User identity must come from server verification, never client-selected headers.
Do not expose the original loopback app as the web server. Do not permit raw
workspace registry provisioning from a public endpoint.

Carry forward the offline financial engine unchanged and use per-request scoped
contexts. Add HTTP tests for login/logout, expired/invalid sessions, disabled
users, revocation, admin permission changes and cross-user access attempts.
Decide production-compatible authentication/deployment details with the existing
Python runtime constraints; do not silently substitute a rewritten JS engine.
