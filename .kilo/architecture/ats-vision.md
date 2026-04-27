# ATS Vision — Working Document

> Iterative design document for the EmDash-powered Applicant Tracking System.
> Phases are sequential but each section evolves as design decisions are made.
> Last updated: 2026-04-26

---

## Overview

Build an AI-native ATS on the EmDash + Cloudflare Workers stack. The system
manages the full hiring lifecycle: jobs, candidates, applications, interviews,
offers, and agent-driven automation. Each candidate, job, and contact gets a
persistent AI agent (Durable Object) that maintains context across years.

**Key architecture decisions already made:**

- EmDash 0.7.0 as the CMS foundation (collections, admin UI, auth, storage, APIs)
- Cloudflare Durable Objects for agent-per-entity persistence
- Workers AI (Gemma 4) for inference — $0.02 per candidate session
- LoRA adapter training on DGX Spark via Unsloth Studio (handled separately)
- OpenViking MCP for cross-session agent context
- Deployed as single Worker per customer (SaaS model)
- All built and tested locally via `wrangler dev`

---

## Phase 1: Database Schema

### Core Collections

| Collection | Purpose | Key Fields |
|-----------|---------|-----------|
| `jobs` | Job listings | title, company_id (FK), location, salary_range, department, description (portableText), requirements (portableText), status, expires_at, hiring_manager_id (FK) |
| `candidates` | Candidate profiles | name, email, phone, linkedin_url, resume_path (R2), skills (AI-extracted), experience_years, education (JSON), location, source |
| `applications` | Candidate-job applications | candidate_id (FK), job_id (FK), status (pipeline stage), resume_path, cover_letter, ai_score (JSON), ai_report (portableText), stage_history (JSON), submitted_at |
| `companies` | Employer companies | name, website, industry, size, logo_path (R2) |
| `contacts` | People at companies | name, email, phone, company_id (FK), role, notes |
| `interviews` | Scheduled interviews | application_id (FK), interviewer_id (FK), scheduled_at, format (phone/video/onsite), scorecard (JSON), notes, status |
| `offers` | Job offers | application_id (FK), salary, start_date, status, letter_path (R2), accepted_at |

### Pipeline Stages (applications.status)

```
applied → screened → phone_screen → onsite → offer → hired
                                              → rejected
                       ↓
                    rejected
```

### Relationships

```
companies 1──N jobs
candidates 1──N applications N──1 jobs
applications 1──N interviews
applications 1──1 offers (optional)
companies 1──N contacts
```

### Indexes

Following EmDash index discipline:
- `idx_ec_jobs_status`, `idx_ec_jobs_company_id`, `idx_ec_jobs_hiring_manager_id`
- `idx_ec_candidates_email` (UNIQUE), `idx_ec_candidates_source`
- `idx_ec_applications_candidate_id`, `idx_ec_applications_job_id`, `idx_ec_applications_status`
- `idx_ec_interviews_application_id`, `idx_ec_interviews_scheduled_at`
- `idx_ec_offers_application_id`

### Migration

Follows EmDash migration pattern: `NNN_ats_collections.ts`, registered in
`StaticMigrationProvider`. Standard `ec_*` content tables with full
EmDash lifecycle columns (id, slug, status, author_id, created_at, etc.).

---

## Phase 2: Admin UI Design

### Pages

| Route | Purpose | Layout |
|-------|---------|--------|
| `/jobs` | Job listing management | Table with status badges, search, filters |
| `/jobs/new` | Create job posting | Two-column form: left=details, right=preview |
| `/jobs/:id` | Edit job + view applicants | Tabbed: details, applicants, pipeline |
| `/candidates` | Candidate database | Searchable table with skill filters |
| `/candidates/:id` | Candidate profile | Timeline, applications, AI scores, comms |
| `/pipeline/:jobId` | Kanban board for one job | Drag-and-drop cards, real-time WebSocket sync |
| `/reports` | Hiring analytics | Pipeline funnel, time-to-hire, source effectiveness |
| `/settings` | ATS configuration | Pipeline stages, email templates, scoring weights |

### Component Mapping (Kumo + EmDash)

| ATS Element | Component | Key Props |
|-------------|-----------|-----------|
| Kanban column | `div` + `flex flex-col gap-4` | Drop target via @dnd-kit |
| Candidate card | `Card` | `padding="md" variant="elevated"` |
| Stage badge | `Badge` | Color per stage (success/warning/info) |
| Job form | `Input` + `Select` + `InputArea` | Bound to collection schema |
| AI score display | `Badge` + `Tooltip` | Green > 80%, yellow 50-80%, red < 50% |
| Chatbot widget | `Card` + `useAgent` | Fixed position, WebSocket |
| Pipeline funnel chart | Custom SVG/Recharts | In reports dashboard |
| Confirm dialog | `ConfirmDialog` | Delete candidate, reject application |

### Color Tokens (Kumo Semantic)

```
Page background:      bg-kumo-canvas
Card background:      bg-kumo-elevated
Pipeline header:      bg-kumo-brand
Primary text:          text-kumo-default
Secondary text:        text-kumo-subtle
Borders:              border-kumo-line
Success (hired):      text-kumo-success
Warning (screening):  text-kumo-warning
Danger (rejected):    text-kumo-danger
Info (applied):       text-kumo-info
```

### RTL-Safe Rules

All layout classes must use logical properties: `ms-*` not `ml-*`, `pe-*` not `pr-*`,
`start-*` not `left-*`, `end-*` not `right-*`.

---

## Phase 3: Agent SDK Integration

### Agent Classes

| Agent | DO Name Pattern | Purpose | AI Model | Key Tools |
|-------|----------------|---------|----------|-----------|
| `ScreeningAgent` | `screening-{applicationId}` | Parse resumes, score fit, flag issues | Gemma 4 + LoRA | `parseResume`, `scoreFit`, `generateBrief` |
| `PipelineAgent` | `pipeline-{jobId}` | Manage kanban, send emails, schedule tasks | Gemma 4 | `moveStage`, `sendEmail`, `scheduleFollowup` |
| `CareerCoachAgent` | `coach-{visitorId}` | Chatbot on job board, job search, skill match | Gemma 4 | `searchJobs`, `matchSkills`, `explainRole` |
| `InterviewAgent` | `interview-{applicationId}` | Conduct AI interviews, score responses | Gemma 4 + LoRA | `generateQuestion`, `analyzeResponse`, `scoreInterview` |

### Agent Lifecycle

```
Agent created on first candidate interaction or application submission
  ↓
Processes task (screening, email, pipeline update)
  ↓
Writes results to D1 + DO SQLite (private memory)
  ↓
Broadcasts state to connected admin clients via WebSocket
  ↓
Hibernates when idle (0 connections, no pending tasks)
  ↓
Wakes on next interaction or scheduled alarm
  ↓
State + SQLite memory intact — knows everything from prior sessions
```

### Agent-to-D1 Integration

Agents write to the same D1 tables EmDash reads from:

```typescript
// Agent writes screening result
await this.env.DB.prepare(
  "UPDATE ec_applications SET data = json_set(data, '$.ai_score', ?), status = ? WHERE id = ?"
).bind(JSON.stringify(score), "screened", applicationId).run();

// Admin UI reads the same row (via EmDash Kysely)
const app = await db.selectFrom("ec_applications")
  .selectAll().where("id", "=", applicationId).executeTakeFirst();
```

No API calls between agent and application layer — same database, same transaction model.

### Local Development Model

```typescript
// Agent AI calls route through LiteLLM in local dev
const model = import.meta.env.DEV
  ? createOpenAI({
      baseURL: "http://localhost:4000/v1",
      apiKey: "sk-1234",
    })("gpt-4o-mini")  // Free tier during development
  : workersai("@cf/google/gemma-4-26b-a4b-it");  // Production

const result = await streamText({
  model,
  lora: import.meta.env.DEV ? undefined : "screening-lora-id",
  prompt: "Screen this candidate..."
});
```

---

## Phase 4: Chatbot Widget

### Architecture

```
Job Board Page (Astro)
  └── <CareerCoach /> (React island, client:load)
        └── useAgent({ agent: "CareerCoach", name: visitorId })
              └── WebSocket to CareerCoachAgent DO
                    └── AIChatAgent with Gemma 4 + tools
```

### Visitor Flow

```
Visitor: "I know Python and React, what jobs fit?"
  → Agent: matchSkills("Python, React") → queries D1 → returns top 3 matches
  → Visitor: "Tell me about the senior role"
  → Agent: explainRole(jobId) → reads job description → summarizes

Visitor: "What's the salary range?"
  → Agent: reads job.salary_range from D1 → displays

Visitor: "How do I apply?"
  → Agent: guides to application form, explains process

Visitor leaves → DO hibernates
Visitor returns tomorrow → same DO, same chat history
```

### Cost

~$0.00085 per visitor session on Gemma 4. 1,000 visitors/day = $0.85/day.

---

## Phase 5: LoRA Adapter (DGX Spark / Unsloth Studio)

Handled separately — not part of the codebase build.

**Training data format:**
```json
{
  "resume": "Full resume text...",
  "job_description": "Full job description...",
  "screening_result": {
    "score": 0.87,
    "skills_match": ["Python", "React", "PostgreSQL"],
    "skills_gap": ["Kubernetes"],
    "experience_match": "5 of 5 years required",
    "flags": ["Salary expectation exceeds range"],
    "recommendation": "Strong hire",
    "reasoning": "Candidate has all required skills..."
  }
}
```

**Training approach:**
- Base model: `@cf/google/gemma-4-26b-a4b-it`
- LoRA rank: r=8 (within Workers AI limits)
- Adapter size: < 300MB
- Upload via: `wrangler ai finetune create @cf/google/gemma-4-26b-a4b-it screening-lora ./lora`
- Integration: `lora: "screening-lora"` in agent AI calls

---

## Phase 6: SaaS Deployment Model

### Architecture: One Worker Per Customer

```
Customer A                    Customer B
┌──────────────────┐    ┌──────────────────┐
│ Worker A          │    │ Worker B          │
│ ├── EmDash CMS    │    │ ├── EmDash CMS    │
│ ├── Admin UI      │    │ ├── Admin UI      │
│ ├── Agent classes │    │ ├── Agent classes │
│ └── Job board     │    │ └── Job board     │
│                   │    │                   │
│ D1: ats-customerA │    │ D1: ats-customerB │
│ R2: ats-resumes-A │    │ R2: ats-resumes-B │
│ DOs: agents-* (A) │    │ DOs: agents-* (B) │
└──────────────────┘    └──────────────────┘
```

### Customer Onboarding

```bash
npx create-emdash@latest --template ats-customer
# → Scaffolds Astro project with EmDash + ATS pre-configured
# → Customer configures wrangler.jsonc
# → wrangler deploy → live in 30 seconds
# → EmDash setup wizard → collections created, admin user seeded
```

### Pricing Tiers (Draft)

| Tier | Candidates/Year | AI Screens/Month | Price |
|------|----------------|------------------|-------|
| Starter | 1,000 | 5,000 | $49/mo |
| Growth | 10,000 | 50,000 | $199/mo |
| Enterprise | 100,000+ | Unlimited | Custom |

### Cost Structure Per Customer

| Component | Monthly Cost |
|-----------|-------------|
| Worker compute + D1 + R2 + DOs | ~$5 |
| AI inference (Gemma 4) | ~$0.02/candidate |
| Total COGS | ~$10-50/mo depending on volume |

---

## Open Questions

1. **UI design details:** Exact kanban card layout, candidate profile timeline design,
   report chart types — left for Designer agent to resolve in Design Brief.

2. **Email integration:** Resend vs. Cloudflare Email Routing vs. direct SMTP — resolve
   during agent implementation phase.

3. **Calendar integration:** Google Calendar API vs. Cal.com for interview scheduling —
   resolve during InterviewAgent design.

4. **Resume parsing quality:** Base Gemma 4 vs. LoRA fine-tuned — test base model first,
   add LoRA if quality insufficient.

5. **Multi-tenant middleware:** Route by domain header, database-per-tenant, or
   query-level isolation — Model 1 (Worker per customer) chosen for simplicity.

6. **GDPR/data residency:** D1 replicas can be geo-restricted. Delete candidate data
   on request via EmDash storage API. Document in compliance section.

---

## Team Assignments

| Phase | Architect | Code | Site-Builder | Plugin-Builder | Designer | Review | Plan |
|-------|-----------|------|-------------|----------------|----------|--------|------|
| 1. Schema | Lead | Implement | — | — | — | Verify | Track |
| 2. Admin UI | Review brief | — | Build pages | Register routes | Design brief | Check Kumo | Track |
| 3. Agents | Define tools | Implement | — | Package plugin | — | DO patterns | Track |
| 4. Chatbot | Define flow | Implement | Widget UI | — | — | Review | Track |
| 5. LoRA | Spec format | — | — | — | — | — | — |
| 6. SaaS | Define model | Config | Template | Onboarding | — | — | — |

---

## References

- AGENTS.md — EmDash conventions, patterns, gotchas
- skills/creating-plugins/ — Plugin creation patterns
- skills/designer-reference/ — Kumo component mappings, color tokens
- skills/building-emdash-site/ — Astro page patterns
- packages/cloudflare/src/db/do-class.ts — Proven DO pattern
- OpenViking: `ov_search("database migration pattern")` — existing patterns
