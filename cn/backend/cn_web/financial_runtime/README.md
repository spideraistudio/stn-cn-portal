# Financial runtime extension

`engine.py` starts from the preserved Update35.2 engine. It adds protected prior receipt sources, their independent earlier-dues clearance, gross opening-dues bounds, non-overlapping unreserved credit and crop/provenance validation. No CN benefit formulas are changed. Original files remain under `cn/offline_baseline` and retain their manifest hashes.

`prior_payments.py` reconstructs reviewed receipt availability from owned PDF evidence. Normal receipt dates, accounting entries, original balances, rounding and scheme rules are preserved. Canonical statement references are resolved by `native_interface.py`; clients cannot replace this proof through Save. Source edits require normal import/review. Reservations and late-CN approvals are checked across the owner's saved workbooks and issued lineages.

Baseline engine SHA256: 237984ca2f7657667801c1341f0070aecf6ecdb31113b691efc51cf623e7edc0
