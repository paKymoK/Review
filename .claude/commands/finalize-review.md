---
description: Turn the owner-edited review.md into CSVs, update the debt register, export Excel
argument-hint: <service> <review-dir e.g. 2026-10-30_MR-123>
---

Finalize a review: $ARGUMENTS

The edited `review.md` is the truth. Follow `docs/review-flow.md` step 7.

1. Read `services/<service>/reviews/<review-dir>/review.md` completely. Anything the owner deleted is not logged and not changed.
2. Write, to match the file exactly:
   - `findings.csv` – every finding block (fix-now and new debt). `debt_id` is filled for debt items after step 4.
   - `debt_check.csv` – every row of the "Kiểm tra nợ cũ" table.
   - `meta.json` – service, MR, date, reviewer, risk tier, verdict and reason.
3. Update `services/<service>/techdebt.csv` for each `debt_check.csv` row: new status, `last_checked`, `last_checked_mr`, `times_seen` +1, `touched_not_fixed` +1 when the file was touched and the problem remains, and an `evidence` line (MR, file:line). Items not touched in this MR keep their status, with `last_checked` unchanged.
4. Append new debt (`D1, D2, ...` blocks and any `DEFER:` lines) as rows with the next free ID `TD-<service>-nnn` (never reuse an ID). Set `first_seen`, `first_seen_mr`, `times_seen = 1`. For `DEFER:` fill `deferred = yes`, reason, mitigation, approver, sprint. If a security or data-loss item is deferred without `duyệt bởi`, stop and ask the owner.
5. Append one `history.csv` row per status change and per new item.
6. Run `python scripts/export_excel.py services/<service>/reviews/<review-dir>` and `python scripts/export_excel.py services/<service>`. Fix any error and rerun.
7. Reply with: items fixed, items still open, new debt IDs, deferrals logged, and anything that needs the owner's decision. Do not commit unless asked.
