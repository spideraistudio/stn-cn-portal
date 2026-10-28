# Public registration/navigation audit — 28 October 2026

The resumed workspace had reverted to its pre-audit checkpoint; this pass restored and retested the public changes.

## Fixes
- Preserved recovered registration API fix: malformed JSON responds with 400, bounded-body failures preserve 400/413 rather than a generic 500.
- Public Home links now use full-document anchors in About, Contact, FAQ, public header, legacy landing navigation, legal pages and registration success. The combined gateway reserves `/` for the shared portal and maps `/stn` to the Next root. Next client routing can canonicalize Home to `/`; anchors preserve `/home` → `/stn` gateway routing.
- Public browser tests now expect `/stn` and actual landing heading, rather than the intermediate redirect route `/home`. Added click checks for FAQ/legal/header/success in addition to About/Contact.

## Verification
- Twelve isolated registration tests passed: malformed, null, array JSON; declared and streamed oversize; required company; GSTIN, mobile, email, other category; one valid save; honeypot no-save.
- The VM harness now injects host JSON alongside host SyntaxError to avoid cross-realm false negatives.
- Targeted public page/API/component/test ESLint and browser-script syntax passed.
- Rendered public registration → approval → forced password change and both-theme checks are part of root's coordinated full-stack run. This report does not claim its outcome before root completes it.

No live data, credentials, deployment or original repository changed. Windows and production hosting acceptance remain pending.
