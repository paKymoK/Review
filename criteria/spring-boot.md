# Spring Boot (BE) checklist

Use together with `general.md`. Apply to changed code.

## 1. Transactions and I/O (anti-patterns)

- No remote API call (Feign/RestTemplate/WebClient), Kafka publish, mail send, or long file I/O inside `@Transactional`. Prefer after-commit hooks or an outbox.
- `@Transactional` that is ineffective: private method, self-invocation, wrong propagation.
- Checked exceptions without `rollbackFor`; exceptions caught inside the transaction so rollback never happens.
- Transaction scope too large (holds a DB connection during slow work); missing `readOnly = true` on read paths when it matters.

## 2. Authentication and authorization

- New endpoint reachable without authentication; matcher order or path patterns that leave a gap.
- Missing method-level checks (`@PreAuthorize`) or role checks that do not match the business rule.
- Object-level authorization missing (IDOR): ID from the path/body used without checking ownership or tenant.
- User ID, role or tenant read from the request instead of the security context.
- Service-to-service calls without authentication, or tokens forwarded to places they should not go.
- Actuator, Swagger or debug endpoints exposed; CORS or CSRF settings loosened without reason.

## 3. Persistence and performance

- N+1 queries; lazy loading outside a transaction; entity graphs returned straight to the API.
- Unbounded queries: no pagination, no limit, `findAll` on large tables.
- New query on a filter or join column with no supporting index (ask if the migration is not in the diff).
- Loops with a query or remote call per item where a batch is possible.
- Native or JPQL queries built by string concatenation (injection).
- Large result sets loaded into memory; heavy work in the request thread.

## 4. Concurrency and idempotency

- Read-modify-write without locking (optimistic version or pessimistic lock) on shared rows.
- Retried or redelivered requests/messages that are not idempotent (duplicate payment, duplicate record).
- Mutable state in singleton beans; non-thread-safe objects shared across requests.
- `@Async` or custom executors: unbounded queues, no error handling, lost security/transaction context.
- `@Scheduled` jobs that run on every instance without a lock (ShedLock or similar).

## 5. Integration

- Remote calls without timeouts; retries on non-idempotent operations; no fallback or circuit breaker where failure would cascade.
- Remote errors mapped to a wrong or misleading local status.
- Kafka: no error handler or dead-letter topic; offset committed before processing finishes; ordering assumptions; incompatible schema change.
- Behavior when the other service returns 4xx/5xx/timeout is not defined in the diff → `QUESTION`.

## 6. Validation and error handling

- Request bodies and parameters not validated (`@Valid`, constraints) at the controller.
- Entities used directly as request/response objects (mass assignment, overexposure).
- Exceptions swallowed, logged and ignored, or turned into success responses.
- Stack traces or internal messages returned to clients; wrong HTTP status for the error.

## 7. Data and configuration safety

- Secrets, tokens or passwords in code, properties, or test fixtures that ship.
- Sensitive data in logs (PII, tokens, full request bodies).
- File upload without type/size checks or path traversal protection; unsafe deserialization.

## 8. Database migrations (Flyway / Liquibase)

- Long locks on big tables; destructive change (drop/rename) that breaks the previous version during a rolling deploy.
- New NOT NULL column without a default or backfill; data fix mixed into schema change without a safe rollback plan.

## 9. Tests (new code)

- New business logic without tests, or tests that assert nothing meaningful.
- Tests that depend on execution order, wall-clock time, or external services.
