# Phase 2 account service design and boundaries

## Stack and identity

Python WSGI application (`http_app.AccountApp`) is separated from the offline
loopback server. The local runner uses wsgiref on 127.0.0.1 solely for account
review. The production WSGI factory requires CN_WEB_DATA and CN_WEB_ORIGIN;
there are no default passwords, public registration or HTTP bootstrap route.
A supported production server, TLS gateway and trusted-proxy configuration will
be completed in Phase 8 before any hosted use. This phase is not deployed.

There is one operator-created administrator. Admin-created accounts are ordinary
users and cannot grant themselves an administrator role through JSON fields.
The admin flag grants account administration, not cross-user ledger access or
an implicit financial-permission bypass. There is no support impersonation route.
Forgotten-user passwords can be reset by the administrator; emailed resets and
operator recovery of a forgotten administrator password are not implemented.

## Passwords

Passwords use salted Python/OpenSSL scrypt, N=16384, r=8, p=5, dklen=32, 16-byte
random salts. This is one of OWASP's published scrypt memory/CPU tradeoffs.
Password policy: 12–128 characters, at most 512 UTF-8 bytes. No plaintext password
is stored or included in account/audit responses. Unknown account login uses a
dummy scrypt comparison. Disabled/unknown/wrong-password errors are generic.
New and reset users must change their temporary password before opening a
workspace. Change/reset revokes every session. The CLI uses hidden getpass entry.

The service persists failed-login throttles: five failures per normalised username
or 30 per direct source IP in a rolling 15-minute window. Forwarded IP headers
are not trusted. Expired attempt history is pruned on login. Multiple users behind
a proxy will share its IP until production ingress/trusted-source-IP policy is
configured. Hosted load/DoS protection belongs to deployment testing.

## Sessions and browser protections

32 random bytes produce each session cookie. Only its SHA-256 digest is stored.
Successful re-login rotates the presented session; session fixation is not used.
Sessions have an eight-hour absolute timeout and 30-minute idle timeout. Revoke,
disable and expiry are checked server-side on every protected request. Session
changes and account mutations are serialized by SQLite transactions.

Production cookie: __Host-cn_session, Secure, HttpOnly, SameSite=Strict, Path=/,
no Domain. Development has a separately named cookie and is restricted to local
HTTP. Production rejects a non-HTTPS WSGI scheme even if an untrusted caller adds
X-Forwarded-Proto. The deployment gateway must supply trustworthy WSGI scheme
metadata after terminating TLS; this service never blindly trusts those headers.

All mutations including login require the configured exact Origin and JSON.
Authenticated mutations also require a per-session anti-CSRF header, obtained
from same-origin /api/me. No CORS access is enabled. APIs reject query-based user
selection, oversized bodies, unsupported fields and forged Host. Security headers
include no-store, CSP, anti-framing and no-referrer; production adds HSTS. Browser
code uses textContent for account content and keeps no session credential in
localStorage or sessionStorage.

## Ownership and permissions

The only workspace API currently returns metadata for the server-verified user.
X-CN-User, X-CN-Role, X-CN-Project, X-CN-Workbook and bearer strings cannot select
another user's workspace. No filesystem path is returned. The original offline
API and static data directories are not exposed by the new service.

Central checks support all ten planned financial permissions. Tests check grant
and revoke for each; the implemented workspace endpoint also enforces its view
permission over real HTTP. Financial endpoints do not exist yet. They must call
the same permission service and reauthorize inside their write transaction.
Imports, scheme shortcuts, Cash settings and mappings must not bypass edit rights.
Permission edits are read live; existing cookies cannot retain old permissions.

## Account operations and audit

Administrator APIs create users, list account metadata, update enabled status/
permissions/quota, reset passwords and read account audit events. Quota is only
metadata in Phase 2. The root administrator cannot be disabled. User creation and
workspace insertion are atomic, including duplicate/race failures. No HTTP route
can set is_admin, change a workspace path or use the internal provision method.

Audit includes bootstrap, login/failure, account creation/change, password reset/
change and sign-out actions. It omits passwords, password hashes, session and CSRF
tokens, body dumps and ledger contents. Audit retention/export and hosted support
operations are future work. POSIX account root/database modes are restricted to
700/600; Windows hosting needs the dedicated service account's filesystem ACLs.

## Verification boundaries

Tests use actual localhost HTTP with isolated temporary accounts and production
KDF settings. They are regression evidence, not a penetration-test certificate.
PC form bindings, safe DOM operations and JavaScript syntax are checked. Native
browser/Windows visual acceptance and hosted TLS/proxy tests have not run.
The existing financial core is untouched and checksum verified. Phase 1's full
332-test baseline run (331 passes, one optional private-PDF skip) is historical
evidence; financial tests were not repeated for account-only Phase 2 work.

## Primary references consulted

- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
