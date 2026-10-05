# Structure

## Monorepo

```text
<project>/
├── docs/
│   ├── openapi.json
│   ├── acceptance-baseline.json
│   ├── plans/
│   └── decisions/
├── packages/
│   └── contracts/
└── apps/
    ├── api/
    └── web/
```

Pin exact versions. Keep shared versions in the pnpm catalog.

| Component | Package |
| --- | --- |
| HTTP | `@nestjs/platform-fastify` |
| Configuration | `@nestjs/config` |
| OpenAPI | `@nestjs/swagger` |
| ORM | `@nestjs/typeorm`, `typeorm`, PostgreSQL |
| Contracts | `zod` |
| Tests | `vitest`, `@nestjs/testing` |

## API tree

```text
apps/api/src/
├── main.ts
├── app.module.ts
├── common/          exceptions, exception filter, validation pipe, security headers
├── config/          validated environment and configuration factories
├── database/        data source, entity registry, transaction runner, migrations, seeds
├── logging/         JSON logger and the request log hook
├── health/          /health/live and /health/ready
├── auth/            /api/auth/**
└── <module>/        /api/<module>/**
```

Infrastructure folders follow the same file-type rules as modules. Only `database/` and other persistence files import the ORM. Do not name a module after a NestJS keyword such as `providers`.

The web client mirrors module names at `apps/web/src/features/<module>/`. This skill does not define component or state rules.

## File types

Every source file has one of these suffixes. The only other allowed source files are `main.ts`, `config/environment.ts`, the contracts `index.ts`, migrations, and tool configuration at a package root.

| Suffix | Content | Kind folder | Export |
| --- | --- | --- | --- |
| `.module.ts` | Wires providers. Never runs a query | never | `<Name>Module` |
| `.controller.ts` | One controller | `controllers/` | `<Name>Controller` |
| `.service.ts` | One service | `services/` | `<Name>Service` |
| `.repository.ts` | One repository | `repositories/` | `<Name>Repository` |
| `.adapter.ts` | One port or one external-service implementation | `adapters/` | `<Name>Adapter` |
| `.entity.ts` | One entity or view entity | `entities/` | `<Name>Entity` |
| `.exception.ts` | One exception | `exceptions/` | `<Subject><Reason>Exception` |
| `.interface.ts` | One interface | `interfaces/` | PascalCase of the file name |
| `.type.ts` | One type alias | `types/` | PascalCase of the file name |
| `.guard.ts` | One guard | `guards/` | `<Name>Guard` |
| `.decorator.ts` | One decorator | `decorators/` | PascalCase of the file name |
| `.filter.ts` | One exception filter | never | `<Name>Filter` |
| `.pipe.ts` | One pipe | never | `<Name>Pipe` |
| `.logger.ts` | One logger | never | `<Name>Logger` |
| `.runner.ts` | Transaction or seed runner, `database/` only | never | `<Name>Runner` |
| `.datasource.ts` | Data source options, `database/` only | never | camelCase functions |
| `.config.ts` | One configuration factory, `config/` only | never | camelCase constant |
| `.constants.ts` | Fixed values of one module | never | `UPPER_SNAKE` |
| `.utils.ts` | Pure functions, no state or database access | `utils/` | camelCase functions |
| `.hook.ts` | One Fastify hook | never | camelCase function |
| `.registry.ts` | Entity list, `database/` only | never | `UPPER_SNAKE` |
| `.seed.ts` | One seed, `database/seeds/` only | never | camelCase function |
| `.fixture.ts` | One fixture or record builder, tests only | `fixtures/` | camelCase, `InMemory<Port>` |
| `.spec.ts` | Unit tests of the sibling file | beside the file | — |
| `.e2e-spec.ts` | One use case, requirement, or flow | `e2e/` or a suite folder | — |
| `.schema.ts` | Zod schemas, contracts only | module folder | see contracts reference |

`<Name>` is the PascalCase form of the file name before the suffix. `users-access.service.ts` exports `UsersAccessService`.

Migrations keep TypeORM names: `database/migrations/<timestamp>-<kebab-name>.ts`. They are the only files without a role suffix.

### Kind folders

1. Two or more files of one kind go in the kind folder.
2. One file of a kind stays loose in the module folder.
3. A `.spec.ts` file sits beside its source file and does not count toward rule 1.
4. Every module has `<module>.module.ts`. A module with a controller has `e2e/`, even for one test file.
5. A suffix marked "never" never goes in a kind folder. A folder has at most one `.module.ts` and one `.constants.ts`.
6. A kind folder holds one kind only.

### Topics

Topics apply to controllers, services, and repositories.

- Start with one of each. Add a second only as a topic.
- A topic is a group of routes with its own rules, such as `/api/users/:id/role`.
- The topic name is `<module>-<subject>` in every layer: `users-access.controller.ts`, `users-access.service.ts`, `users-access.repository.ts`.
- Split by subject, never by verb. `create-user.service.ts` is not a topic.
- Create a topic when a controller, service, or repository passes 300 lines.
- When an adapter passes 300 lines, split its port by external capability.

### Adapters

An adapter calls one external service. It lives in the module that owns that service, never in an infrastructure folder.

- The port is one abstract class with abstract members only.
- Each implementation is its own file that extends the port.
- The module binds the port: `{ provide: EmailSenderAdapter, useClass: SmtpEmailSenderAdapter }`.
- An implementation reads settings through `@nestjs/config`, sets a timeout, parses each reply with its own Zod schema, and maps external errors to module exceptions.
- No external type or error leaves the adapter. The adapter is private to its module.
- The end-to-end fake is `InMemory<Port>` in the test fixtures. Application code never imports it.
- When several modules need one external service, one module owns it and exports a service that wraps the adapter.

## Module shape

Several tables that change together stay in one module:

```text
users/
├── users.module.ts
├── users.constants.ts
├── controllers/
│   ├── users.controller.ts
│   └── users-access.controller.ts
├── services/
├── repositories/
├── entities/
│   ├── user.entity.ts
│   └── user-role.entity.ts
├── exceptions/
└── e2e/
```

`user_role` stays in `users/` because the routes that change it start with `/api/users`, and the row does not exist without its user. A catalog with its own routes, such as `roles/`, is its own module.

One table stays flat:

```text
products/
├── products.module.ts
├── products.controller.ts
├── products.service.ts
├── products.service.spec.ts
├── products.repository.ts
├── product.entity.ts
├── product-not-found.exception.ts
└── e2e/
```

A repository returns entities. The service converts an entity to a contract type in one private method, such as `toRecord`. The service treats the entity as read-only, imports it with `import type`, never imports `typeorm`, and never returns an entity.

## Where each thing goes

| Thing | Location |
| --- | --- |
| Endpoint | Controller of the module named by the first URL segment |
| Business rule | Service of that module |
| Query | Repository of that module |
| External call | Adapter of that module |
| Table | Entity of the module whose routes change it |
| Transaction | `TransactionRunner.run`, called by a service |
| Schema | `packages/contracts/src/<module>/` |
| Error code | `<module>-error-codes.schema.ts` in that folder |
| Permission code | `packages/contracts/src/permissions/` |
| Use-case test | `<module>/e2e/<verb>-<object>.e2e-spec.ts` |
| Call to another module | That module's exported service |

## Imports between modules

A file may import another folder only from this list:

| May import | Condition |
| --- | --- |
| `common/`, `config/`, `database/`, `logging/` | Persistence rules still apply |
| `auth` decorators | Controllers and services |
| `Principal` | Controllers, services, and repositories |
| Another module's `*.module.ts` | Only from a module file, in `imports` |
| Another module's exported service | Only a service that module exports |
| Another module's entity | Only from an entity, for a relation, and from the entity registry |
| Another module's interface | Only `import type`, when an exported method returns it |
| The contracts package | Any file |

A module never imports another module's repository, controller, or exception. An exported method returns a contract type, a primitive, or an interface of its own module.

Modules call each other in process. They never call each other over HTTP. A cycle is an error: move the shared rule to the module that owns the data.
