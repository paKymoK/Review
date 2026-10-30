# Code Review Workspace

Claude Code reviews merge requests for ~20 Java Spring Boot / ReactJS services and keeps a per-service technical-debt register. Everything is plain files in Git, so it can be reviewed from anywhere that can open the repo.

Claude reads `CLAUDE.md` automatically when started in this folder.

## Daily use

1. **Draft:** `/review-mr <service> <MR id> <diff source>` → Claude writes `services/<service>/reviews/<date>_MR-<id>/review.md` (Vietnamese). It also re-checks old debt against the diff.
2. **Owner edits:** open `review.md` anywhere (Git UI, IDE, phone), delete items that need no action, mark deferrals. Removed items are not logged.
3. **Finalize:** `/finalize-review <service> <review-dir>` → Claude syncs the CSVs, updates the debt register, and regenerates the Excel files.
4. **Commit** the result. Managers read `techdebt.xlsx` (Summary and Backlog sheets). Developers only read `review.md`.

Other commands: `/new-service` (add a service), `/debt-sweep` (refresh old debt from current files).

## Setup

```bash
pip install -r requirements.txt     # openpyxl, for Excel export
```

## Editing the rules

- What gets reviewed: `criteria/*.md` (shared) and `services/<service>/service-profile.md` (per service).
- How it works: `docs/review-flow.md`.
- Instructions Claude follows: `CLAUDE.md`.

Commit changes to these files like any other code; the next review uses them.

## Notes

- `services/example-service/` is sample data. Delete it when you add real services.
- Excel files are generated from CSV. They diff poorly in Git, so review the CSV or `review.md` for changes.
- Formulas calculate when the file is opened in Excel. Some web previewers show blanks until then.
