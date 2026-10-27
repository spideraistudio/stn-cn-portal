> Phase 4 update: ledger_workspaces adds owned workbook-level source/review state
> in the same account SQLite database. See PHASE4_LEDGER_SECURITY.md for the
> current runtime; later engine storage statements below remain design notes.

> Phase 3 update: document storage now uses the same account SQLite transaction
> for atomic live authorization. Earlier per-project database statements below
> are planned engine-adapter design. See PHASE3_WORKSPACES.md for current behavior.

# Current status — Phase 2

Account service uses a standalone Python WSGI adapter. See PHASE2_SECURITY.md
for sessions, administrator controls, permission enforcement and deployment
boundaries. The preserved financial baseline is unchanged. Phase 3 adds owned
projects/workbooks and object-level APIs.

---

# Architecture decision — keep the proven Python financial core

## Why

The baseline uses Python Decimal arithmetic, SQLite workbooks, local filesystem
PDF imports and a loopback HTTP server. The existing HTTP server has one local
token and local-host checks. It is not an internet authentication system and
must not be exposed as the production web service.

Retain the financial modules byte-for-byte for the initial migration. Add a
production Python web service around authenticated, user-scoped contexts.
Select the exact framework/deployment configuration after the account layer's
needs are recorded; do not translate Decimal rules into JavaScript to fit a
hosting platform. Browser code is never authoritative for rates or permissions.

The inspected Sites hosting contract uses a Cloudflare Worker runtime. It can
host a frontend, but cannot directly run this existing Python server with its
SQLite/filesystem dependencies. A Sites frontend would therefore need a separate
Python backend and verified server-to-server/user-session integration. No Site
was registered or deployed during Phase 1, which delivers backend foundation
and compatibility evidence rather than a finished website. No public endpoint
or login screen is presented as operational.

## Phase 1 executable components

- `backend/cn_web/workspaces.py`: trusted identity -> opaque workspace key ->
  private storage directory. Registry stores enabled/disabled state and selected
  quota metadata. It does NOT enforce quota, implement accounts/login/passwords,
  or authorize administrator callers. Its mutation methods are internal only.
- `backend/cn_web/retention.py`: pure read-only candidate planner with an
  explicit allowlist of temporary categories; no deletion or scheduler.
- `offline_baseline/`: preserved Update35.2 source, tests and synthetic fixtures.
  No user workbook, private uploaded PDF, production database or credentials.
- `baseline_manifest.json`: SHA-256 checksums for the entire preserved baseline.

The future session layer supplies the verified identity. It must never trust a
browser user ID, project header, workbook ID, filename or client-supplied role
as proof of ownership. All object lookups are scoped to that identity before
calling existing project/workbook services. Authentication and authorization
will be tested through real HTTP in subsequent phases.

## Persistence and concurrency

Use one account registry and a separate private storage root per user. Continue
separate project/workbook databases below that root initially to preserve existing
schema and snapshots. Sessions and account metadata will be outside workbook
exports. Never use global “current user”, “current workbook” or mutable store
switching to route concurrent requests. Resolve context per request and preserve
optimistic saved revisions, frozen guards and reviewed preview fingerprints.

Application-level isolation is not an operating-system sandbox. The service
operator retains infrastructure access. Directory ownership, service identity,
symlink safeguards and storage backups need production deployment checks.

## Storage allowance and retention (Phase 7)

Count originals, saved work, generated files and staging reservations against a
clear allowance; define database/WAL and backup accounting before enabling it.
Reserve space atomically before receiving uploads. Abort and release reservations
on failure. Recheck settings imported through every supported format.

When over quota, keep read/export available; reject growth with an actionable
message. Do not delete financial records to make room automatically. Keep enough
operational headroom for audit writes and emergency export/cleanup.

A scheduled worker will create an auditable candidate plan, recheck active and
saved references at deletion time, then delete only eligible temporary objects.
Preview expiry, upload leases and cleanup permissions are server-side. Backups
have a separate policy. This foundation does not activate recurring deletion.

## Financial migration gates

Use identical original receipt snapshots and workbook settings. Compare entire
normalised engine outputs, not just the grand total. Check separate rounded CNs,
ABS old-dues clearance/excess routing, actual-date CD, Cash/regular exclusions,
DAWAT segment separation, frozen issue history, requested-only adjustments, NRV
exclusions, IPT and April–March Year Link. Add a mixed-season test for delayed
Kharif CN posted after Rabi supply before promising February Rabi correctness.
No new cross-season accounting rule has been implemented in Phase 1.


## Phase 5 interface adapter
`/calculator` reuses the existing Update35.2 shell/assets. Authenticated transport
maps its request paths to CalculatorService, which loads a private in-memory
Store from owned calculator_workspaces rows and commits inside the same account
transaction as permissions and audit. The offline HTTP server is never mounted.
Source-bound calculation uses a reviewed season item mask and calculation-only
start-to-cutoff stock envelope, preserving original dates and saved period dates.
Phase 4 services remain authoritative for provenance, source review and Year Link.
Project backup v3 includes validated draft calculator tables; source/record/layout
IDs remap into an independent copy. See PHASE5_INTERFACE_SECURITY.md.
