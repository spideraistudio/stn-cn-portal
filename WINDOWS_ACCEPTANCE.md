# Public visitor UI acceptance — pending

The user accepted the preceding case-number/rate-precision update on Windows. For this new release, follow PUBLIC_VISITOR_UI_HANDOFF.md and test /home, /join and /portal in a signed-out window, both themes and your usual zoom. Check validation/retained details, pending success, duplicate prevention, administrator approval, issued credentials/permissions and first login. Reopen existing saved work. No deployment or live migration.

# UX Phase 5 acceptance

The current complete setup and acceptance checklist is START_HERE_WINDOWS.md. All native Windows acceptance remains pending. The Linux browser checks for Phases 3–5 now passed; older pending-Linux notes below are historical.

# Windows acceptance — not yet performed

Use a fresh local setup or explicitly copied test data, never the live application. Read INTEGRATION_README.md first.

- [ ] Setup/start/restart on Windows; original applications remain usable separately.
- [ ] Platform individual login → two module cards; switch CN/STN without another login; shared logout.
- [ ] New company admin: 1024 MiB own allowance, five users, 250 MiB per user. Sixth user refused. Superadmin can change limits.
- [ ] Company admin can manage/reset only its own users and cannot access the STN platform dashboard/review APIs or another person's CN workbook/PDF.
- [ ] Company module/subscription settings and independent user CN/STN switches. An already open tab loses disabled access immediately; re-enable requires a new sign-in after session revocation.
- [ ] Temporary password forces a change; company-scoped reset revokes both modules. Superadmin can reset company admins.
- [ ] Explicit STN member lookup shows the expected company/status; invalid or cross-company member links fail; grant the approved company membership explicitly to staff; no automatic linking by GST/email/company name.
- [ ] Original CN PDF import opens Check Ledger directly. All five steps clickable. Known mappings reused; optional segments assigned separately; saved party reopens after restart.
- [ ] Navy Studio after login; Classic Emerald option; ABS/CD diagrams, product card shares, dragging, empty-canvas left pan, cursor-focused zoom and saved layouts.
- [ ] ABS/CD/outstanding rules, separate rounding, IPT and late IPT, late Kharif entries, April–March Year Link; finalise/issue once; reports, NRV exclusions, CSV and compact/detailed print.
- [ ] Billing Rate Audit: periods, wrong sale, return against selected original bill, split references, review notes and reopen. This and direct audit mapping still need new Windows acceptance.
- [ ] Run Ledger Checks → click unmapped product → prefilled source details → map/save/recheck; missing packing remains blank; source dates/amounts and existing frozen CNs stay intact.
- [ ] CN quota rejection/retry, simultaneous uploads and usage meter. STN storage shows separately and does not reduce CN allowance. Temporary cleanup preserves saved/protected work.
- [ ] STN approved-member/category behavior, seller report submission/review/GST search; seed request, state/Pan India scope, anonymous buyer, quotation, approval/contact exchange, completion/history.
- [ ] Separate account migration rehearsal on copies; no name/GST/email merge. Independent project export/import preserves original work and frozen history.
- [ ] Restart both local services and reopen both modules. Stop and back up all test data and keys; rehearse restore before any later live migration.

Record Windows results with date, package version, failed step and exact message. Passing Linux tests do not check Windows installation, native PDF printing, animation/interaction feel or the user's actual statements.

## Staff storage form update — pending

- [ ] STN Company Users and Account create/edit forms show the granted maximum and block 2560 MiB for a 250 MiB ceiling; valid maximum saves.
- [ ] Superadmin can increase the ceiling; after reload the company admin sees and can use the updated maximum.
- [ ] Existing accounts, CN work and module switching remain usable.

Previous update: user reported successful account creation on Windows. This is not full Windows acceptance.

## UX Phase 1 — pending

Use the Windows checklist in PHASE1_WORKFLOW_HANDOFF.md during final acceptance. Linux verification does not mark these user checks passed.
