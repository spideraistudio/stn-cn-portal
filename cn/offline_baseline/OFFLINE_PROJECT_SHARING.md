# Offline project sharing and storage maintenance — cumulative Update28

## Sharing workflow

Each person runs their own offline calculator. Open Settings → Share & Open Work → Review & Export Project. The preview shows parties, workbook stores, calculations, completed work and archived records. Enter a project label and optional sender name; download the `.cnwork` file and send it through your chosen channel.

Both people should use a calculator version that supports .cnwork sharing. The recipient uses Settings → Share & Open Work → Open someone else’s work. Review the sender, project, date and counts, then choose Open New Separate Copy. The sidebar shows Received, its project name and sender. Switch back to My Work to resume your own data.

The recipient can edit draft calculations, create revisions of completed calculations, and export the received project back. Frozen finalised/issued records are preserved exactly. Existing receipt dates, source evidence, payment allocations, settings versions, issued totals, Year Link provenance and bulk-review queues travel with the project.

The export includes the **entire selected project**, including all its workbooks, parties, histories and deleted records. It excludes every other project. This deliberately preserves cross-workbook issue and traced-receipt safeguards. It is not a single-party export. Review the counts before sending. Export files are compressed data files, not password-protected files.

Import never merges or overwrites projects. Reimporting the same file creates another independent local copy. There is no automatic reconciliation of changes made by two people in separate copies; use an agreed handoff order and return the updated file.

Use Backup & Restore for recovery within the selected project. Use Share & Open Work for received files. A backup includes all workbook stores **in that project**; other received projects have their own backups/exports. Startup returns to My Work.

## Why separate projects

GnuCash documents separate data files for finances that must remain separate. QuickBooks Desktop documents restoring to a separate folder or unique filename to avoid overwriting existing company data. This implementation follows that separate-file pattern, applied to the calculator’s whole project rather than just a workbook.

- https://wiki.gnucash.org/docs/C/gnucash-guide/basics-files1.html
- https://quickbooks.intuit.com/learn-support/en-us/help-article/back-data/restore-backup-company-file/L2FptZyV1_US_en_US

A new workbook alone is insufficient here: reports and duplicate-issue checks span workbook stores. Received projects therefore have separate SQLite roots, workbook registries, settings, reports, import queues and issue checks. Requests carry a project header; opening one tab does not switch another tab’s server context. Changing projects saves the current draft and clears temporary audit/PDF/report/mapping views.

Portable files contain only `manifest.json` and `work.json`. Import reads those fixed names without extracting paths, checks the format/version, checksum and size limits, validates by restoring in a temporary isolated directory, and registers a fresh project identity only after successful validation. The checksum detects corruption; it is not sender authentication. Invalid imports do not change existing project databases.

## Cleanup and permanent deletion

Settings → Storage & Delete → Scan Storage shows regenerable Python cache, unused SQLite pages and known restore safety copies. Review Cleanup removes cache and compacts project databases. Recovery backups remain unless individually selected; removing them requires typing DELETE BACKUPS. Original PDFs/source evidence, live ledgers, settings, .venv, exported files and updater backups are not treated as cache.

Already-deleted parties, schemes and workbooks have a Permanently Delete action in their deleted lists and on the storage page. Preview the target and counts, then type its exact name. Stale previews are rejected. SQLite compaction follows deletion to reclaim space.

- Parties: removes their archived calculations, corresponding record audit copies and linked bulk-review rows. Other calculations that reference those records block removal.
- Schemes: removes an unused archived scheme and exclusively owned product definitions from settings history; independent frozen snapshots remain unchanged. Saved calculation references or other schemes sharing the product group block removal.
- Workbooks: removes an archived private workbook database, registry entry and its dedicated automatic recovery copies. Existing calculations is not deletable as a workbook.
- Issued CN history, prior-issued revision history and their duplicate-issue safeguards cannot be purged using party/workbook deletion. Keep these archived.
- General backups and files previously exported may still contain removed data. Manage known safety copies explicitly in Storage Cleanup; user-selected exported files and updater backups are managed outside this cleanup screen.

No live user data or PC folders were deleted during development. Verification uses temporary databases only. Windows native/browser visual acceptance remains pending; the automated UI checks use a simulated DOM with a real isolated API.
