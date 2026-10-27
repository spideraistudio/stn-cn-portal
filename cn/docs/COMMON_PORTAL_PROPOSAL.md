# Proposed common company portal — CN Calculator + Seller Trust Network

23 October 2026. Proposal only: this cumulative calculator update does NOT deploy
hosting, migrate STN, introduce subscriptions or replace either login system.

## User experience and account authority

One named-user login opens two module cards: CN Calculator and Seller Trust Network.
A module switcher returns to this choice without another login. A company has a
subscription; individual staff still have their own credentials and audit history.
No shared company password. One central password reset/session revocation flow.

Platform superadmin controls company accounts, company admins, purchased modules,
seat/storage limits and subscription periods. A company admin manages only their
own staff, within the purchased modules and rights the superadmin grants.
Per-user switches independently enable CN and STN. STN actions may additionally
separate view/search, reports, and buy/sell activity using its existing policy.
An expired/unpurchased company entitlement cannot be overridden by its admin.
Disable access in both UI and every API; hiding a card alone is insufficient.
Platform operator authority must stay distinct from a customer's company admin.

Current CN defaults remain 1024 MiB own admin storage, five user slots, 250 MiB
per user. Existing users' workspaces and allowances are retained. Company
membership must NOT grant an admin access to private CN workbooks. STN data
continues to follow its approved-member/network sharing rules. Neither module's
records are automatically merged into the other. Keep CN source PDFs and
allocations private even if the same staff member uses STN.

## Subscriptions and identity

Recommended initial package structure: CN-only, STN-only, or both; bill the company
once. Store plan/expiry, entitled modules, staff limit and storage policy centrally.
Payment-provider integration, tax/invoices, expiry/read/export policy and payment
failure behavior are later scoped work, not invented defaults in this release.

Choose one authoritative identity/session service; both Node STN and Python CN
must validate it server-side. A standards-based SSO flow or secure server-mediated
session exchange can bridge the two services. Do not pass passwords/session tokens
in URLs, create a second password copy, trust user/role headers from browsers, or
embed one unrelated login page behind a card and call that SSO. Reconcile existing
accounts through explicit verified identities; do not automatically merge by
matching company name, GST or email. Preserve recovery, forced temporary-password
changes, audit trails and immediate revocation.

Keep the preserved Python calculator service and financial engine. A common Node
portal may call its secured API. Rewriting tested CN financial logic into Node is
not required for one login or subscription management.

## What was actually checked

Earlier project context identifies the Hostinger plan as Cloud Startup; current
billing status, renewal dates and account-specific credits have NOT been inspected.
Hostinger's published programming support says Python is supported on VPS rather
than Web/Cloud hosting. Its upgrade guide says Web/Cloud cannot be directly
upgraded to VPS; a separate VPS purchase and manual migration are required.
A larger Cloud tier therefore does not solve this Python hosting requirement.

Official sources checked:
- https://www.hostinger.com/support/which-programming-languages-and-frameworks-are-supported-at-hostinger/
- https://www.hostinger.com/support/1583459-how-to-upgrade-a-hosting-plan-at-hostinger/
- https://www.hostinger.com/support/4334278-how-to-use-hostinger-balance/

Unused Cloud payments are not assumed to become VPS credits. Eligible refunds
can be credited to Hostinger Balance, but eligibility or discretionary account
credit must be confirmed with Hostinger using the actual subscription details.
No purchase, cancellation, support message or live hosting change was made.

Read-only inspection of spideraistudio/sellers-trust, Meet-Dev:
- package.json: Next.js / Node and a MongoDB dependency.
- lib/runtime-env.ts: MongoSqlDb and MongoDB-backed file objects.
- app/chatgpt-auth.ts: a separate administrator session cookie and credential
  version/session validation. Do not equate this platform-admin login with a
  customer's company admin login.

This differs from the earlier MariaDB deployment description. Before integration,
identify the exact deployed commit and database; do not migrate the old described
stack or infer that this branch matches sellerstrustnetwork.com's live build.
Source references:
- https://github.com/spideraistudio/sellers-trust/blob/Meet-Dev/package.json
- https://github.com/spideraistudio/sellers-trust/blob/Meet-Dev/lib/runtime-env.ts
- https://github.com/spideraistudio/sellers-trust/blob/Meet-Dev/app/chatgpt-auth.ts

## Hosting choices and recommended order

1. Keep STN on the existing Cloud plan and add a Hostinger VPS for Python CN.
   One login remains possible across the two services. This has the smallest STN
   migration scope, but leaves two hosting subscriptions to manage.
2. Stage both services on a single Hostinger VPS, then migrate STN after acceptance.
   This is the long-term recommendation for one hosting environment supporting
   Node, Python and the actual STN database. VPS is self-managed: explicitly
   arrange updates, restart/monitoring, TLS, backups and demonstrated restore.
   Select capacity after measuring PDF/concurrent-user load and storage growth;
   do not buy solely from the current per-user quota figures.

Keep the live Cloud site operating while staging. The existing domain can stay;
its DNS/routing changes only at the approved cutover. Verify and protect any email
or other websites on the current plan before deciding whether it can be cancelled.
No public cutover until common identity, permission/isolation, quota/concurrent PDF
load, full existing workflows, backup restore and rollback have passed staging.

Implementation order: pin deployed STN source/database → define company and user
identity mapping → shared identity/module API checks → common two-card portal →
subscription records → private staging → migration rehearsal/restore → approved
cutover. Keep the calculator's existing local login usable during development.
