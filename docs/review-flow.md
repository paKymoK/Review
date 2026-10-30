# Review flow

Stack: Java Spring Boot (BE), ReactJS (FE). About 20 services, older code of mixed quality, new features still shipping.

## 1. Settled decisions

- Reviews are written in **Vietnamese only** (English technical terms kept).
- The workspace lives in **Git**: shared criteria, every review and every problem-register change are tracked.
- The verdict is **advisory**. The owner decides, managers set priority.
- **Formatting is out of scope** (Spotless / Prettier / ESLint in CI).
- **No stale threshold by default.** It can be set per service in `service-profile.md`.
- Low-risk "fix when you touch the file" items **get their own register ID**.
- The register (`problem.csv` / `problem.xlsx`) tracks **every finding**: `Fix now` findings from new code and debt alike. Managers see what was reported and whether it was fixed.
- ❓ QUESTION items are not problems yet; they stay in `review.md` only.
- Developers do not edit any tracking file and do not need a dedicated MR to fix debt.

## 2. Principles

1. New and changed code is held to the standard. Untouched old code is left alone unless it is a real risk.
2. Only the diff is judged. Anything the diff cannot show is `QUESTION` or `Unverified`.
3. Problem status is reviewer-owned and set only from evidence.
4. Stuck problems are kept as proof. Nothing is auto-closed, hidden or deleted because of age.
5. CSV and Markdown are the source of truth. Excel is generated for managers.

## 3. Roles

| Role | Does | Does not |
|---|---|---|
| Developer | Reads `review.md`, fixes what they choose while working in the area | Update any tracking file |
| Reviewer (owner + Claude) | Reviews the diff, triages, sets all statuses from evidence | |
| Manager | Reads `problem.xlsx`, sets priority, approves Won't fix and deferrals | |

## 4. Repo layout

```
CLAUDE.md                         instructions Claude Code reads automatically
docs/review-flow.md               this file
criteria/                         shared checklists (general, spring-boot, react)
templates/                        blank files, headers must not change
scripts/export_excel.py           CSV -> xlsx
.claude/commands/                 /new-service /review-mr /finalize-review /problem-sweep
services/<service>/
├─ service-profile.md             risk tier, owners, optional stale threshold, overrides
├─ problem.csv  history.csv      source of truth: problem register
├─ problem.xlsx                  generated (Summary, Register, Backlog, History)
└─ reviews/YYYY-MM-DD_MR-<id>/
   ├─ review.md                   draft by Claude, edited by the owner, read by devs
   ├─ findings.csv  problem_check.csv  meta.json    written at finalize
   └─ tracker.xlsx                generated
```

## 5. Per-MR flow

**Step 0. Intake** (`/review-mr`)
Input: service, MR id, and a diff source: a diff file, a pasted diff, or `repo-path + branch` (use `git -C <repo> diff <base>...<branch>`). Ignore images and binaries. Load `service-profile.md` and `problem.csv` for the service.

**Step 1. Read the diff by logical flow**
Group changes into flows (controller → service → repository, component → hook → API call). For large diffs read targeted line ranges, not a skim.

**Step 2. Review new and changed code**
Apply `criteria/`. Depth depends on the service's risk tier:
- **High:** full checklist, all severities.
- **Medium:** full checklist, MINOR only when cheap.
- **Low:** BLOCKER and MAJOR only.

**Step 3. Classify every finding** (see section 6).

**Step 4. Problem re-check**
For each `Open` or `Partially fixed` item in `problem.csv` (debt and `Fix now` items from earlier MRs alike):

| Situation | Result |
|---|---|
| Location is in the diff and the fix is visible | `Fixed (verified)` + evidence (MR, file:line) |
| Location is in the diff and part of the fix is visible | `Partially fixed` + what remains |
| Location is in the diff, problem still there | stays `Open`, `touched_not_fixed` +1 |
| Location is not in the diff | unchanged, noted "không chạm trong MR-x". No guessing |
| Code deleted or rewritten | `Obsolete` |

**Step 5. Write the draft `review.md`** (template in `templates/review.md`)
Order: metadata → advisory verdict → summary → findings by part → problem re-check → open problems in files this MR touches → new debt → open questions. Claude writes **only** `review.md` at this stage. No CSV or register changes yet.

**Step 6. Owner review**
The owner edits `review.md` anywhere Git is reachable. Deleting an item means no action and it is not logged. To defer a "fix now" item, add a line under it: `DEFER: <lý do>; giảm thiểu: <...>; duyệt bởi: <tên>; sprint: <tùy chọn>`. Deferring a security or data-loss item requires `duyệt bởi`.

**Step 7. Finalize** (`/finalize-review`)
Claude treats the edited `review.md` as the truth and:
1. writes `findings.csv`, `problem_check.csv`, `meta.json` to match it exactly;
2. updates `problem.csv`: statuses, counters and evidence for re-checked items, and **a new row for every finding block** (`Fix now` and `D#`) with the next `P-<service>-nnn` ID (never reuse an ID);
3. appends `history.csv`;
4. runs `scripts/export_excel.py` for the review folder and the service.

**Step 8. Commit** (by the owner, or by Claude when asked).

## 6. Classification

| Field | Values |
|---|---|
| Origin | `New` (added in this MR) · `Existing-touched` (old code in a changed file or hunk) · `Existing-untouched` (seen in passing, outside the diff) |
| Severity | 🔴 BLOCKER (security hole, wrong or lost data, outage, wrong business result) · 🟠 MAJOR (wrong behavior under concurrency/timeout/failure, clear performance loss) · 🟡 MINOR (maintainability, small performance) · ❓ QUESTION (diff does not give enough information) |
| Class | `Fix now` (this MR) · `Debt-Track` (real risk: security, data correctness, reliability, performance) · `Debt-Opportunistic` (low risk, fix when touching the file) |

Rules:
- `New` findings are `Fix now` unless the owner defers them.
- `Existing-*` findings are debt (`Debt-Track` or `Debt-Opportunistic`). They never block the MR.
- Every finding block (`Fix now`, `Debt-Track`, `Debt-Opportunistic`) gets its own register ID at finalize.
- A `Fix now` item stays `Open` in the register until a later MR diff or a sweep shows the fix (`Fixed (verified)`). Being merged is not proof.
- Formatting and style findings are not logged at all.

Numbering inside a review: `Part.Item` (1.1, 3.4). Parts: 1 transaction/I-O anti-patterns · 2 authentication and authorization · 3 performance and concurrency · 4 error handling and quality · 5 FE code quality. Keep gaps if the owner deletes items. New debt blocks are numbered `D1, D2, ...` until finalize assigns `TD-` IDs.

## 7. Problem lifecycle

Statuses, set by the reviewer only:
`Open` → `Partially fixed` → `Fixed (verified)`. Other end states: `Obsolete` (code gone), `Won't fix` (manager decision, reason recorded in `evidence`).

Deferred items ("go live first, fix after") record: reason, mitigation until fixed, approver, optional target sprint.

**Stuck problems as proof.** The register keeps `first_seen`, `times_seen`, `touched_not_fixed`, `last_checked` and an evidence trail in `history.csv`. Age is computed in Excel. The Backlog sheet lists everything not closed, oldest first.

**Stale flag (optional).** If `stale_after_days` in `service-profile.md` has a value, the Register shows a `STALE` column and the Summary counts it. Blank means no flag.

**Sweep.** `/problem-sweep` verifies open items against current files the owner supplies (or a local repo path). Without that input, statuses stay unchanged.

## 8. Data files

| File | Columns |
|---|---|
| `problem.csv` | `id, severity, category, origin, class, issue, location, description, suggested_fix, status, first_seen, first_seen_mr, last_checked, last_checked_mr, times_seen, touched_not_fixed, deferred, deferral_reason, mitigation, approved_by, target_sprint, evidence` |
| `history.csv` | `date, mr, problem_id, old_status, new_status, evidence` |
| `findings.csv` | `id, severity, origin, part, issue, location, description, suggested_fix, class, problem_id, note` |
| `problem_check.csv` | `problem_id, issue, previous_status, result, new_status, evidence` |
| `meta.json` | `service, mr, date, reviewer, risk_tier, verdict, verdict_reason` |

Conventions: dates `YYYY-MM-DD`; `deferred` is `yes` or empty; problem IDs `P-<service>-001`, never reused; `category` is one of `security, data, reliability, performance, maintainability, tests`; MR reference like `MR-123`. CSV is UTF-8 with a header row.

## 9. Limits

- Claude verifies only what a diff or supplied files show. A fix in an MR nobody reviewed stays `Open` until a later MR touches that file or a sweep runs.
- Anything outside the diff is `QUESTION` or `Unverified`.
- Excel files are outputs. Changes made directly in Excel are overwritten at the next export.
