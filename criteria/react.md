# ReactJS (FE) checklist

Use together with `general.md`. Apply to changed code.

## 1. Security

- XSS: `dangerouslySetInnerHTML` without sanitization; user-controlled `href`/`src` (`javascript:` URLs); HTML built from strings.
- Tokens stored in `localStorage` or `sessionStorage` where an httpOnly cookie is expected by the project's standard; tokens or secrets in the bundle, URL query, or logs.
- Authorization enforced only in the UI. Hiding a button is not access control; the BE must also enforce it. If the BE check is not visible, mark `QUESTION`.
- Sensitive data written to console, analytics, or error reporting.

## 2. Hooks and component logic

- Rules of hooks violated; conditional hooks.
- `useEffect` with missing or wrong dependencies, no cleanup, or race conditions (an older request resolving after a newer one).
- Stale closures; state derived in an effect when it could be computed during render.
- Infinite render or fetch loops; effects that fire a request on every render.

## 3. Data fetching (RTK Query / API layer)

- Cache tags and invalidation missing or too broad, so data goes stale or refetches excessively.
- Polling or refetch settings that load the BE unnecessarily.
- Loading and error states not handled; errors swallowed; the UI shows success when the call failed.
- Duplicate requests for the same data; request parameters built unsafely.
- Mutations without handling for double submit, partial failure, or rollback of optimistic updates.

## 4. Forms

- No validation, or validation only in the UI where the BE needs it too.
- Double submit possible; buttons not disabled during submit.
- Errors from the BE not shown to the user; form state not reset or kept incorrectly after success/failure.

## 5. Performance

- Large lists without pagination or virtualization.
- Heavy computation in render without memoization **when it is measurably heavy**. Do not request `memo`/`useMemo` by reflex.
- Large dependencies added for small use; routes or heavy components not lazy-loaded when they should be.

## 6. Code quality (substance, not style)

- Duplicated logic that already exists in a shared helper or hook.
- TypeScript: `any` or unsafe casts that hide real type errors; missing null handling on API data.
- Components doing too many jobs in a way that makes the change risky to test.
- New logic without tests (MINOR unless critical).
