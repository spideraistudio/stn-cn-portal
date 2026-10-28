# STN + All Crop CN Portal

Independent combined application source, prepared for a new private repository under meetpatelhmt-dev. Original Meet-Dev and sellers-trust-buy-sell repositories are not modified. This repository is not deployed.

## Start locally on Windows

Read START_HERE_WINDOWS.md. Install the prerequisites, then run Setup_Combined_Windows.bat, Start_Local_Mongo_Windows.bat and Start_Combined_Windows.bat. Create the platform administrator using the interactive setup prompt; never commit credentials or integration-data. Open http://127.0.0.1:8787/home for visitors and /portal for shared access.

A fresh profile has no projects, workbooks, parties, files, catalogue, saved mappings, schemes, approved rates, allocations or history. The first CN screen asks the user to create a workbook with their state and season dates. That workbook contains no reference products or schemes. Import a supported statement, map the user's products and packing, then create and confirm the user's scheme. Sample-party buttons are removed. New blank workbooks are also empty; explicitly copying one's own existing workbook remains a separate action.

Saved workspaces are loaded intact. This change does not erase, reset or migrate any existing account's catalogue, schemes, allocations or frozen history. Do not delete an existing integration-data folder to update an installation. Back up the complete stopped data directory, including keys, before updates.

## Current scope

Includes the public visitor/registration UI, administrator approval and module permissions, private CN workspaces, storage ceilings, five UX phases, temporary/permanent case-number history, billing-rate precision fixes and multi-company text statement adapters. The requested unknown-packet-weight/per-packet calculation enhancement is still pending; it is not implemented by this clean-start change. See CLEAN_START_HANDOFF.md and MULTI_COMPANY_STATEMENT_HANDOFF.md. Native Windows acceptance and internet production readiness remain pending.

## Tests

Use the Python dependencies installed by setup. From the repository root on Linux:

```
PYTHONPATH=cn/backend:cn/offline_baseline:cn/tests python -m unittest test_clean_profiles -v
python cn/verify_baseline.py --allow-private-fixtures
```

Use `;` instead of `:` in PYTHONPATH on Windows. The original baseline code and tests remain unchanged. Seven private source-statement PDFs are deliberately excluded from Git, and fixture-dependent legacy tests require those files supplied privately. Synthetic PDFs in cn/tests/fixtures are tracked. Do not commit customer statements to run tests. The optional test_multi_statement acceptance also requires separately supplied private samples; it is explicitly skipped without CN_MULTI_STATEMENT_DIR.

Real-browser clean-profile verification is available in cn/tests/run_clean_profiles_browser.py with Playwright, a compatible Chromium runtime and CN_BROWSER_EXECUTABLE/CN_SCREENSHOT_DIR where required. Screenshots stay outside the repository. Earlier financial, STN and public registration verification records are historical, not proof of internet deployment.

## Future releases

Work on feature branches, test on disposable data and staging, then release reviewed versions. Keep live databases, keys, backups, uploads, statements, generated dependencies and runtime caches outside Git. New statement adapters should affect new imports or deliberate user re-reading, and must not silently rewrite saved calculations. Production hosting, HTTPS, backup/restore, migration and rollback validation are separate work.

## Combined portal audit branch

See FULL_AUDIT_HANDOFF.md for verified fixes and current limits. `npm start` starts STN only. The complete combined runtime requires Python and persistent storage. This branch is not yet a production deployment package for Hostinger Node.js web hosting. Do not point the local-only launcher at a live database.
