---
description: Audit SQL queries for injection, missing indexes, and correctness
agent: review
---

Audit the SQL path in $ARGUMENTS for the following issues:

1. **String interpolation into SQL** — Search for `sql.raw()` with template literals or unvalidated dynamic values. Flag every instance.
2. **Missing validation on `json_extract`** — Any `json_extract(data, '$.${field}')` pattern must pass `field` through `validateIdentifier()` first.
3. **Missing indexes on WHERE columns** — New columns used in WHERE or ORDER BY clauses must have corresponding indexes.
4. **Missing indexes on FK columns** — All foreign key columns must be indexed.
5. **Missing locale filter** — Content table queries must filter by `locale` or intentionally operate across locales.
6. **Kysely usage** — Queries should use Kysely's typed query builder. Raw SQL is the escape hatch, not the default.

Report every finding with file, line, severity, and a specific fix.
