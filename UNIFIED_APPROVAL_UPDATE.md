# One-form signup approval and user access — 24 October 2026

Install this update into the existing STN_CN_Integration_Local folder. Your existing logins, CN work and MongoDB data are retained. No dependency reinstall or new administrator setup is required.

## Install
1. Close both the combined-app and local MongoDB command windows.
2. Extract STN_CN_Unified_Accounts_Update.zip and copy its contents into the existing application folder. Choose Replace files.
3. Run Start_Local_Mongo_Windows.bat and wait for MongoDB ready.
4. Run Start_Combined_Windows.bat. On first start after this update it builds the STN frontend; keep the window open until the application address appears. Later starts reuse that build. Open http://127.0.0.1:8787/portal and sign in with your existing platform account.

The update includes the Windows Mongo startup correction. No integration-data, passwords or databases are included in the ZIP.

## Approve a signup
Open STN → Member Company → the signup request. The **Approve & create account** form now contains:
- Individual username and temporary password.
- CN Calculator and/or STN access.
- CN permissions and own storage allowance (admin default 1024 MiB).
- Maximum users (default five), per-user allowance ceiling (default 250 MiB).
- Plan and optional subscription start/expiry.

Click **Approve & create account** once. It creates the company, company administrator, permissions and explicit link to THAT signup's STN membership. It never guesses a match by name/GST/email. The person signs in once, changes their temporary password and sees only the granted applications. CN-only approval does not enable STN access.

Record the temporary password privately before submitting. The password field is cleared on success. No passwords are included in logs or audit details.

If a network failure interrupts approval, retry from the same member page using the same username, password and settings. A prepared account remains disabled until approval completes. The same request cannot create duplicate accounts. For an existing linked account use Edit existing user access; approval does not overwrite its identity or financial work.

## Company staff and existing users
Platform superadmin: STN → CN & company management. Create the staff username/password, select its managing company admin, CN/STN switches, financial permissions and allowance in the same form.

Company admins with STN: **Company users** in the member sidebar. They can create only their own staff within the granted permissions, seat/storage limits and linked company membership. CN-only company admins can use Account & permissions; its staff creation form now includes CN/STN switches too.

The same management page contains **Edit existing user access** for enable/disable, module switches, permissions, allowance and an optional temporary-password reset. Those edits are transactional and revoke affected sessions. Password changes/reset do not delete work. Company admins cannot approve platform memberships or manage another company's users.

Advanced company subscription/assignment settings remain accessible through the existing management link. Manual legacy administrator creation remains available in Account for compatibility; the normal company signup route is the new approval form.

## Security and recovery
New company/account/permission/link preparation uses one SQLite transaction. MongoDB approval and identity activation use a recoverable sequence: prepare disabled account → approve exact membership → activate. A failed intermediate step never creates an active half-configured account. Retrying changed grants is rejected; Edit access is required instead. CN ownership and stored financial history are unchanged.

The local launcher now uses the production frontend, avoiding development hot-reload dependencies. Its local shared-session cookie is explicitly configured, so both modules still use the same login. It automatically rebuilds when frontend source changes.

The STN nonce proxy now passes its CSP to the Next.js render request as well as the browser response. This lets framework hydration scripts receive the matching nonce; it does not allow unsafe-inline scripts. This also fixes pages displaying while interactive controls remain inert.

## Verification
- Four targeted unified-account tests: disabled preparation, idempotent retry, activation/forced password change, invalid-term rollback, CN-only/staff grants and rollback of a failed access edit.
- 24 existing portal/account tests passed after the transaction changes.
- TypeScript, targeted ESLint and optimized Next build checks recorded under verification/unified_*.
- Original 140 Update35.2 baseline hashes retained. No financial engine changes.
- Actual signup approval, staff creation and existing CN/STN workflows are checked by the included Linux browser/API journey. Windows acceptance of these additions remains pending; test the signup-request form on your PC.
