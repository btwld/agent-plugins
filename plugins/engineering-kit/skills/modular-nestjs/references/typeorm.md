# TypeORM

## Entities

- One entity per file. A table entity extends `AuditedEntity`. An insert-only table extends `CreatedEntity`. A view entity extends neither.
- Do not name a base class `BaseEntity`. TypeORM exports a class with that name.
- `AuditedEntity` adds `id`, `created_at`, `updated_at`, `created_by_user_id`, and `updated_by_user_id`. `CreatedEntity` adds `id`, `created_at`, and `created_by_user_id`.
- Actor foreign keys use `@ForeignKey("UserEntity")` with a string target, so the base class does not import the user entity.
- The repository fills actor columns with `actorId(transaction)`. They never come from the request.
- A system process uses the system user that the first migration creates.
- An archivable table also has `archived_at` and `archived_by_user_id`.
- Table names are singular `snake_case`. Quote a reserved word, such as `"user"`, in hand-written SQL.
- Columns are `snake_case` in the database and `camelCase` in the entity, with the `name` option. Declare an explicit `type` on every column.
- Identifiers are UUIDs from `gen_random_uuid()`. Time is `timestamptz`. Money is `numeric`, handled as a string. Never use floating point for money.
- Declare every constraint on the entity and in the migration: primary key, foreign keys, unique, index, and check.
- Name a constraint only when a repository translates its violation into a module exception.
- Every foreign-key column has an index. Foreign keys use `ON DELETE NO ACTION`. Never use `ON DELETE CASCADE`. Never enable `synchronize`.

## Relations

- Declare the foreign key as a column, with `@ManyToOne` and `@JoinColumn` on that column.
- An entity may import another module's entity for a relation. The relation is read-only across modules.
- Add `@OneToMany` only when a repository reads through it.
- Do not use `eager` or `cascade`.

## Many-to-many

Never use `@ManyToMany`. Create a join entity:

```text
role ──< role_permission >── permission
         id
         role_id
         permission_id
         UNIQUE (role_id, permission_id)
```

The join entity extends `AuditedEntity`, has two `@ManyToOne` relations and a unique constraint on the pair, and belongs to the module whose routes change it. The link can then gain columns, audit events, and locks.

## Queries

Use the repository API first. Use the query builder when that API cannot express the query or a measured query is too slow.

| Need | Use |
| --- | --- |
| One row | `reader.findOneBy` or `reader.findOne({ where, select })` |
| List, filters, page, total | `reader.findAndCount` with `pageOptions` |
| Read and lock | `writer(transaction).findOne({ where, lock: { mode: "pessimistic_write" } })` |
| Insert | `writer(transaction).save` or `insert` |
| Conditional update | `writer(transaction).update`; check `affected` |
| A join the repository API cannot express | `createQueryBuilder` with named parameters |
| Grouping or aggregates | Query builder; parse raw rows into a named interface |
| A reused read model | A view mapped with `@ViewEntity` |
| A PostgreSQL feature TypeORM lacks | `query()` with numbered parameters, in a repository only |

- Pass values as parameters. Never build SQL by joining strings with values.
- Escape `%`, `_`, and `\` before `ILike`.
- Select only the columns the use case needs.
- Load a list and its related rows in one query or one extra `In(...)` query. Never run one query per row.
- Prefer a conditional update to a lock. When a lock is required, lock rows in ascending identifier order. Name the locked tables in a join.
- An advisory lock goes through the database lock helper, called only from a repository or a seed.
- A report lives in the `<module>-reports` topic of the module that owns the data, and it applies the same context rules as a list.

## Migrations

- Migrations are forward only. Each keeps the previous application version working during a deployment.
- Generate a migration from the entities, then review it. Add views, functions, grants, and exclusion constraints by hand.
- A migration never imports application code. Copy each constant it needs.
- Fail the schema check when the entities and the migrated schema differ.
- An effective period is `valid_from` and `valid_until` as a half-open range. An overlap rule is an exclusion constraint, declared on the entity with the same name.
- Each migration sets a short `lock_timeout`.
- The API never runs migrations at startup.

## Seeds

- A seed is an idempotent upsert keyed by a business code, never by a generated identifier.
- Reference data that the business edits after release is insert-only.
- Seeds reach entity classes only through the entity registry, validate fixture data against the contracts, and run in one transaction under an advisory lock with the system principal.
- Seeds hold synthetic or controlled reference data only. They do not use raw SQL for data.
