# Combined application phases

| Phase | Scope | Local status |
|---|---|---|
| I0 — inspect and preserve | Pin Meet-Dev, verify source/database/auth/storage, read CN handoff, independent branch | Complete; 284 STN blob hashes verified, MongoDB confirmed |
| I1 — common authority | Individual login, company policy, module entitlements, explicit links, scoped resets/revocation | Implemented; automated HTTP and real-service tests pass |
| I2 — portal and administration | Two module choices, switchers, existing STN admin navigation, company/subscription controls, existing CN quota/permission console | Implemented; Linux Chromium checks pass |
| I3 — retained module behavior | Original CN engine/interface; STN member, category, report, search and trading rules | Implemented; regression and combined journeys pass |
| I4 — storage and migration rehearsal | Separate module usage, retained CN quotas/cleanup; copied-account inventory/linking; restart/interchange | Implemented for local tests; actual user-data rehearsal remains pending |
| I5 — local acceptance package | Windows launchers, complete source, test results and checklist | Delivered as a candidate; Windows user acceptance pending |
| I6 — production staging/cutover | Verify deployed STN commit/database/key, backup/restore, TLS/process/database operations, capacity and approved migration | Not started; no deployment or purchase authorized |

No phase label confers production certification or Windows acceptance. Original calculator Phases 2–7 retain their user-reported acceptance. New hierarchy/navigation and 7.2/7.2.1 audit acceptance is only as recorded in the supplied handoff; this integration does not mark new Windows checks accepted.
