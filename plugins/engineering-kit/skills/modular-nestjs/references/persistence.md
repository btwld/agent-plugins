# Persistence and transactions

## Boundary

Persistence files are every file in `database/`, every `*.repository.ts`, and every `*.entity.ts`.

| Rule | Reason |
| --- | --- |
| Only persistence files import `typeorm`, `pg`, or `@nestjs/typeorm` | Other layers stay free of the ORM |
| Only persistence files import entities as values. A service may use `import type` | The service never runs ORM code |
| A repository returns entities or parsed rows, never `UpdateResult` or similar | ORM types stay inside the repository |
| A repository translates database errors into module exceptions | The filter knows only application exceptions |
| A repository receives page, sort, and filters in contract form | ORM options stay inside the repository |

## Commands and queries

Every command runs in one transaction. Every query runs without a transaction.

- A command method calls `TransactionRunner.run` once. A query method never calls `run`.
- A command that calls an external adapter may run one short transaction before the call and one after it, never during it.
- A command uses a transaction even when it writes one row today.
- `TransactionRunner` is the only class that uses the ORM transaction API. `DatabaseModule` is global and exports it. Inject the class: `@Inject(TransactionRunner)`.
- The signature is `run(principal, work, options?)`. `work` receives an opaque `TransactionContext`.
- `principal` is `TransactionPrincipal`: `userId`, scopes, and active context. The auth `Principal` extends it, so `database/` never imports `auth/`.
- A system process calls `run` with the system principal.

Write methods require a transaction at compile time:

- A command method takes the transaction context first and uses `writer(transaction)`. Reads inside a command do too.
- A query method has no transaction parameter and uses `reader`.
- When both need the same read, use two methods, such as `findById(id)` and `findForCommand(transaction, id)`. Never use an optional transaction parameter.
- An exported method that another module calls inside a transaction ends with `ForCommand` and takes `(transaction, input)`.

## Transaction rules

1. Every transaction starts with `run`. No other file opens one.
2. A service called for a write receives the caller's transaction context. Both writes commit, or neither does.
3. A nested `run` in the same call chain fails. Detect it with `AsyncLocalStorage`.
4. A context stops working after commit or rollback.
5. A transaction contains database work only. HTTP, e-mail, and queue messages run before it or after commit.
6. Prefer one conditional statement to read-check-write. `update({ id, status: "ACTIVE" }, { status: "INACTIVE" })` returns the changed-row count. If none changed, a read separates "not found" from "wrong status".
7. Lock a row only when the new value depends on a value the command reads.
8. The application connection sets `statement_timeout`.
9. PostgreSQL `40001` and `40P01` become `ConcurrentChangeException` (`409`). Do not retry automatically.
10. Background work opens its own transaction.
11. Seeds use `TransactionRunner` with the system principal. Migrations use their own transaction.

## Repository supertype

Every repository extends `TypeOrmRepository`. The supertype has no public operation.

| Protected member | Use |
| --- | --- |
| `reader` | Ordinary connection, for reads |
| `writer(transaction)` | Inside the transaction, for writes |
| `readerOf(Entity)` | Another entity of the same module, ordinary connection |
| `writerOf(transaction, Entity)` | Another entity of the same module, inside the transaction |
| `pageOptions(page, sort)` | `order`, `skip`, `take`, with `id` as the last sort key |
| `actorId(transaction)` | Actor user id, for audit columns |

- This table is the complete list.
- A repository serves its own module. It reads another module's table only through a join and never writes it.
- Do not add `findAll`, `delete`, or any other public operation to the supertype.
- There is no base controller and no base service.
- A repository without an entity, such as the readiness query, injects `DataSource` directly.

A command method takes `(transaction, input)`. A query method takes `(principal, input)`. Public methods use entities and contract types, never `FindOptionsWhere` or `UpdateResult`.

```ts
@Module({
  controllers: [UsersController],
  providers: [UsersService, UsersRepository],
  exports: [UsersService],
})
export class UsersModule {}
```

The module exports services, never the repository. A unit test replaces the repository with `{ provide: UsersRepository, useValue: fake }` and does not cast the fake.

## Lists

The list-query builder supplies `page`, `pageSize`, `sort`, and `order`. The page builder supplies the response. The repository calls `reader.findAndCount` with filters and `pageOptions`. The controller and the service pass the parsed query through unchanged.

## Service rules

A query:

1. Receives `(principal, input)`.
2. Calls reads that filter by the active context.
3. Throws the module "not found" exception when no row matches.
4. Converts entities to contract types.

A command, inside one `run(principal, ...)`:

1. Receives `(principal, input)`.
2. Checks rules that need no database.
3. Reads and changes the target through command methods filtered by the transaction's context.
4. Uses one conditional statement where it can.
5. Records the audit event in the same transaction.
6. Returns only the fields of the result contract.

## Style

- One responsibility per function. A block that needs a "what" comment becomes a private method.
- Return early. Do not mutate a received object. Await every promise. Use named exports.
- No `any`. Parse `unknown` with Zod at a boundary. Do not use `as` to hide a type error.
- Public service and repository methods declare parameter and return types.
- Comments explain why. Delete dead code.
- A method past 40 lines splits into private methods.
- A private method needed by two classes in one module moves to `<module>.utils.ts` as a pure function.
- A function needed by two modules moves to `common/` when it has no business rule. Otherwise callers use the owner's service.
- Every constructor parameter declares `@Inject(<Class>)`.
