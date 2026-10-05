# Security, gates, foundation, and checklist

## Security

| Principle | Rule |
| --- | --- |
| Deny by default | A route without a declared access decorator is denied |
| Least privilege | Each user, role, database role, and integration job gets only the access its task needs |
| Defense in depth | Check access in the guard, the service, and the database |
| Fail closed | An error, a timeout, or a missing value denies the operation |
| Trust no input | Parse every request part with Zod. Read the actor and the context from the session |
| Minimize data | Collect, store, return, and log only what the use case needs |
| No secrets in code | Secrets come from the runtime secret store |
| Secure by default | Production settings are the defaults |

Map the OWASP API risks as follows: object checks against the principal and context (`404` for a foreign identifier); `HttpOnly` `Secure` `SameSite=Strict` cookies, CSRF, and a throttled sign-in; strict request objects; a maximum page size, body limit, rate limits, and statement timeouts; an access decorator on every route; rate limits and audit events on sensitive flows; no fetch of a client-supplied URL; security headers, a CORS allowlist, and no Swagger in production; the OpenAPI document lists every route; external responses are parsed with Zod and have timeouts.

- Mark a personal-data field with `.meta({ personalData: true })`. Personal data never appears in a URL, a log, an error, or a metric.
- Responses set `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, a restrictive content security policy, and `Cache-Control: no-store`.
- CORS allows configured origins only. Never allow `*` with credentials.
- Validate configuration at startup. Production has no default secret, no development sign-in, and no Swagger.
- Pin exact versions. Install with the frozen lock file. Audit high and critical findings on every pull request. Pin integration actions to a commit SHA.
- The application role owns no table and has no `BYPASSRLS`. Migrations and seeds use the migrator role. The application connection sets `statement_timeout`. Multi-tenant tables add row-level security to the service checks.

Endpoint checklist:

- The route declares its access decorator.
- Every request part has a strict Zod schema with limits.
- The service checks the target against the principal and the active context.
- A foreign or unknown identifier gives the same `404`.
- The response holds only contract fields.
- A list has a maximum page size and a stable order.
- A sensitive flow has a rate limit.
- Every change writes an audit event in the same transaction.
- End-to-end tests cover each denied case.

## Gates

| Rule | Enforced by |
| --- | --- |
| File suffixes, kind folders, one module file and one constants file | Structure check |
| Route owner, route protection, schema on every body, query, and param | Structure check |
| Import allowlist, private repositories, ORM boundary, transaction owner | Structure check |
| No NestJS exceptions in services, error-code prefix, contracts import only `zod` | Structure check |
| No `@ManyToMany`, `eager`, or `cascade`; entities extend a base entity | Structure check |
| 300 lines per controller, service, repository, or adapter; 40 lines per method | Structure check |
| No `console`, no `any`, named exports, no `process.env` outside `config/`, no skipped tests | Linter |
| Transaction context on write methods | TypeScript |
| Module cycles, OpenAPI drift, schema drift, acceptance ratchet, 80% coverage | Continuous integration |

TypeScript uses `strict`, `isolatedModules`, and `verbatimModuleSyntax`.

Useful scripts: `check` (lint, format, typecheck, module cycles, structure, OpenAPI), `test`, `test:e2e`, `test:coverage`, `acceptance:update`, `openapi:export`, `check:schema`.

Integration runs migrate twice, seed twice, the end-to-end suite with the ratchet, coverage, and the schema check. One required status check aggregates the jobs.

## Foundation, before the first feature

Build these in order, each with its own tests:

1. Workspace, catalog, TypeScript, lint, and format.
2. Contracts `common/` schemas: page, list query, audit fields, API error, common error codes.
3. Validated configuration and the JSON logger.
4. Data source, base entities, transaction runner, lock and error helpers, and the first migration with the system user.
5. Application exception, common exceptions, exception filter, and validation pipe.
6. Health routes.
7. Security headers, CORS allowlist, body limit, rate limits, and `statement_timeout`.
8. Auth: session, context, guards, decorators, and `Principal`.
9. OpenAPI export and drift check.
10. Test fixtures, end-to-end config, coverage, and the acceptance ratchet.
11. Structure check.
12. Continuous integration.
13. API and migration containers.

Add features only after the foundation passes its verification and integration.

## Anti-patterns

| Do not | Do this |
| --- | --- |
| One module per table | One module per resource, the first URL segment |
| A domain folder above the modules | Modules at the top of `src/` |
| A base controller, or a base repository with public methods | Protected helpers on `TypeOrmRepository` only |
| A business rule in a controller | The rule in the service |
| The actor or the context in the body | Read them from the session |
| A service that injects a TypeORM `Repository` | Inject the module repository class |
| A service that mutates an entity and expects a save | Call a repository write method |
| An entity in a response | Convert it to the contract type |
| A DTO class or a custom validation pipe | Zod with `StandardSchemaValidationPipe` |
| A transaction outside the runner, or around a query | `run` for a command; `reader` for a query |
| Read, check, and write when one statement is enough | One conditional `update` |
| An HTTP call inside a transaction | Before `run` or after commit |
| `@ManyToMany` | A join entity with two `@ManyToOne` relations |
| A kind folder with one file | Keep the file loose |
| A regular expression for an identifier or an email | `z.uuid()` or `z.email()` |
| A permission or error code as a raw string | The contracts enum or constant |
| A skipped test, or a test edited to match the code | Keep it failing until the use case works |

## New-feature checklist

Contract phase:

- Each use case has its requirement identifiers.
- The module folder is the first URL segment.
- Schemas and the error-code enum are in `packages/contracts/src/<module>/`.
- The entities and their migration exist.
- The module file, controllers, and service stubs exist.
- Each route has an access decorator. Each body, query, and param has a schema.
- Each stub throws `UseCaseNotImplementedException`.
- Each use case has one end-to-end file, with one test per rule and per denied case.
- Each success test fails.
- The plan lists denied cases, removals, and the requirements version, and it contains no foundation work.
- The OpenAPI document shows every new route.

Implementation phase, for each use case:

- The repository extends `TypeOrmRepository` and is not exported.
- Module exceptions use codes from the enum.
- The service uses one transaction and writes the audit event in it.
- The use-case tests pass without edits to the tests, and the baseline lists them.
- The endpoint checklist passes.
- Verification, end-to-end tests, and coverage pass.
