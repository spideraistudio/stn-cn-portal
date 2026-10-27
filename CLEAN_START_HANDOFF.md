# Clean new-profile source — 27 October 2026

Prepared from STN_CN_Multi_Company_Statements_Source_Handoff.zip for a separate private stn-cn-portal repository. No original GitHub repository, deployment or live data was changed. GitHub remote creation is pending: the available GitHub connection can modify repositories but cannot create one. A local main branch and initial source commit are prepared for publication after remote creation.

## Changes

The authenticated Runtime now always installs clean settings for a workspace with no saved calculator payload. Default products and schemes are empty. An unconfigured workbook has a neutral, unconfirmed Working season with no dates; ordinary first-workbook onboarding saves the user's chosen season. A catalogue explicitly saved by the user produces only its own unconfirmed placeholders, with no benefit rates, billing amounts or payment windows. New blank workbooks also discard inherited audit/rate/configuration metadata. Explicit copy mode remains available for a user's own configured workbooks.

A supplied existing calculator payload still loads every settings version and every stored table intact; no clean-start migration runs on old data. Existing permissions, account isolation, quotas, source originals, saved corrections, frozen history, all financial formulae and the original engine source are unchanged. Demo/reference buttons are removed from the authenticated dashboard and new-calculation page. The protected offline baseline retains its original code for regression comparison; that separate legacy developer server is not the combined application's production entry point.

Git ignores private original PDF fixtures as well as runtime data, keys, database files, environment files, dependencies and archives. Seven private legacy PDFs are omitted from tracked source; all protected code remains unchanged. cn/verify_baseline.py gains --allow-private-fixtures, permitting only those seven named missing fixtures, and continues to enforce all other hashes. Historical source manifests describe their historical releases. README is current; historical handoffs are retained for provenance. Source code reference templates used by tests/internal shape construction are not imported into fresh users' settings.

## Verification record

- verification/clean_profiles_tests.txt: five focused tests for empty defaults; exact existing-payload preservation including issued history; user-only placeholders without benefits; two new independent profiles with no saved objects and server-side cross-user denial; a blank workbook created beside configured work without changing the original.
- verification/clean_profiles_statement_tests.txt: five importer/review tests, including all three actual private statements and their reconciled totals, saved/repeated import, missing-page rejection, ownership, finalisation blocking and independent project transfer. The PDFs are not committed.
- verification/clean_profiles_browser.txt: real Chromium first-workbook form, empty dashboard/settings, no sample actions, reload persistence and both themes; no page errors. Screenshots were inspected internally and not committed.
- verification/clean_profiles_baseline.txt: all 140 baseline files match locally; seven private PDF inputs are ignored by Git. A clean tracked export is separately checked with --allow-private-fixtures.
- verification/clean_profiles_regressions.txt: all 59 combined-account CN regression tests passed.

The focused test harness initially required correcting its setup delegation and using the saved period when entering test-only reference settings. Those were test-fixture corrections. No deployed database or original repository was touched. Windows acceptance remains pending. Production deployment readiness and unknown packet-weight schemes remain pending.

## Publish the prepared source

Suggested private remote: meetpatelhmt-dev/stn-cn-portal. Do not push to sellers-trust-buy-sell or original Meet-Dev. The remote has not been created by this preparation. Use main for the initial reviewed source; do not enable automatic deployment yet. The GitHub connector lacks a repository-create action, so remote creation requires an approved browser fallback or the owner creating the private repository and sharing its URL.
