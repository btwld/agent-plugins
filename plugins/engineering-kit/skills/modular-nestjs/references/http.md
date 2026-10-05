# HTTP, errors, and logs

## Request flow

1. A global authentication guard denies every route by default.
2. `@Public()` is allowed only in `auth/` and `health/`. `@Authenticated()` means a session without a permission. `@RequirePermission(...)` names the permission.
3. The guard reads the session cookie and loads the `Principal`: user, role, permissions, scopes, and active context.
4. Guards read decorators on the route method only. A decorator on the controller class is ignored, so do not put one there.
5. The controller receives the principal through `@CurrentPrincipal()` and passes it to the service.
6. The service checks record-level rules. A command checks them inside the transaction. A query applies them in `where`.

Rules:

- The actor and the active context come from the session. A body or query never supplies them.
- Context selection is `POST /api/auth/context`. It is a command. The server checks the selection against the user's scopes and stores it in the session.
- A user-facing method takes `(principal, input)`. A method called inside another module's transaction takes `(transaction, input)`.
- The active context filters every read and change of context-owned data. No active context means no such data.
- A context command without an active context throws `ContextRequiredException` (`403`).
- Only auth controllers use `@Res({ passthrough: true })`, to set or clear the session cookie.
- A state-changing request needs the session cookie and a CSRF token from that session.
- A development sign-in may exist for local work. It is disabled in production, and a test proves that.

```text
auth/
├── auth.module.ts
├── controllers/
│   ├── auth-session.controller.ts
│   └── auth-context.controller.ts
├── services/
├── guards/
│   ├── authentication.guard.ts
│   ├── permission.guard.ts
│   ├── csrf.guard.ts
│   └── rate-limit.guard.ts
├── decorators/
│   ├── public.decorator.ts
│   ├── authenticated.decorator.ts
│   ├── require-permission.decorator.ts
│   └── current-principal.decorator.ts
├── principal.interface.ts
└── e2e/
```

## Validation and OpenAPI

Register one `StandardSchemaValidationPipe` with `APP_PIPE`.

- Every `@Body`, `@Query`, and `@Param` declares `schema`. A parameter without one is not checked.
- The pipe's `exceptionFactory` throws `ValidationFailedException` with the field list.
- Do not write a custom validation pipe. Use `@Param("id", { schema: z.uuid() })` instead of `ParseUUIDPipe`.
- Request bodies, path parameters, and queries come from that `schema` option. Responses come from `standardSchema` on the response decorators.
- Error responses use the shared API error schema.
- Outside production, Swagger serves `/api/docs`.
- Export OpenAPI from the compiled application in NestJS preview mode, so the export needs no database. Fail the check when the committed document differs.

## Fixed values

- Use `z.uuid()`, `z.email()`, `z.iso.datetime()`, and `z.enum()`.
- Declare each value list once, in the contracts package.
- Permission codes come from one grouped constant, such as `Permission.USERS.EDIT`. Error codes come from the module enum.
- API-only limits go in `<module>.constants.ts`. A limit the contract also enforces is exported by the schema file.
- An entity column that stores a value list uses the contract type. Its `CHECK` constraint lists the same values.
- Only `config/` reads `process.env`. Feature code reads configuration through `@nestjs/config`.

## Exceptions

`ApplicationException` holds the code, HTTP status, message, and optional field list. It does not extend `HttpException`.

The code format is `<MODULE>_<REASON>`. The prefix is the module folder name with hyphens turned into underscores: `users` gives `USERS_`, `order-items` gives `ORDER_ITEMS_`. The code comes from the module error-code enum.

| Exception | Code | HTTP |
| --- | --- | --- |
| `ValidationFailedException` | `COMMON_VALIDATION_FAILED` | 400 |
| `MalformedRequestException` | `COMMON_MALFORMED_REQUEST` | 400 |
| `UnauthenticatedException` | `COMMON_UNAUTHENTICATED` | 401 |
| `PermissionDeniedException` | `COMMON_PERMISSION_DENIED` | 403 |
| `CsrfInvalidException` | `COMMON_CSRF_INVALID` | 403 |
| `ContextRequiredException` | `COMMON_CONTEXT_REQUIRED` | 403 |
| `RouteNotFoundException` | `COMMON_ROUTE_NOT_FOUND` | 404 |
| `ConcurrentChangeException` | `COMMON_CONCURRENT_CHANGE` | 409 |
| `PayloadTooLargeException` | `COMMON_PAYLOAD_TOO_LARGE` | 413 |
| `UnsupportedMediaTypeException` | `COMMON_UNSUPPORTED_MEDIA_TYPE` | 415 |
| `RateLimitedException` | `COMMON_RATE_LIMITED` | 429 |
| `InternalErrorException` | `COMMON_INTERNAL_ERROR` | 500 |
| `UseCaseNotImplementedException` | `COMMON_USE_CASE_NOT_IMPLEMENTED` | 501 |

- Services, repositories, and adapters throw only application exceptions. They never import exception classes from `@nestjs/common`.
- Name an exception `<Subject><Reason>Exception`, not after a NestJS exception.
- A controller does not catch exceptions.
- A unique violation becomes a module conflict exception.
- A record outside the actor's context is "not found", never a permission error.
- An unknown identifier in the body or query is `400` with `<MODULE>_<REFERENCE>_NOT_FOUND` and the field in the field list.
- A message tells the user what to do. It never contains a stack trace, SQL, a foreign identifier, or a secret.

One exception filter, registered with `APP_FILTER`, maps an `ApplicationException` to its contract and any other error to `COMMON_INTERNAL_ERROR`. A framework `HttpException` maps by status: `400`, `404`, `413`, `415`, and `429` become the matching common exception. The readiness route is the only route that sets its own status, for its `503` health body.

## Logs

Logs are JSON lines on standard output. Create the NestJS `ConsoleLogger` with `json` and `flattenParams`. Each class uses `new Logger(ClassName.name)`. Never use `console`.

| Field | Content |
| --- | --- |
| `timestamp` | Time of the entry |
| `level` | `error`, `warn`, `log`, or `debug` |
| `context` | Class name |
| `message` | Short fixed text. Variable values are fields |
| `userId` | Signed-in user, when one exists |
| `errorCode` | Exception code, when one caused the line |

- An `onResponse` hook writes one line per request, including requests a guard refuses.
- The filter logs the error code. A `500` also logs the stack trace.
- Slow queries log the query and the duration, never the parameters.
- `error` is a `500` or a failure a person must handle. `warn` is a refused security check, a slow query, or a repeated `4xx`. `debug` is off in production.
- Do not log passwords, tokens, cookies, secrets, full bodies, or unneeded personal data. Do not log inside a loop.
- A log is not an audit event. The audit event is business history, saved in the same transaction as the change.
