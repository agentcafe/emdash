## Phase 1: Jobs Schema Foundation

Date: 2026-05-01
Linear: [AGE-5 — Jobs schema migration (ec_jobs table)](https://linear.app/agentcafe/issue/AGE-5)

---

### Architecture Decision

**`ec_*` tables are NOT created by numbered migrations.** The `SchemaRegistry.createContentTable()` method produces the canonical 15-column + 12-index layout for every content table. The deleted `036_ats_jobs.ts` was doing it wrong — duplicating standard columns that the registry provides automatically.

**Correct approach:** Register the "jobs" collection via `SchemaRegistry` (plugin install hook or setup script), then define ATS-specific fields via `SchemaRegistry.createField()`. No numbered migration file needed. This is the standard EmDash pattern used by `ec_posts`, `ec_pages`, and every other content type.

**Why not a migration:**
- Migrations are for system-table schema changes, not content table creation
- `SchemaRegistry` handles `ec_*` table creation with 15 standard columns + 12 indexes automatically
- Using the registry means the "jobs" collection appears in the admin UI's collection list, field manager, and content browser
- The registry pattern future-proofs: if standard columns change (new index, new column), `ec_jobs` gets the update automatically via `SchemaRegistry.migrateContentTables()`

---

### Field Design

#### Standard Columns (handled by SchemaRegistry)

Every `ec_*` table gets these automatically:

| Column | Type | Notes |
|--------|------|-------|
| `id` | TEXT PK | ULID |
| `slug` | TEXT | URL-safe, unique per locale |
| `status` | TEXT | draft / published / archived |
| `author_id` | TEXT | FK to users |
| `primary_byline_id` | TEXT | FK to bylines |
| `created_at` | TEXT | ISO 8601 |
| `updated_at` | TEXT | ISO 8601 |
| `published_at` | TEXT | ISO 8601, nullable |
| `scheduled_at` | TEXT | ISO 8601, nullable |
| `deleted_at` | TEXT | Soft delete, nullable |
| `version` | INTEGER | Revision counter |
| `live_revision_id` | TEXT | FK to revisions |
| `draft_revision_id` | TEXT | FK to revisions |
| `locale` | TEXT | "en" default |
| `translation_group` | TEXT | ULID for i18n linking |

Compound unique constraint: `(slug, locale)`

#### Standard Indexes (handled by SchemaRegistry)

```
idx_ec_jobs_slug                  ON (slug)
idx_ec_jobs_scheduled             ON (scheduled_at) WHERE scheduled_at IS NOT NULL
idx_ec_jobs_live_revision         ON (live_revision_id)
idx_ec_jobs_draft_revision        ON (draft_revision_id)
idx_ec_jobs_author                ON (author_id)
idx_ec_jobs_primary_byline        ON (primary_byline_id)
idx_ec_jobs_locale                ON (locale)
idx_ec_jobs_translation_group     ON (translation_group)
idx_ec_jobs_deleted_updated_id    ON (deleted_at, updated_at DESC, id DESC)
idx_ec_jobs_deleted_status        ON (deleted_at, status)
idx_ec_jobs_deleted_created_id    ON (deleted_at, created_at DESC, id DESC)
idx_ec_jobs_deleted_published_id  ON (deleted_at, published_at DESC, id DESC)
```

#### ATS-Specific Fields (added via SchemaRegistry.createField)

| Slug | Type | Required | Label | Notes |
|------|------|----------|-------|-------|
| `title` | string | yes | Job Title | Searchable, displayed in listings |
| `company` | string | yes | Company | Employer name |
| `location` | string | yes | Location | "Remote", "New York, NY", or "Hybrid — London" |
| `department` | string | no | Department | "Engineering", "Design", "Marketing" |
| `employment_type` | select | yes | Employment Type | Full-time / Part-time / Contract / Freelance / Internship |
| `workplace_type` | select | no | Workplace Type | Remote / Hybrid / On-site |
| `salary_min` | integer | no | Salary Min | Annual salary minimum (raw number, displayed formatted) |
| `salary_max` | integer | no | Salary Max | Annual salary maximum |
| `salary_currency` | string | no | Currency | ISO 4217, default "USD" |
| `salary_period` | select | no | Salary Period | yearly / monthly / hourly |
| `description` | portableText | yes | Description | Rich job description (supports headings, lists, bold/italic) |
| `requirements` | portableText | no | Requirements | Qualifications, skills, experience |
| `benefits` | portableText | no | Benefits | Perks, benefits, culture notes |
| `application_email` | string | no | Application Email | Where applications are sent (until apply form is built) |
| `application_url` | url | no | External Apply URL | Link to external ATS/Greenhouse/Lever if applicable |
| `closing_date` | datetime | no | Closing Date | Application deadline |
| `is_featured` | boolean | no | Featured | Highlighted on the job board (default false) |
| `is_remote` | boolean | no | Remote Eligible | Quick filter flag (default false) |

**SQL column types** (from `FIELD_TYPE_TO_COLUMN` mapping):
- `string` → TEXT
- `select` → TEXT
- `integer` → INTEGER
- `portableText` → JSON
- `url` → TEXT
- `datetime` → TEXT
- `boolean` → INTEGER (0/1)

#### Additional Indexes (ATS-specific, added manually)

```sql
CREATE INDEX idx_ec_jobs_status_featured ON ec_jobs (status, is_featured)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_ec_jobs_employment_type ON ec_jobs (employment_type);
CREATE INDEX idx_ec_jobs_location ON ec_jobs (location);
CREATE INDEX idx_ec_jobs_department ON ec_jobs (department);
CREATE INDEX idx_ec_jobs_closing_date ON ec_jobs (closing_date)
    WHERE closing_date IS NOT NULL;
CREATE INDEX idx_ec_jobs_salary_range ON ec_jobs (salary_currency, salary_min, salary_max)
    WHERE salary_min IS NOT NULL;
```

Rationale:
- `status_featured`: hot path — every public listing query filters by `deleted_at IS NULL AND status = 'published'`, and featured sort is common
- `employment_type`, `location`, `department`: filter facets on the public job board
- `closing_date`: partial index — only non-null rows, used for "closing soon" queries
- `salary_range`: composite index for salary-based filtering and range queries

---

### Collection Registration

```typescript
// Plugin install hook or setup script
const registry = new SchemaRegistry(db);

// 1. Create the collection — this creates ec_jobs with all standard columns + indexes
await registry.createCollection({
    slug: "jobs",
    label: "Jobs",
    labelSingular: "Job",
});

// 2. Define ATS-specific fields — each adds an ALTER TABLE ADD COLUMN
await registry.createField("jobs", {
    slug: "title", label: "Job Title", type: "string", required: true,
});
await registry.createField("jobs", {
    slug: "company", label: "Company", type: "string", required: true,
});
// ... all 18 fields

// 3. Create ATS-specific indexes
await db.schema
    .createIndex("idx_ec_jobs_status_featured")
    .on("ec_jobs")
    .columns(["status", "is_featured"])
    .where(sql`deleted_at IS NULL`)
    .execute();
// ... all 6 indexes
```

---

### Seed Data

5 seed jobs covering different employment types, locations, and workplace arrangements:

1. **Senior Frontend Engineer** — Full-time, Remote, Engineering, $140k–180k
2. **Product Designer** — Full-time, Hybrid (San Francisco), Design, $120k–160k
3. **DevOps Engineer** — Contract, Remote, Engineering, $100–150/hr
4. **Marketing Manager** — Full-time, On-site (New York), Marketing, $90k–120k
5. **Data Science Intern** — Internship, Hybrid (London), Data, £30k–35k

Seed data added to `demos/simple/seed/seed.json` under a `"jobs"` collection definition with taxonomy entries for `employment_type`, `workplace_type`, and `salary_period`.

---

### Route Contract Table

| Frontend Call | Backend Route | Handler | Status |
|---------------|---------------|---------|--------|
| `GET /_emdash/api/content/jobs?status=published` | Content API | `ctx.content.list("jobs", query)` | ✅ Built-in |
| `POST /_emdash/api/content/jobs` | Content API | `ctx.content.create("jobs", data)` | ✅ Built-in |
| `GET /_emdash/api/content/jobs/:id` | Content API | `ctx.content.get("jobs", id)` | ✅ Built-in |
| `PATCH /_emdash/api/content/jobs/:id` | Content API | `ctx.content.update("jobs", id, data)` | ✅ Built-in |
| `DELETE /_emdash/api/content/jobs/:id` | Content API | `ctx.content.delete("jobs", id)` | ✅ Built-in |

**Key insight:** No custom routes needed for basic CRUD. `SchemaRegistry` registration makes `ctx.content.*` work automatically. The plugin (`sandbox-entry.ts`) only needs custom routes for things the Content API doesn't provide (like `ai-generate`), which is AGE-7.

---

### Edge Cases

| Scenario | Behavior |
|----------|----------|
| Duplicate slug + locale | UNIQUE constraint rejects, 409 CONFLICT |
| Missing required field (title, company, location) | Schema validation rejects, 400 BAD_REQUEST |
| Empty job board (no published jobs) | `/jobs` returns 200 with empty items[], shows "No open positions" message |
| Salary range: min > max | Validation rejects at API layer |
| `closing_date` in the past | Still displayed but marked "Closed" on public page |
| Featured jobs sort | Featured first, then by published_at DESC |
| Deleted jobs | Soft delete (deleted_at set). Standard index filters exclude them |

---

### Implementation Steps

| Step | Action | Doer |
|------|--------|------|
| 1a | Plugin install hook: `createCollection("jobs")` + `createField(...)` × 18 + custom indexes | code-senior |
| 1b | Unit test: verify `ec_jobs` table shape, column existence, index existence | code-senior |
| 1c | Integration test: create + read + update + delete a job via Content API | code-senior |
| 1d | Seed file: 5 jobs with taxonomy entries in `seed.json` | site-builder-junior |
| 1e | Review: adversarial pass on schema, indexes, test coverage | review agent |

---

### Cross-Layer Impact

- **`demos/simple/seed/seed.json`** — new "jobs" collection + seed entries
- **`packages/ats-plugin/src/index.ts`** — install hook calls SchemaRegistry
- **Public job board (AGE-8)** — reads `ec_jobs` via `ctx.content.list("jobs", ...)`
- **Admin UI (AGE-6)** — reads/writes `ec_jobs` via Content API
- **No core changes needed** — SchemaRegistry is already the mechanism

---

### Tests Required

| Test | What It Verifies |
|------|-----------------|
| Unit: table existence | `ec_jobs` appears in `db.introspection.getTables()` after registration |
| Unit: column existence | All 18 ATS-specific columns present |
| Unit: standard columns | 15 standard columns present (id, slug, status, locale, etc.) |
| Unit: indexes | All 12 standard + 6 ATS-specific indexes exist |
| Unit: unique constraint | `(slug, locale)` UNIQUE constraint active |
| Integration: create | `ctx.content.create("jobs", validPayload)` returns `{ success: true }` |
| Integration: read | `ctx.content.list("jobs", { status: "published" })` returns items |
| Integration: update | `ctx.content.update("jobs", id, patch)` returns updated job |
| Integration: delete | `ctx.content.delete("jobs", id)` returns `{ success: true }` |
| Integration: validation | Missing `title` returns 400 |

---

### Out of Scope

- Plugin `sandbox-entry.ts` custom routes (AGE-7)
- Admin UI components (AGE-6)
- Public job board pages (AGE-8)
- Candidate/applications schema (Phase 2)
- `ai-generate` route (AGE-7)
- CreationAgent Durable Object wiring (AGE-7)
