# Stage 2 — production configuration, not a live deployment

This configuration targets a **fresh Ubuntu 24.04 LTS VPS** and an approved
**staging hostname**. Confirm the actual OS, IP, current services and capacity
before applying it. It has not yet been installed on the owner's VPS. Do not
reuse `integration/run_local.py` as an internet-facing server.

## Architecture

Browser → Caddy HTTPS → loopback Gunicorn gateway → secure combined PortalApp
or loopback Next.js. Next.js calls a separate loopback identity service using
the bridge secret. STN uses authenticated loopback MongoDB; CN uses the existing
private SQLite/workspace storage. Separate Unix users run Node and Python.
Only ports 80/443 and approved SSH access should be publicly reachable.

Preserved: registration → administrator approval → temporary credentials →
required password change → permitted modules; private CN ownership, storage
limits and financial rules; empty catalogues/schemes for fresh profiles. No
data migration, catalogue seeding or live DNS changes occur in these scripts.

## 1. Read-only VPS preflight

Inspect `/etc/os-release`, RAM/disk (`free -h`, `df -h`), listeners (`ss -lntp`),
firewall, installed services and existing websites. Do not replace another
site's Caddy/Nginx configuration or reinstall MongoDB over existing data.
Capture current DNS, especially MX/SPF/DKIM/DMARC/verification records, before
any future domain changes. Choose a separate staging hostname with the owner.

Install supported Node.js 24 LTS at `/usr/bin/node`, Python 3.12 with venv,
Git, Caddy, restic, and MongoDB Community 8.0 plus database tools from official
vendor/signed repositories. Review exact installed patch versions and updates
on the VPS. Pin the reviewed code commit; use `npm ci` and the pinned Python
requirements. No purchase or package-install commands run automatically here.

Vendor references:

- https://nodejs.org/en/download
- https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-ubuntu/
- https://www.mongodb.com/docs/manual/tutorial/enable-authentication/
- https://caddyserver.com/docs/install#debian-ubuntu-raspbian
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- https://gunicorn.org/deploy/
- https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html

## 2. Private accounts, storage and configuration

After preflight, create system users `stncn` and `stnnode` with no interactive
shell and no sudo. Create `/srv/stn-cn/releases` (0755), `/var/lib/stn-cn/cn`
(0700, stncn), `/var/cache/stn-cn/next` (0700, stnnode),
`/var/cache/stn-cn/restic` and `/var/backups/stn-cn` (0700, root), and
`/etc/stn-cn` (0700, root). Keep `/srv/stn-cn` root-owned and 0755.

MongoDB must bind **127.0.0.1 only**, with authorization enabled. Create an app
user limited to `readWrite` on the new staging database, and a separate backup
user with the permissions needed to dump it. Never expose 27017 publicly.
This app currently uses single-document Mongo operations, not replica-set
transactions; do not assume backup consistency while app writes are active.
Existing database users/data need a separate migration plan and owner approval.

Clone only `spideraistudio/stn-cn-portal` to `/srv/stn-cn/repository`, branch
`fix/combined-portal-production`, using an operator-managed read-only deploy
key or other secure GitHub access. Do not store a token in the remote URL.
Configure on the server, with the MongoDB URI entered at a hidden prompt:

```bash
sudo python3 -m deploy.configure --origin https://APPROVED-STAGING-HOST --admin-email OWNER_EMAIL
```

Run from the checkout. It creates `/etc/stn-cn/app.env` mode 0600 and refuses
to overwrite any existing file. Generated bridge/lookup keys are different.
Keep these keys for the lifetime of stored data. **Never regenerate the lookup
key during an update.** Existing offline keys must be migrated deliberately,
not replaced by fresh keys. Do not paste credentials into chat or Git.

`STN_MONGO_TLS=0` is permitted here only because Mongo binds authenticated
loopback on the same VPS. A remote database needs a separate TLS configuration.

## 3. Prepare an immutable release

As root on the VPS, run the following from the reviewed checkout:

```bash
bash deploy/prepare-release.sh FULL_REVIEWED_COMMIT_SHA
```

The script checks that commit belongs to the named branch, refuses overwrites,
installs dependencies and builds combined-mode Next.js. Release source is
root-owned/read-only to app users; Next's writable cache is outside releases.
The Python venv belongs to that release. Nothing starts or switches here.

Copy the reviewed `deploy/systemd/` units into `/etc/systemd/system/` and run
`systemd-analyze verify` on them, then `systemctl daemon-reload`. These are new
unit names; inspect for collisions before installation. Do not start them yet.
Use the supplied Caddy example for **only the approved staging hostname**.
Validate the complete Caddy config with `caddy validate --config ...` before
reloading. Preserve other virtual hosts. Public DNS and ports 80/443 must reach
this VPS for automatic certificate issuance. DNS/cutover is a later approval.

## 4. Explicit staging activation and first administrator

After approving this staging activation and its hostname:

```bash
sudo python3 -m deploy.activate_release FULL_REVIEWED_COMMIT_SHA --origin https://APPROVED-STAGING-HOST --approved-activation
```

This explicitly changes `/srv/stn-cn/current`, restarts the three app services
and waits for real TLS-validated `/ready`. A failed update restores the prior
code symlink; an initial failure leaves services stopped. It never copies data
or reverses a database migration. Activation pauses writes and must not overlap
backup (both share an operation lock). Live activation still requires owner
approval regardless of the command-line flag.

For a **fresh installation only**, create the administrator using a temporary
root-owned systemd service with the same app.env and `User=stncn`, or:

```bash
sudo systemd-run --wait --pty --collect --uid=stncn --gid=stncn --property=WorkingDirectory=/srv/stn-cn/current --property=EnvironmentFile=/etc/stn-cn/app.env /srv/stn-cn/current/.venv/bin/python -m deploy.manage bootstrap-admin
```

The pseudo-terminal supports hidden password input. There are no defaults;
bootstrap refuses when accounts already exist. Never bootstrap over migrated
accounts. The browser administrator cannot read other users' private CN data.

After successful staging checks, enable the three app services for reboot and
`stn-cn-maintenance.timer`. Enabling/restart behavior must be tested on the
actual VPS. Local configuration checks do not certify a server reboot.

## 5. Encrypted off-server backups and recovery drill

Choose an owner-approved private off-server restic destination. Store its
password and Mongo dump settings as root-only files and adapt
`backup-settings.example` to `/etc/stn-cn/backup.env` (0600). Initialise the
new restic repository once deliberately; the backup routine will not do this
or prune/delete old snapshots. Keep a separate secure recovery copy of the
restic password; a backup of that password inside the repository cannot
unlock the repository by itself. Do not use the VPS disk as the only backup.

Run `stn-cn-backup.service` once and inspect its result before enabling the
daily timer. The routine verifies the remote repository, pauses previously
active app/cleanup services, dumps the staging Mongo database, archives the
entire CN directory and settings, then restores prior service state. It
encrypts/uploads the immutable snapshot and checks restic. Failure is reported
through systemd and does not record a successful backup. A short scheduled
availability interruption is intentional. Do not run external database writers
during capture. A hard power loss or SIGKILL during a pause requires inspecting
and restarting stopped services; a backup is not counted as completed then.

Restore drill **on an isolated server or separate protected directories**:

1. `restic snapshots --tag stn-cn`, then restore a chosen snapshot into a new
   empty, private recovery directory. Never restore directly over live paths.
2. Find `snapshot.json`, `private-state.tar.gz`, `mongo.archive.gz`. Confirm the
   code commit; list tar members and safely extract using Python 3.12's data
   filter into the recovery directory. Preserve the original private keys.
3. Run `PRAGMA integrity_check` on every recovered SQLite DB. Restore Mongo
   into a **separate disposable Mongo instance**, bound to a different loopback
   port/data path; never use the production URI or `--drop` on production.
4. Start the recorded code release against recovered isolated data and a
   separate HTTPS test origin. Confirm account login, STN records, source PDFs,
   frozen CN totals and ownership/permissions. Record the successful drill.
5. No production restoration occurs until the owner approves the exact target
   and data-loss window. Code rollback and database restore are separate steps.

Do not call backups ready until a real restore drill passes. Timer times are
specified in UTC, independent of the server timezone (03:45 UTC = 09:15 IST).

## 6. Hosted acceptance gate (still pending)

Check the exact deployed SHA and dependency versions; valid HTTPS; public
navigation/loading in both themes; registration/duplicate handling; approval;
forced password change; company/staff module controls; private CN ownership;
statement import/mapping; credit- and debit-opening Year Link; ABS conversion
dates/limits; known financial totals; issued-history immutability; STN reports
and optional Buy/Sell dates; sign-out/expiry; backup restore; service crash and
VPS reboot. Inspect public listeners and firewall from outside the VPS.

`/health` is gateway liveness only. `/ready` checks the private identity/SQLite
and authenticated Node/Mongo health. Monitor `/ready`, service failures, disk
capacity and backup last-success age from an owner-approved monitoring service.
No notification service or paid integration is activated here.

Do not connect automatic branch-to-live deployment yet. Prepare reviewed
commits, verify staging, obtain owner approval and take a tested backup before
each production activation. Preserve the current hosted app until cutover is
explicitly approved.
