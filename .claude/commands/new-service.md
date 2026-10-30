---
description: Create a service folder from templates
argument-hint: <service> <High|Medium|Low> [repo-path]
---

Create a new service in this workspace for: $ARGUMENTS

1. Parse `service`, `risk_tier` and the optional `repo-path`. If the tier is missing, ask the owner once.
2. Refuse if `services/<service>/` already exists.
3. Create:
   - `services/<service>/service-profile.md` from `templates/service-profile.md`, with `service`, `risk_tier` and `repo_path` filled in
   - `services/<service>/problem.csv` and `history.csv` copied from `templates/` (header row only)
   - `services/<service>/reviews/.gitkeep`
4. If `repo-path` is given, read the repo's README and build file to fill in "Mô tả ngắn" (Vietnamese). Mark anything you could not confirm as `chưa xác nhận`.
5. Run `python scripts/export_excel.py services/<service>` so an empty `problem.xlsx` exists.
6. Tell the owner which fields in `service-profile.md` still need their input. Do not commit.
