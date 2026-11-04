# Release candidate: CN accounting and compact offline setup

Base: fix/combined-portal-production at deb6eb9c95994056433fa2c441f540530f0ad4e7.
Candidate: release/cn-accounting-readiness-2026-11-03.

This is preparation for review/staging, not live deployment or blanket financial certification. Production HTTPS factories, secure cookies, separate identity service, persistent paths, secrets, Caddy/systemd and backup/rollback controls are retained. No live data, private PDFs, credentials or runtime dependency trees belong in this branch.

## Changes

- Workbook-wide product mapping and calculation periods on Parties; creation without dates; period opening from earlier activity and period closing from selected activity.
- Reference-aware, chronological old-dues clearance; original-date advances and shared remaining-receipt budgets across calculations/workbooks; review gates for unclear references and same-day CN/receipt ordering.
- Posted CN now has an explicit manual choice: same app-issued CN now entered in Tally, or separate CN. Drafts with potentially overlapping issued history must choose; matching cannot exceed known issued balance in that calculation. This is reviewed classification, not automated Tally integration/document matching. Separate CNs deduct additionally, same documents once. Old frozen proof reproduces without silent reclassification.
- CD remains payment-based: 100000 cash + 8000 CD settles 108000 where eligible value permits. Other ABS/quantity/cash/rounding and cap rules are retained.
- Direct product mapping/status, selected-period scheme visibility, exact indexed quota counting, lighter navigation and render-local derivations.
- Compact Windows setup builds in temporary storage and retains a traced runtime. Production systemd retains its existing Next launch layout for compatibility; offline compact setup is not silently substituted on the VPS.

## Validation

Fresh results are recorded in the PR/readiness update. Local production-boundary tests, broader CN/account tests, preserved financial regression and explicit CN matching tests passed. Private fixtures absent from this checkout are reported as skips, not passes. The production build passed compilation and TypeScript. Local HTTPS smoke and GitHub checks must be checked before approval; historical verification files alone are not current acceptance evidence.

The dependency-install attempt was slowed by downloading the optional development Chromium package; app build used the installed locked application dependencies. A clean complete npm ci and build is required in GitHub checks/staging. No dependency versions were changed as a workaround.

GitHub Actions verifies only, with read-only repository permissions and no VPS secrets or deployment steps.

## Remaining staging/live gates

Verify the actual deployed commit AND manual/uncommitted server changes, including the reported forwarded-IP behaviour. Inspect actual OS, Node/Python/Mongo versions, service configuration, readiness and disk headroom. Repository state alone cannot prove current host state.

Take a coherent verified backup and rehearse restore in a separate private staging environment. Preserve lookup/bridge keys and existing accounts; never run fresh configure/bootstrap or copy desktop integration-data over the live site. Measure byte-index initialization against a staging copy of real data.

Test permissions/account isolation, imports/mappings, overlapping views, cross-workbook payment budgets, both posted-CN choices, review expiry, old/new saved and issued history, STN reports/Buy-Sell, both themes, concurrency and restart. Older unissued frozen results with newly unclear evidence may need a draft revision before issue. Review legacy ambiguous drafts; do not silently trim or reclassify them. Windows setup/printing and exact Windows disk size remain separate pending acceptance.

To PREPARE an approved candidate in the reviewed server checkout (does not activate):

```bash
sudo bash deploy/prepare-release.sh FULL_REVIEWED_COMMIT_SHA release/cn-accounting-readiness-2026-11-03
```

The explicit branch is validated and commit ancestry checked. The old production default remains compatible. Activation uses the existing separate owner-approved backup/release/rollback process. Do not merge/activate until checks and staging acceptance pass.
