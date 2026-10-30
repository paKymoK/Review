---
description: Re-verify open debt of a service against current code
argument-hint: <service> [repo-path | list of files]
---

Sweep technical debt for: $ARGUMENTS

1. Read `services/<service>/techdebt.csv`. Select items with status `Open` or `Partially fixed`. Oldest first.
2. Get current code only from what the owner supplies: a local repo path (read the files at the item's `location`), attached files, or pasted code. If nothing is supplied, list the items and the files you need, then stop.
3. For each item decide, from the current code only:
   - `Fixed (verified)` – the problem is gone; cite file:line
   - `Partially fixed` – say what remains
   - `Open` – still present; cite file:line
   - `Obsolete` – the code no longer exists or was rewritten
   - leave unchanged and write `Unverified` in the reply if the file or line cannot be found
4. Update `techdebt.csv` (`status`, `last_checked`, `last_checked_mr` = `sweep-<today>`, `times_seen` +1, `evidence`) and append `history.csv` rows for every status change. Do not touch `touched_not_fixed` in a sweep.
5. Run `python scripts/export_excel.py services/<service>`.
6. Reply with counts per result, the oldest items still open, and what could not be verified. Do not commit unless asked.
