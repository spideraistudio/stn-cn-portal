# Phase 7.1 — delegated accounts and navigation

Cumulative from the Phase 7 Windows-tested release. No hosting deployment.

## Acceptance record

The user confirmed the four Phase 7 storage checks, then the remaining workflow
checklist as “all ok”. Thus Phases 3–7 now have user-reported Windows acceptance,
alongside Phase 2. Phase 7.1 adds new hierarchy/default-theme/panning behavior;
these additions have automated evidence and require a new targeted Windows check.
Prior handoff statements about pending earlier acceptance are historical.

## Hierarchy

The original bootstrap administrator becomes the sole superadmin automatically.
Existing credentials, IDs, saved work, quotas and permissions remain. Other legacy
admins become delegated admins under superadmin. Legacy users remain directly
managed by superadmin until explicitly assigned using Edit access → Managed by.
No users are silently grouped or granted access to anyone else's work.

Only superadmin can create admins, assign/reassign users between admins and change
admin management limits. New admin defaults: 1 GiB (1024 MiB) own allowance, five
users and a 250 MiB per-user default/ceiling. User allowances are separate from
the admin's allowance. Superadmin can customize these values, including granting
or revoking Can manage own users. Existing quotas are never overwritten by defaults.
Only the superadmin is protected from disabling; disabled admins and all their
users lose sessions. Re-enabling never restores revoked sessions.

Admins list/manage/reset only their own users, cannot create admins, modify peers
or superadmin, move users, change their own limits, grant financial permissions
they lack, or raise a user's allowance beyond the delegated ceiling. A new user
slot is reserved by BEGIN IMMEDIATE; all assigned users including disabled ones
count, so concurrent creation and disable/recreate cannot bypass five users.
Superadmin may reassign a user directly to itself to release an admin slot.
Lowering a user-count ceiling retains existing users and blocks additions.
Lowering an admin's delegated user-storage ceiling changes future/admin-managed
allowance changes; it never deletes data or silently rewrites existing quotas.

User effective financial permissions are intersected with the parent admin's
current permissions at every server authorization. Revoking an admin's grant
therefore removes that capability from their users immediately. Users remain
independent data owners; management grants never confer ledger/PDF/workbook
access. Admin audit views are limited to their own activity and current children;
superadmin sees the account audit across the installation. Account-role metadata
is security metadata, not part of interchangeable financial project archives.

## Password recovery

Own-user forgotten password: admin or superadmin sets a temporary password using
Edit access → Reset password & revoke sessions. Admin forgotten password:
superadmin does the same. Old sessions are deleted atomically; temporary login
requires choosing a different password before any workspace/management action.
Credentials are hashed and never included in audit details or backups in cleartext.
Reset never replaces the user's identity or touches saved financial data.

Superadmin forgotten password: stop the local server and use
Recover_Admin_Windows.bat (custom data argument remains supported). Only the
superadmin is eligible in that operator tool; it verifies a full database backup
before changing the password and revoking sessions. Keep its backup protected.
This relies on trusted access to the PC/server files, not a public recovery URL.
For future hosting the same Python operator tool can run through a protected
server console; securing operator access and off-server backup is a Phase 8
acceptance requirement. No email/SMS recovery or public reset endpoint was added.

## Appearance and panning

New authenticated sessions default to Navy Studio and normal login opens the
calculator after any required password change. Users can still choose Classic
within their session. Appearance selection is session-scoped, so next login
starts Navy; saved Classic/Navy card-layout rows are retained independently.
No financial scheme/settings/date/engine changes. First-time temporary-password
login stays on the account page until the user changes it and signs in again.

Navy empty-canvas left-button drag pans camera X/Y at any zoom, including with a
locked card layout. Card dragging remains separate, and camera movement changes
neither node positions, allocations nor saved layouts. Pointer release/cancel,
lost capture and blur stop panning; theme changes reset transient camera state.
Classic retains its original scroll-based background panning. Wheel zoom stays
cursor-anchored. Updated UI files live only in the web adapter; all 140 preserved
Update35.2 baseline files and the original calculation page renderers are intact.

## New Windows checks

1. Existing login says superadmin in Account; old parties/workbooks remain.
2. Create admin: default 1024 MiB, maximum five users, 250 MiB user ceiling.
3. Admin creates five users; sixth is refused. Another admin cannot list/manage
   them. Only superadmin can change the admin's limits or assign users.
4. Reset a test user's password as its admin, then an admin as superadmin. Old
   sessions fail; temporary login forces password change; saved data remains.
5. Choose Classic, log out, log in: calculator starts Navy. Zoom, drag blank
   canvas vertically/horizontally, then drag a card. Reopen saved layouts.

See verification/hierarchy_* for actual automated results. No production security
certification or new Windows acceptance is inferred from those checks.
