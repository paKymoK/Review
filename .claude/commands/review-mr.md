---
description: Review a merge request diff and write a draft review.md (Vietnamese)
argument-hint: <service> <MR id> [diff file | repo-path branch | pasted diff]
---

Review a merge request: $ARGUMENTS

Follow `docs/review-flow.md` steps 0-5 and the criteria already loaded.

1. Parse `service`, `MR id` and the diff source. If the diff source is `repo-path branch`, get the diff with `git -C <repo-path> diff <base>...<branch>` (ask for the base branch if unknown). If the diff is pasted in chat, save it to the scratchpad and work from the file.
2. Read `services/<service>/service-profile.md` (risk tier, overrides) and `services/<service>/problem.csv`. If the service folder does not exist, stop and suggest `/new-service`.
3. Create `services/<service>/reviews/<today>_MR-<id>/`. Today's date comes from the system, not from memory.
4. Review the diff by logical flow. Judge only changed code. Skip formatting and pure style. Mark anything the diff cannot show as `QUESTION`.
5. Re-check every `Open` or `Partially fixed` item in the register (debt and earlier `Fix now` items) against the diff using the table in the flow doc. Do not guess about files outside the diff.
6. Write `review.md` from `templates/review.md`, in Vietnamese. Put open problems that sit in files this MR touches in "Vấn đề tồn tại trong các file MR này chạm vào". Put new `Existing-*` problems in "Nợ kỹ thuật mới ghi nhận" as `D1, D2, ...`.
7. **Write only `review.md`.** Do not touch any CSV, `meta.json` or Excel. Those change at `/finalize-review`, after the owner edits the draft.
8. Reply with the verdict, counts by severity, the number of register items checked, and the path of `review.md`. Do not commit.
