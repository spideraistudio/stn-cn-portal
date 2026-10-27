# Phase 2 handoff — 21 October 2026

Status: COMPLETE for account-layer scope. Cumulative from Phase 1. Local PC review
console included; no public deployment or full online calculator is claimed.

## Delivered

- Salted scrypt password hashing; one-time CLI administrator setup.
- Ordinary users created only by the administrator, with mandatory initial
  password change. No open registration or browser-based admin bootstrap.
- Opaque server-side sessions, HttpOnly cookies, login rotation, idle/absolute
  expiry, own logout, logout all, live permission checks and persisted throttles.
- Admin: account list, create, enable/disable, permissions, allowance metadata,
  password resets and account audit. Disable/reset revokes sessions immediately;
  re-enable never restores revoked sessions. Root admin cannot be disabled.
- Separate WSGI account service; original offline loopback app never exposed.
- Same-origin/CSRF/JSON/Host/TLS guards, strict field validation, safe error bodies,
  no browser-local session storage and no credential values in account audit.
- PC account console, operator setup and local Windows launcher files.
- Central permission checks for all ten planned financial permissions. Only
  account APIs and own-workspace metadata exist at this phase. Financial routes
  must use the same checks when implemented; button visibility is not authority.

## Verification actually run

`verification/phase2_all.txt`: all 32 tests passed in 25.895 seconds:
22 account/configuration/UI-contract tests plus the 10 Phase 1 foundation tests.
HTTP tests use a real loopback server, temporary data and the production scrypt
parameters. They cover password lifecycle, session rotation/expiry/revocation,
all ten permission grants/revocations, admin denial, forged identity headers,
cross-user workspace selection, throttle persistence, CSRF/Origin/Host/JSON/TLS
validation, concurrent duplicate creation and credential-free audit responses.

`verify_baseline.py`: all 140 preserved Update35.2 files match the manifest.
JavaScript syntax and Python compilation passed. ZIP integrity checked on the
final deliverable. No live user workbook, private statement or credentials used.

Financial code was unchanged, so the full financial suite was not repeated.
Phase 1's full run remains historical evidence: 332 tests, 331 passed, one optional
actual-private-PDF regression skipped. Phase 2 does not change that skip status.
Native browser/Windows visual checks, deployment TLS/proxy/load checks and real
user acceptance remain pending. This is not a security certification.

## Local review

Extract into a new folder. Run Setup_Admin_Windows.bat once to choose your admin
username, allowance and password. Run Start_Web_Phase2_Windows.bat; open
http://127.0.0.1:8787. Python 3.10+ is required; no new pip dependencies.
Data goes to %LOCALAPPDATA%\AllCropCNWeb, separate from the offline calculator.
There is no default password or supplied account database.

## Limitations and pending phases

Quota is metadata only; no cleanup job or auto-deletion is active. The PC
calculator UI, workbooks, financial API mutations, imports and reports are not
migrated yet. No arbitrary administrator view of user ledgers is implemented.
Forgotten-admin operator recovery and emailed reset flows are not implemented.
The local wsgiref runner is not a production internet server.

## Next — Phase 3 independent workspaces

Add authenticated per-user projects, workbooks, settings, parties, files and
layouts with object-level ownership checks and revision guards. Keep account
sessions and permissions out of exports. Imports/quick builders/Cash shortcuts
must respect scheme-edit restrictions. No default merging or cross-user access.
Use the existing Python financial core and test identical object IDs in different
users' workspaces, concurrent requests, stale revisions and failed imports.
Every new mutation must recheck the session and required permission inside its
write boundary. No mutable global current-user/current-workbook routing.

Read README.md, PHASE_PLAN.md, docs/PHASE2_SECURITY.md and the baseline handoff
before continuing. Preserve all original receipt dates, rules, separate rounding,
issued/frozen history, both interfaces and independent saved layouts.
