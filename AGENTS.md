This file provides guidance to agentic coding tools when working with code in this repository.

## Project Status

**Beta, post pre-release.** EmDash is published to npm and in active use, with i18n, RTL, and the plugin system shipped. We're no longer in the scorched-earth pre-release phase -- real users depend on current behavior, so backwards compatibility now matters (see Rules below). All development happens inside this monorepo using `workspace:*` links. See [CONTRIBUTING.md](CONTRIBUTING.md) for the human-readable contributor guide (setup, repo layout, "build your own site" workflow).

## Agent Team

This project is built by a multi-agent engineering team. **All agents:** see [`.kilo/architecture/agent-team.md`](.kilo/architecture/agent-team.md) for the canonical team organisation chart — agent profiles, models, skills, pipeline diagrams, dispatch decision matrices, and cost profiles. The companion [`.kilo/architecture/agent-team-report.md`](.kilo/architecture/agent-team-report.md) covers project context, gap analysis, and architecture rationale. Pipeline: `user → architect → {code-junior|senior|site-junior|senior} → review → github`.

## Repository Structure

This is a monorepo using pnpm workspaces.

`CLAUDE.md` is a symlink to `AGENTS.md`. `.opencode/skills` and `.claude/skills` are symlinks to `skills/`. Don't try to sync between them.

- **Root**: Workspace configuration and shared tooling
- **packages/core**: Main `emdash` package - Astro integration and core APIs
- **demos/**: Demo applications and examples (`demos/simple/` is the primary dev target)
- **templates/**: Starter templates (blog, marketing, portfolio, starter, blank) -- contributors copy these into `demos/` to build their own sites
- **docs/**: Public documentation site (Starlight)

# Rules

**Backwards compatibility matters now.** We're out of pre-release, but pre-1.0. Real installs depend on current behavior, schemas, and API shapes. Breaking changes are allowed in minors, but need an explicit decision, a bump on the affected package, and a changeset that calls the break out clearly. Prefer additive changes: new fields, new routes, new options with sensible defaults. If an old API is obsolete, mark the replacement as preferred and keep the old path working unless there's a reason it can't. Database migrations are forward-only -- never write one that leaves existing content inaccessible. When in doubt, open a Discussion before coding.

**TDD for bugs.** Write a failing test -> fix the bug -> verify the test passes. A bug without a reproducing test is not fixed.

**Localize everything user-facing.** All admin UI strings, aria labels, and toast messages go through Lingui. All admin layout uses RTL-safe logical Tailwind classes. See the Localization and RTL sections below.

## Contribution Rules (for AI agents and human contributors)

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR. Key rules:

- **You MUST use the PR template.** Every PR must include the PR template with all sections filled out. The template is loaded automatically when you create a PR via the GitHub UI. If you create a PR via the API or CLI, copy the template from `.github/PULL_REQUEST_TEMPLATE.md` into the PR body. **PRs that do not use the template will be closed automatically by CI.**
- **Features require a prior approved Discussion.** Do not open a feature PR without one. It will be closed. Open a [Discussion](https://github.com/emdash-cms/emdash/discussions/categories/ideas) in the Ideas category first.
- **Bug fixes and docs** can be PRed directly.
- **Check every applicable checkbox** in the PR template, including the "I have read CONTRIBUTING.md" box and the AI disclosure box if any part of the code was AI-generated.
- **Do not make bulk/spray changes** (e.g., "fix all lint warnings", "add types everywhere", "improve error handling across codebase"). If you see a systemic issue, open a Discussion.
- **Do not touch code outside the scope of your change.** No drive-by refactors, no "while I'm here" improvements, no added comments or logging in unrelated files.
- **All CI checks must pass.** Typecheck, lint, format, and tests. No exceptions.

## Workflow

### Before Starting

1. Run `pnpm --silent lint:json | jq '.diagnostics | length'` and fix any issues. Non-negotiable.

### During Work

- Run `pnpm --silent lint:quick` after every edit -- takes less than a second. Returns JSON with stderr redirected to /dev/null, so it won't break parsers. Fix any issues immediately.
- Run `pnpm typecheck` (packages) or `pnpm typecheck:demos` (Astro demos) after each round of edits.
- Format regularly. pnpm format in the root uses oxfmt with tabs for indentation and is very fast. Don't let formatting pile up.
- Commit regularly, and always format and quick lint beforehand.
- Update tasks.md when completing tasks. Write a journal entry when starting or finishing significant work, or if you learn anything interesting or useful that you'd like to remember.

### Before Committing

You verified linting and types were clean before starting. If they're failing now, your changes caused it -- even if the errors are in files you didn't touch. Don't dismiss failures as "unrelated". Don't assign blame. Just fix them.

### Changesets

If your change affects a published package's behavior, add a changeset. Without one, the change won't trigger a package release.

```bash
pnpm changeset --empty
```

This creates a blank changeset file in `.changeset/`. Edit it to add the affected package(s), bump type, and description:

```markdown
---
"emdash": patch
---

Fixes CLI `--json` flag so JSON output is clean.
```

Start descriptions with a present-tense verb (Adds, Fixes, Updates, Removes, Refactors). Focus on what changes for the user, not implementation details.

Skip changesets for docs-only, test-only, CI, or demo/template changes.

See [CONTRIBUTING.md § Changesets](CONTRIBUTING.md#changesets) for full guidance and examples.

### PR Flow

1. All tests pass: `pnpm test`
2. Full lint suite clean: `pnpm --silent lint:json | jq '.diagnostics | length'`. Returns JSON with stderr piped to /dev/null, so it won't break parsers. Fix any issues.
3. Format with `pnpm format` (oxfmt with tabs for indentation, configured in `.prettierrc`).
4. Add a changeset if the change affects a published package: `pnpm changeset`.
5. Open the PR with the `pr` skill. Fill out every section of the PR template. Check the AI disclosure box.

## Architecture Overview

EmDash is an Astro-native CMS

### Core Architecture

- **Schema in the database.** `_emdash_collections` and `_emdash_fields` are the source of truth. Each collection gets a real SQL table (`ec_posts`, `ec_products`) with typed columns -- not EAV.
- **Middleware chain** (in order): runtime init -> setup check -> auth -> request context (ALS). Auth middleware handles authentication; individual routes handle authorization.
- **Handler layer** (`api/handlers/*.ts`) -- Business logic returns `ApiResponse<T>` (`{ success, data?, error? }`). Route files are thin wrappers that parse input, call handlers, and format responses.
- **Storage abstraction** -- `Storage` interface with `upload/download/delete/exists/list/getSignedUploadUrl`. Implementations: `LocalStorage` (dev), `S3Storage` (R2/AWS). Access via `emdash.storage` from locals.

### Known Quality Patterns

**Index discipline.** Every content table gets indexes on: `status`, `slug`, `created_at`, `deleted_at`, `scheduled_at` (partial -- `WHERE scheduled_at IS NOT NULL`), `live_revision_id`, `draft_revision_id`, `author_id`, `primary_byline_id`, `updated_at`, `locale`, `translation_group`. Foreign key columns always get an index. Naming: `idx_{table}_{column}` for single-column, `idx_{table}_{purpose}` for multi-column.

**API envelope consistency.** Handlers return `ApiResponse<T>` wrapping data in `{ success, data }`. List endpoints return `{ items, nextCursor? }` inside `data`. The admin client's `parseApiResponse` unwraps `body.data`. Be aware of this layering when adding new endpoints.

## Commands

### Root-level commands (run from repository root):

- `pnpm build` - Build all packages
- `pnpm test` - Run tests for all packages
- `pnpm check` - Run type checking and linting for all packages
- `pnpm format` - Format code using oxfmt

### Package-level commands (run within individual packages):

- `pnpm build` - Build the package using tsdown (ESM + DTS output)
- `pnpm dev` - Watch mode for development
- `pnpm test` - Run vitest tests
- `pnpm check` - Run publint and @arethetypeswrong/cli checks

## Key Files

| File                                | Purpose                                               |
| ----------------------------------- | ----------------------------------------------------- |
| `src/live.config.ts`                | Collection schemas + admin config (user's site)       |
| `src/emdash-runtime.ts`             | Central runtime; orchestrates DB, plugins, storage    |
| `src/schema/registry.ts`            | Manages `ec_*` table creation/modification            |
| `src/database/migrations/runner.ts` | StaticMigrationProvider; register new migrations here |
| `src/plugins/manager.ts`            | Loads and orchestrates trusted plugins                |

## Import Conventions

- **Internal imports** always use `.js` extensions (ESM requirement)
- **Type-only imports** must use `import type` (enforced by `verbatimModuleSyntax: true`)
- **Package imports** do not use extensions: `import { sql } from "kysely"`
- **Virtual modules** use `// @ts-ignore` comment
- **Barrel files** (`index.ts`) re-export from sub-modules. Separate `export type { ... }` from value exports

## Environment Gating

- **Dev-only endpoints** must check `import.meta.env.DEV` and return 403 if false. This is a compile-time constant -- it cannot be spoofed at runtime.
- **Never** use `process.env.NODE_ENV` -- always use `import.meta.env.DEV` or `import.meta.env.PROD` (Vite/Astro standard).
- **Secrets** follow the pattern: `import.meta.env.EMDASH_X || import.meta.env.X || ""` -- check prefixed name first, then generic, then fallback.

## Testing

- **Framework:** vitest. Tests in `packages/core/tests/`.
- **Database:** Tests use real in-memory SQLite via `better-sqlite3` + Kysely. No DB mocking.
- **Utilities:** `tests/utils/test-db.ts` provides `createTestDatabase()`, `setupTestDatabase()` (with migrations), and `setupTestDatabaseWithCollections()` (with standard post/page collections).
- **Structure:** `tests/unit/` for unit, `tests/integration/` for integration (real DB), `tests/e2e/` for Playwright. Test files mirror source structure.
- **Lifecycle:** Each test gets a fresh in-memory DB in `beforeEach`, destroyed in `afterEach`.

## URL and Redirect Handling

When accepting redirect URLs from query params or request bodies:

- Validate the URL starts with `/` (relative path only).
- Reject URLs starting with `//` (protocol-relative -- would redirect to external hosts).
- HTML-escape any URL values before interpolating into HTML responses.
- Prefer server-side `Response.redirect()` over HTML `<meta http-equiv="refresh">`.

## Toolchain

- **pnpm** -- package manager
- **tsdown** -- TypeScript builds (ESM + DTS)
- **vitest** -- testing
- **oxfmt** -- code formatting (tabs for indentation). All source files use tabs, not spaces.

## TypeScript Configuration

- Target: ES2022
- Module: preserve (for bundler compatibility)
- Strict mode with `noUncheckedIndexedAccess`, `noImplicitOverride`

## Dev Bypass for Browser Testing

EmDash uses passkey authentication which cannot be automated in browser tests. Two dev-only endpoints are available to bypass authentication:

### Setup Bypass

Skips the setup wizard, runs migrations, creates a dev admin user, and establishes a session:

```
GET /_emdash/api/setup/dev-bypass?redirect=/_emdash/admin
```

### Auth Bypass

Creates a session for the dev admin user (assumes setup is already complete):

```
GET /_emdash/api/auth/dev-bypass?redirect=/_emdash/admin
```

### Usage in Agent Browser

When testing the admin UI with agent-browser, navigate to the setup bypass URL first:

```typescript
await page.goto("http://localhost:4321/_emdash/api/setup/dev-bypass?redirect=/_emdash/admin");
```

This will:

1. Run database migrations
2. Create a dev admin user (`dev@emdash.local`)
3. Set up a session cookie
4. Redirect to the admin dashboard

**Note**: These endpoints only work when `import.meta.env.DEV` is true. They return 403 in production.

## Code Patterns (Reference)

Detailed code patterns are indexed in OpenViking. Search for them on demand using `ov_find` (exact terms) or `ov_search` (semantic intent):

| Topic                           | Search Query                                               |
| ------------------------------- | ---------------------------------------------------------- |
| SQL / database operations       | `ov_find("SQL injection Kysely parameterized")`            |
| API error handling              | `ov_find("apiError handleError parseBody")`                |
| Authorization roles             | `ov_find("requireRole Role.EDITOR")`                       |
| CSRF protection                 | `ov_find("X-EmDash-Request CSRF")`                         |
| Pagination                      | `ov_find("cursor-based pagination FindManyResult")`        |
| Database tables / columns       | `ov_find("adding database tables columns index")`          |
| Migrations                      | `ov_find("migration naming exports registration")`         |
| API route structure             | `ov_find("API route file structure prerender")`            |
| Handler layer                   | `ov_find("handler ApiResponse discriminated union")`       |
| Performance / caching           | `ov_find("requestCached after fn performance")`            |
| Admin UI: Kumo components       | `ov_search("Kumo Button Dialog component admin")`          |
| Admin UI: Localization (Lingui) | `ov_find("useLingui Trans macro Lingui")`                  |
| Admin UI: RTL-safe Tailwind     | `ov_find("RTL-safe Tailwind logical classes")`             |
| Content localization            | `ov_find("locale translation_group row per locale")`       |
| Admin UI: Error handling        | `ov_find("throwResponseError DialogError ConfirmDialog")`  |
| Cloudflare env / Workers        | `ov_find("cloudflare workers env wrangler types")`         |
| Content table lifecycle         | `ov_find("ec_ table SchemaRegistry FIELD_TYPE_TO_COLUMN")` |
