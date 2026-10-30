# Stage 2 — production source/configuration, 30 October 2026

Branch: `fix/combined-portal-production`, based on
`fb4e89226b70873a0cf45478e5a2cd2b37715b84`.

## Implemented

- Separate production factories for the combined HTTPS gateway and private
  identity bridge, using Gunicorn and secure `__Host-cn_session` cookies.
  Production never enables the local launcher or development cookie mode.
- Shared gateway routing extracted without changing the Windows launcher's
  loopback policy. Proxy scheme follows the configured origin.
- Loopback-only Node/Python services, exact host/origin checks, trusted edge
  forwarding, client-address replacement and private-route denial. The Node
  identity URL remains restricted to loopback. Gunicorn control socket disabled.
- Caddy HTTPS configuration and systemd service/restart/cleanup/backup templates.
  Node and CN have separate Unix users; private CN data is outside code releases.
- Exclusive fresh-server secret generation; no automatic key rotation, data
  migration, catalogue seeding or default administrator credentials.
- Immutable commit-based release preparation, explicit activation and code
  rollback on readiness failure. Activation and backup share an operation lock;
  cleanup/app workers pause for coherent capture and release changes.
- Encrypted off-server restic backup routine: briefly pause writes, dump Mongo,
  capture all CN files/settings, resume services, upload and check the repository.
  No automatic repository creation, pruning, deletion or live restore.
- Readiness checks cover Python/SQLite, the identity bridge and Node/Mongo.
  `deploy/README.md` documents setup, activation, recovery and acceptance gates.

## Fresh verification

| Check | Result | Evidence |
| --- | --- | --- |
| Production trust/session/operator safeguards | 15 tests passed | `verification/stage2_production.txt` |
| Existing combined account tests | 24 tests passed | `verification/stage2_accounts.txt` |
| Combined Next production build / TypeScript | Passed | `verification/stage2_build.txt` |
| Caddy configuration | Validated with Caddy 2.11.7 | `verification/stage2_caddy.txt` |
| Unit directive/dependency syntax | Passed with test-host executable substitutions; VPS paths are not installed here | `verification/stage2_units.txt` |
| Real Caddy TLS + Gunicorn + Next + authenticated Mongo | Passed | `verification/stage2_tls_smoke.txt` |
| Python compile, shell/Node syntax and whitespace | Passed | Source preparation checks |

The integrated smoke uses disposable authenticated MongoDB 8.0.17, a dedicated
database-limited app user, a local test CA and a temporary test-only DNS mapping.
Both Python and Node validate its certificates. It tests public pages, private
endpoint denial, registration/duplicate, actual unified approval callback,
secure login, required password change, STN/CN access, spoofed-edge headers,
dependency outage/recovery, saved sessions across gateway restart and logout.
Test workers use a five-second graceful shutdown budget to bound test cleanup;
production allows 180 seconds and systemd waits 200 seconds. Systemd supervision,
public ACME certificates and actual VPS reboot are not tested by this harness.

Early attempts exposed test namespace/service-lifetime setup, an inherited
outbound proxy and a test timeout shorter than the production drain budget.
The final self-contained test runner isolates all services, disables inherited
Node proxying for same-server callbacks and uses the stated test drain budget.
Final records above are passing. These were local tests, not hosted acceptance.

Financial engines, benefit formulas and saved financial records are unchanged
by this stage. The preceding CN/STN tests and build remain historical evidence;
their counts are not added to these as unique tests.

## Not yet applied to the owner's VPS

Hostinger sign-in is restricted from this cloud browser. No authenticated VPS
inventory, IP/OS/capacity/firewall inspection or SSH connection was available.
The owner's purchase/running status is user-reported, not independently checked.

**Not done:** server package installation, database/user creation, real secrets,
service installation/enablement, real DNS/HTTPS, off-server backup destination,
restore drill, hosted workflow/financial acceptance, crash/reboot verification,
monitoring destination, existing-data migration and live cutover.

Next: confirm the actual VPS overview/access and an owner-approved staging
hostname, read its current state, apply the reviewed configuration to the
separate staging copy, and run the hosted acceptance gate. Preserve the live
Node hosting and original Meet-Dev repository. Obtain explicit approval before
migrating existing data or switching the live deployment. A configuration commit
must not be represented as a production-ready deployed service.
