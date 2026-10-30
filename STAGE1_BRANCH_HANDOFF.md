# Stage 1: cumulative source update — 30 October 2026

Target: `spideraistudio/stn-cn-portal`, branch `fix/combined-portal-production`.
Base: `aa4e8937c6d826e6567ef37c8d5b2c23878ef9eb`.

This update brings the latest offline acceptance package into the existing
branch. It includes previous-year receipt evidence and crop reservations,
earlier-dues clearance, approved late-CN reconciliation, carried-credit
conversion dates, opening-credit overlap protection, unlinking, non-blocking
PDF import feedback, optional STN business summaries and buyer dates, and
consistent public-page/theme/loading colours. Existing artwork is retained.

Read `PRIOR_RECEIPTS_UPDATE.md`, `TEST_RESULTS.md` and
`FULL_AUDIT_HANDOFF.md` for rules, recorded verification and limitations.
Existing verification records are historical unless explicitly rerun.

Fresh checks before this source commit: 19 prior-payment model tests, four
prior-payment API tests, seven STN seed/report tests, TypeScript `--noEmit`,
and `git diff --check` passed. These are local checks, not hosted acceptance.

## Production status

This commit completes source synchronisation only. It is **not a production
readiness certification**. The local launcher must not be exposed unchanged.
VPS production services, proxy/TLS, secrets, persistent storage, backups and
restore, monitoring, deployment/rollback, and hosted workflow verification
remain to be implemented and tested. Windows acceptance remains pending.

No data migration or live-site switch is authorised by this stage. Test a
separate hosted copy and obtain owner approval before migration or cutover.
Preserve the original Meet-Dev repository and existing private data. Fresh
profiles must retain empty catalogues and schemes. Unknown packet weights
remain deferred.
