---
name: modular-nestjs
description: >-
  Use when building, changing, or reviewing a NestJS API that follows modular NestJS:
  the first URL segment after /api names the module, request and response schemas are
  Zod contracts, and only repositories and one transaction runner touch the database.
  Covers file placement, module shape, tests, transactions, errors, TypeORM, and gates.
  Do not use to choose NestJS versus another stack, to write an architecture decision,
  or for an application that has not adopted this convention.
---

<!-- Original engineering-kit skill. See ../../SOURCES.md. -->

# Modular NestJS

Apply these rules when the user asks for modular NestJS, or when the repository already follows them. If the repository uses a different NestJS layout, follow that layout and say so. Do not convert it unless the user asks.

This skill is generic. Do not invent a product name, a requirement catalog, or a tenancy model.

## Boundaries

- Choosing NestJS, the database, or a module boundary is the `architecture` skill. This skill starts after that choice.
- Turning requirements into a task list is `writing-plans`. When the plan targets a repository that uses this convention, the plan's paths follow this skill.
- Carrying out an approved plan is `executing-plans`. Obey this skill while placing files.
- A project document owns runtime, deployment, and database roles. Do not invent those rules.

## The one rule

The first segment of the URL after `/api` is the module name. Use that name for the module folder, the main file prefix, the contracts folder, and the web feature folder.

```text
URL                /api/users/:id/role
module folder      apps/api/src/users/
contracts          packages/contracts/src/users/
use-case tests     apps/api/src/users/e2e/
```

A sub-resource belongs to that module. A table with no route of its own belongs to the module whose routes change it.

Two exceptions only:

- Health routes live in `apps/api/src/health/` at `/health/*`, without the `/api` prefix.
- `common/`, `config/`, `database/`, and `logging/` have no routes.

## What to read

Read only the reference the task needs.

| Task | Reference |
| --- | --- |
| Place a file, name a module, or split a topic | [references/structure.md](references/structure.md) |
| Add schemas, tests, or a contract-phase slice | [references/contracts-and-delivery.md](references/contracts-and-delivery.md) |
| Write a repository, a command, or a query | [references/persistence.md](references/persistence.md) |
| Auth, validation, OpenAPI, errors, or logs | [references/http.md](references/http.md) |
| Entity, relation, query, migration, or seed | [references/typeorm.md](references/typeorm.md) |
| Security, gates, a new project, or the feature checklist | [references/quality.md](references/quality.md) |

## Apply the change

1. Derive the module from the URL. Do not add a domain folder above the modules.
2. Create only the files the change needs. Two or more files of one kind go in that kind's folder. One file stays loose.
3. For a new use case, add the contract, the failing use-case test, and the service stub before the repository and the rules.
4. A command runs in one `TransactionRunner.run`. A query does not open a transaction.
5. A service throws a module exception. It does not throw a NestJS HTTP exception, return an entity, or import the ORM.
6. Every route declares `@RequirePermission(...)`, `@Authenticated()`, or `@Public()`. Every `@Body`, `@Query`, and `@Param` declares a Zod schema.
7. Stop when the repository already has a rule this skill does not cover. Ask. Do not invent the missing rule.

## Check before you finish

- The new path follows the URL.
- The module does not export its repository.
- The success test of a new use case failed before the behavior existed, unless the repository's own process says otherwise.
- You did not add a DTO class, `@ManyToMany`, a skipped test, `any`, or `console`.
