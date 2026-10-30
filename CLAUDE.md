# Code Review Workspace – instructions for Claude Code

This repo is the working area for reviewing merge requests of ~20 Spring Boot / ReactJS services and tracking every problem found (fix-now findings and technical debt) in one register. You are the reviewer's assistant. The owner makes every decision.

## Hard rules

1. **Write all review output in Vietnamese** (review.md, notes, evidence, Excel content). Keep English technical terms (`@Transactional`, N+1, Kafka, ...). Instruction and criteria files in this repo stay English.
2. **Judge only the diff.** New and changed code is held to the criteria. Untouched old code is not reviewed; if you notice a real problem there, log it as `Existing-untouched` debt, never as a reason to block.
3. **Never assert what the diff cannot show.** Function bodies not in the diff, Feign/DB/Kafka/gateway config, other services' behavior → mark `QUESTION` or `Unverified`. Do not accept a developer's claim ("service X already handles it") without a file:line reference.
4. **The verdict is advisory.** Never say a MR "must be blocked". Use exactly one of: `Có thể merge` / `Merge sau khi sửa các mục` / `Cần trao đổi thêm`.
5. **No formatting or pure-style findings.** Spotless (BE) and Prettier/ESLint (FE) run in CI. Skip whitespace, brace style, import order, line length, pure naming style.
6. **Problem status belongs to the reviewer.** Developers never edit tracking files. Set status only from evidence (MR + file:line). Never close an item because it is old. Never guess about files that are not in the diff.
7. **CSV is the source of truth, Excel is generated.** Edit `problem.csv`, `history.csv`, `findings.csv`, `problem_check.csv`, `meta.json`; then run `python scripts/export_excel.py <dir>`. Never hand-edit `.xlsx`. Quote every CSV field that contains a comma, quote or newline (prefer writing CSV with Python's `csv` module over typing rows by hand); the export script rejects malformed rows.
8. **This repo holds reviews and problem-register data only.** Never modify service source code. Do not commit or push unless the owner asks. When asked, use branch `review/<service>-mr-<id>`.
9. **Every finding needs:** location (file:line, or diff line if no file line), problem, impact, suggested fix. No vague findings.

## Commands

| Command | Use |
|---|---|
| `/new-service <service> <High\|Medium\|Low> [repo-path]` | Create a service folder from `templates/` |
| `/review-mr <service> <MR id> [diff source]` | Review a diff and write a **draft** `review.md` only |
| `/finalize-review <service> <review-dir>` | After the owner edits `review.md`: sync CSVs, update the problem register, export Excel |
| `/problem-sweep <service>` | Re-verify open problems against current files supplied by the owner, then export |

## Where things are

- `docs/review-flow.md` – the full flow, classification and data schemas (imported below)
- `criteria/` – shared checklists (imported below); the owner edits these to change what gets reviewed
- `templates/` – blank files to copy; keep their headers exactly
- `services/<service>/service-profile.md` – risk tier, owners, optional stale threshold, overrides
- `services/<service>/problem.csv` + `history.csv` + `problem.xlsx` – living problem register: every finding, `Fix now` and debt
- `services/<service>/reviews/YYYY-MM-DD_MR-<id>/` – `review.md`, `findings.csv`, `problem_check.csv`, `meta.json`, `tracker.xlsx`

When a service has a `service-profile.md` override, it wins over the shared criteria for that service.

@docs/review-flow.md
@criteria/general.md
@criteria/spring-boot.md
@criteria/react.md
