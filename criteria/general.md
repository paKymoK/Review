# General review criteria

Applies to every service. Per-service overrides live in `services/<service>/service-profile.md`.

## Scope

- Review **added and changed lines**, with the surrounding code needed to understand them.
- Do not review untouched old code. Log a real problem seen there as `Existing-untouched` debt.
- **Out of scope:** formatting, whitespace, brace style, import order, line length, pure naming style. CI formatters own these. A naming problem counts only if it hides a bug or misleads about behavior.

## Evidence standard

- Cite file and line. If the diff has no file line numbers, cite the diff line.
- State the problem, the impact, and a concrete fix.
- If the answer depends on code outside the diff (function bodies, config, schema, other services), mark `QUESTION` and say what is needed to decide.
- A developer's claim without a file:line reference is not evidence.

## Severity

| Level | Meaning |
|---|---|
| 🔴 BLOCKER | Security hole, data loss or wrong data, outage, wrong business result |
| 🟠 MAJOR | Wrong behavior under concurrency, timeout or network failure; clear performance loss |
| 🟡 MINOR | Maintainability, small performance cost |
| ❓ QUESTION | The diff does not give enough information to decide |

## Always check (BE and FE)

- **Authentication and authorization:** every new endpoint or action is protected; access is checked per object, not only per role; client-supplied identity or role is never trusted.
- **Performance:** unbounded data, repeated calls in loops, work on the request thread that should not be there.
- **Anti-patterns:** remote calls, messaging, mail, or long file I/O inside a database transaction.
- **Cross-service consistency:** what happens if the other service is down, slow, retried, or returns an unexpected status.
- **Concurrency:** read-modify-write races, duplicate processing, retries without idempotency.
- **Input validation** at the boundary and **error handling** that neither swallows errors nor leaks internals.
- **Secrets and sensitive data** in code, config, logs and responses.
- **Tests:** new business logic has tests with meaningful assertions (MINOR unless the logic is critical).

## Debt triage

| Class | Use for |
|---|---|
| `Debt-Track` | Security, data correctness, reliability, real performance risk |
| `Debt-Opportunistic` | Low-risk maintainability issues worth fixing when someone touches the file |

Do not create debt for things CI formatters fix. Do not create debt for opinions without a concrete risk.
