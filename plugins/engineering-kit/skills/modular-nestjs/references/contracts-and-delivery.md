# Contracts, tests, and delivery

## Contracts package

Browser-safe Zod schemas live in `packages/contracts`. The API and the web client import the same schemas. Every module has a folder with its name, even for one file.

The package imports only `zod`. It never imports NestJS, TypeORM, Node built-ins, or environment variables.

```text
packages/contracts/src/
├── index.ts
├── common/
│   ├── page.schema.ts
│   ├── list-query.schema.ts
│   ├── audit-fields.schema.ts
│   ├── api-error.schema.ts
│   └── common-error-codes.schema.ts
└── users/
    ├── user.schema.ts
    ├── user-create.schema.ts
    └── users-error-codes.schema.ts
```

| Kind | Name | Example |
| --- | --- | --- |
| Request body | `<subject><Operation>RequestSchema` | `userCreateRequestSchema` |
| Query | `<subject>ListQuerySchema` | `userListQuerySchema` |
| Record | `<subject>RecordSchema` | `userRecordSchema` |
| Command result | `<subject><Operation>ResultSchema` | `userStatusChangeResultSchema` |
| Page | `<subject>PageSchema` | `userPageSchema` |
| Error codes | `<module>ErrorCodeSchema` | `usersErrorCodeSchema` |
| Inferred type | Schema name without `Schema` | `UserCreateRequest` |

- A record schema extends `auditFieldsSchema`.
- A command result holds only the values the command submitted or changed.
- A request or query schema never contains audit fields.
- A limit shared by the contract and the database is an exported `UPPER_SNAKE` constant in the schema file. The entity imports it. The migration copies the number.
- Do not add a schema for a use case that an open question blocks.
- Each schema file has a `.spec.ts` beside it.
- The web client uses each schema to validate a form, to type the response, and to parse the response at run time.
- There is no DTO class.

## Tests

| Kind | Suffix | Location | Proves |
| --- | --- | --- | --- |
| Unit | `.spec.ts` | Beside the file | One rule, with a fake repository |
| Use case | `.e2e-spec.ts` | `<module>/e2e/` | One route: HTTP, database, and audit event |
| Requirement | `.e2e-spec.ts` | `apps/api/tests/requirements/` | One requirement, across modules |
| Flow | `.e2e-spec.ts` | `apps/api/tests/flows/` | One user scenario |

- A use-case file is `<verb>-<object>.e2e-spec.ts`. Its `describe` title names the use case and the requirement identifiers the project uses.
- A use-case file calls only its own module and `/api/auth` routes. Other records come from fixtures.
- Write one `it` for each rule and each denied case: no session (`401`), missing permission (`403`), unknown or foreign identifier (`404`), wrong context (`404`), unknown or read-only field (`400`), oversized input (`400`), and concurrent change (`409`) on a write. A case that does not apply is `Not applicable: <reason>` in the plan.
- A refused write checks that nothing changed. A change checks its audit event.
- Tests import `it` from the application fixture and `describe` and `expect` from `vitest`. Do not use globals.
- Fixtures are `environment`, `app` (one per file), `signIn`, `anonymous`, and `records`.
- A fixture replaces only an adapter port, with `overrideProvider(<Port>).useClass(InMemory<Port>)`. It never overrides a service.
- Record builders write through the TypeORM repository API. Each test creates its own records. End-to-end files run one at a time.
- Do not use `skip`, `only`, `todo`, expected failures, or retries.
- Coverage of the API and the contracts package stays at or above 80% of lines, branches, functions, and statements. Exclude migrations, `*.module.ts`, and `main.ts`.
- Every service, guard, pipe, filter, hook, utils file, adapter implementation, and contract schema has a `.spec.ts`. A contract-phase stub and an adapter port do not.

### Acceptance ratchet

End-to-end tests exist before their behavior. The failing tests on the main branch are the missing features.

- `docs/acceptance-baseline.json` lists every end-to-end test that passes.
- Continuous integration fails when a listed test fails, and when a test passes but is not listed.
- A failing test that is not listed is a missing feature. Integration reports it and does not fail.
- A test leaves the baseline only when the plan lists it under removals.
- A file that fails to load fails integration.

## Delivery

```text
requirement → use cases → contract phase → implementation, one use case at a time
```

| Phase | Output | Tests |
| --- | --- | --- |
| Contract | Schemas, entities, migration, module, controllers, service stubs, end-to-end tests, OpenAPI | Success tests fail |
| Implementation | Repositories, rules, exceptions, unit tests | Those tests pass |

- A service stub throws `UseCaseNotImplementedException`, so the response is `501`.
- A `401`, `403`, or `400` test may already pass, because guards and validation exist. It proves a boundary, not the use case.
- Each use case has one success test that fails until the use case works.
- The contract phase may merge. The ratchet keeps integration green.
- Pin the requirements version in the plan. If requirements change, reopen the plan before more code.
- A feature plan does not include foundation work. Land the foundation first.
- List every route, test, constraint, or file the change deletes.
- A use case blocked as a whole has no route. A test proves the route is absent.
- A use case with one blocked rule still has its route. The blocked rule has no behavior until the question closes.

### Contract-phase controller and stub

```ts
@Controller("api/users")
export class UsersController {
  constructor(@Inject(UsersService) private readonly users: UsersService) {}

  @Post(":id/deactivate")
  @HttpCode(HttpStatus.OK)
  @RequirePermission(Permission.USERS.EDIT)
  @ApiOkResponse({ standardSchema: userStatusChangeResultSchema })
  deactivate(
    @CurrentPrincipal() principal: Principal,
    @Param("id", { schema: z.uuid() }) id: string,
  ) {
    return this.users.deactivate(principal, id);
  }
}
```

```ts
deactivate(_principal: Principal, _id: string): Promise<UserStatusChangeResult> {
  throw new UseCaseNotImplementedException();
}
```

The controller has no condition, no loop, and no data access. The actor and the active context come from the session, not from the body.
