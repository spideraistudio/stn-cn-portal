# Authentication and sign-out audit — 28 October 2026

All tests used disposable local data. No live account, repository or deployment changes.

## Fixes reviewed

The STN shared navigation now checks session and logout responses, prevents repeated submissions, shows retryable failures, and redirects only after logout succeeds or the session is already expired. The shared portal clears signed-in controls on a 401 response and guards duplicate logout requests. These fixes were recovered from the previous checkpoint; this pass required no further application edits.

## Verification

- `python3 integration/test_portal.py`: **24 tests passed** in 36.859 seconds. Covers login, password change, logout/all, session expiry/revocation, CSRF/origin/content safeguards, hierarchy, permissions, individual data isolation, module access and storage limits.
- `python3 integration/run_auth_audit_browser.py`: **8 browser scenarios passed**, with no uncaught browser exceptions:
  1. Logout server error retains session, displays retryable error, and does not navigate.
  2. Network-aborted logout retains session and permits retry.
  3. Session-check 503 prevents a false sign-out redirect.
  4. Keyboard logout shows disabled busy control, issues one logout request, revokes session and shows login.
  5. Already-expired session returns to sign-in.
  6. Account login to portal and portal logout revoke the shared session.
  7. Account logout-all revokes session and restores login.
  8. Session revoked elsewhere restores login instead of leaving signed-in controls visible.

The STN component fault checks render the actual PortalSwitch in an isolated harness against a real disposable Python account server. Portal and account tests use their actual pages. Browser runtime used browser-runtime/chromium with test-fonts.conf. Two browser regression cases (network abort and session 503) were restored in integration/browser_auth_audit.cjs.

Evidence: verification/four_agent_auth_portal.txt and verification/four_agent_auth_browser.txt.

Linux/local verification only. Windows acceptance, production HTTPS deployment and a comprehensive security audit remain outside this result.
