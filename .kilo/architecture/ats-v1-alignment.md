# ATS V1 Pipeline Alignment

Date: 2026-05-01
Product: Talent247 (app.talent247.co + jobs.talent247.co)

## ATS Deliverable → Agent Slot Mapping

| Deliverable | Agent | Wave | Dependencies |
|-------------|-------|------|-------------|
| Jobs schema (ec_jobs) | code-junior | 1 | None |
| Jobs seed data | site-junior | 1 | Jobs schema |
| Admin UI — jobs list page | code-junior | 2 | Jobs schema |
| Admin UI — job editor | code-junior | 2 | Jobs schema |
| Admin UI — job create form | code-junior | 2 | Jobs schema |
| AI generate route (P0) | code-junior | 2 | Jobs schema |
| Public job board page | site-junior | 3 | Jobs schema + seed data |
| Public job detail page | site-junior | 3 | Jobs schema |
| Job board filtering (facet search) | site-senior | 3 | Jobs schema + custom indexes |
| Applications schema | code-senior | 4 | Jobs schema |
| Pipeline schema | code-senior | 5 | Applications schema |
| Candidates schema | code-senior | 6 | Applications schema |
| Companies schema | code-junior | 6 | None |

## Wave-Based Build Order

### Wave 1: Foundation (Current)
**Goal:** Schema exists, data seeded, CRUD functional via Content API
- AGE-5: Jobs schema migration (ec_jobs) → **code-junior dispatched**
- AGE-6: Admin UI components (list, editor, create)
- AGE-7: AI generate route + plugin sandbox-entry
- Seed data: 5 sample jobs

### Wave 2: Public Surface
**Goal:** Live public job board with filtering
- AGE-8: Public job board page (list + detail)
- AGE-9: Facet search / filtering

### Wave 3: Application Pipeline
**Goal:** Candidates can apply, employers can manage pipeline
- Applications schema + CRUD
- Apply form
- Application dashboard

### Wave 4: RecOps Extensions
**Goal:** Full RecOps pipeline
- Pipeline stages schema
- Candidate management
- Company profiles
- Career coach agent (future)

## Route Contract Gap Analysis

| Route | Status | Wave |
|-------|--------|------|
| `GET /_emdash/api/content/jobs` | ✅ Built-in (Content API) | 1 |
| `POST /_emdash/api/content/jobs` | ✅ Built-in | 1 |
| `GET /_emdash/api/content/jobs/:id` | ✅ Built-in | 1 |
| `PATCH /_emdash/api/content/jobs/:id` | ✅ Built-in | 1 |
| `DELETE /_emdash/api/content/jobs/:id` | ✅ Built-in | 1 |
| `POST /_emdash/api/plugins/emdash-ats/ai-generate` | ⚠️ P0 — missing, needs custom route | 2 |

## Linear Issue Map

| Issue | Title | Wave | Status |
|-------|-------|------|--------|
| [AGE-5](https://linear.app/agentcafe/issue/AGE-5) | Jobs schema migration | 1 | In Progress |
| [AGE-6](https://linear.app/agentcafe/issue/AGE-6) | Admin UI — jobs | 2 | Backlog |
| [AGE-7](https://linear.app/agentcafe/issue/AGE-7) | AI generate route + sandbox | 2 | Backlog |
| [AGE-8](https://linear.app/agentcafe/issue/AGE-8) | Public job board | 3 | Backlog |
| [AGE-9](https://linear.app/agentcafe/issue/AGE-9) | Facet search / filtering | 3 | Backlog |

## Parallel Dispatch Strategy

Admin UI components (AGE-6) are independent React components — can be dispatched in parallel to multiple code-junior sessions:
- Jobs list page → code-junior session A
- Job editor → code-junior session B
- Job create form → code-junior session C

Each gets its own worktree: `age-6-list`, `age-6-editor`, `age-6-create`.

DO classes (Wave 4) must serialize: build CreationAgent first as template, then parallel-dispatch ScreeningAgent, PipelineAgent, CareerCoachAgent.
