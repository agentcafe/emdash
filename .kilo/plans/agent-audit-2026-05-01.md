# Agent Team Audit & Restructure Plan

**Date:** 2026-05-01
**Requested by:** User
**Owner:** Architect

## Current State

**8 agents, 3 of which are doers writing code.** The team has accumulated specialization that creates serial handoff bottlenecks without clear parallel work boundaries.

```
Current: user → plan → architect → code → review → github
                    → designer → site-builder → code → review → github
                    → plugin-builder → code → review → github
                    → code → review → github (direct)
```

**Problems:**

1. `plan` is a thin routing layer — architect could absorb it
2. `plugin-builder` writes the same kind of code as `code` — artificial split
3. `designer` produces design briefs but hands off to `site-builder` — serial bottleneck; architect can do visual analysis with the `designer-reference` skill
4. Cloudflare skills are loaded by code/site-builder agents who shouldn't need to research in-session — that's the architect's job
5. No mechanism for cost-appropriate model selection per task (boilerplate vs complex logic)
6. Too many handoffs = poor parallel throughput

## Target State

**5 agent slots, 3 distinct roles, 2 quality gates.** All research happens upfront in the architect. Doers receive complete specs. Multiple doers can execute in parallel.

```
user → architect (research + design + dispatch) →
  ├── code-junior  ──┐
  ├── code-senior  ──┤
  ├── site-junior   ─┼──→ review → github
  └── site-senior   ─┘
```

## Agent Restructure

### 1. Architect (default, always-on)

**Model:** `DeepSeek-V4-Pro-high` (thinking enabled — reasoning essential for design)
**Prompt:** `architect.md` (enhanced)
**Absorbs:** plan, designer

**New responsibilities:**

- Entry point for all user requests (Kilo default agent)
- Task triage and complexity assessment
- ALL research — Cloudflare docs, API patterns, migration patterns
- Produces complete design specs (contracts, route tables, schemas, edge cases, test requirements)
- Dispatches to correct doer with correct mode (junior vs senior)
- Visual design analysis via `designer-reference` skill
- Pipeline routing (absorbs plan agent's routing table)

**Skills:**

- cloudflare-agents-sdk — for Workers/DO architecture decisions during design phase
- cloudflare-durable-objects — for DO state model and alarm design
- designer-reference — for visual design analysis from screenshots
- openviking-agent-config

### 2. Code (two variants, shared prompt)

**Shared prompt:** `code.md`
**Old model:** `DeepSeek-V4-Flash-none` (one-size-fits-all)
**New model bindings:**

| Variant       | Model                    | Thinking | Best For                                                                                               | Cost Multiplier |
| ------------- | ------------------------ | -------- | ------------------------------------------------------------------------------------------------------ | --------------- |
| `code-junior` | `DeepSeek-V4-Flash-none` | No       | Boilerplate wiring, straightforward implementation from complete design, templates, simple CRUD        | 1x (baseline)   |
| `code-senior` | `DeepSeek-V4-Flash-high` | Yes      | Complex logic chains, debugging, performance optimization, multi-step problem-solving, race conditions | 2x–5x           |

**Scope:** All server-side and admin implementation — core features, plugins, API handlers, database operations, middleware, admin UI components.

**Skills (removes Cloudflare):**

- openviking-agent-config
- emdash-cli (for test commands, seeding)

**Testing gate (mandatory before handoff to review):**

- `pnpm --silent lint:quick` → zero diagnostics
- `pnpm typecheck` → no errors
- `pnpm test` → all passing
- `pnpm test:browser` → if admin UI changed
- `pnpm test:e2e` → if full-stack flows affected
- `pnpm format` → applied
- Changeset present if packages/ changed

### 3. Site-builder (two variants, shared prompt)

**Shared prompt:** `site-builder.md`
**Old model:** `DeepSeek-V4-Flash-none`
**New model bindings:**

| Variant               | Model                    | Thinking | Best For                                                                                           | Cost Multiplier |
| --------------------- | ------------------------ | -------- | -------------------------------------------------------------------------------------------------- | --------------- |
| `site-builder-junior` | `DeepSeek-V4-Flash-none` | No       | Boilerplate pages, seed files, simple layouts, straightforward component wiring from Design Brief  | 1x (baseline)   |
| `site-builder-senior` | `DeepSeek-V4-Flash-high` | Yes      | Complex content queries, Portable Text rendering logic, performance optimization, layout debugging | 2x–5x           |

**Scope:** Astro pages, collections, seed files, content queries, Portable Text rendering, menus, taxonomies, widgets, deployment configuration.

**Skills (removes Cloudflare):**

- building-emdash-site
- emdash-cli
- openviking-agent-config

**Testing gate (same as code):**

- `pnpm --silent lint:quick` → zero diagnostics
- `pnpm typecheck` → no errors
- `pnpm test` → all passing
- `pnpm format` → applied

### 4. Review (keep, enhanced)

**Model:** `DeepSeek-V4-Flash-high` (thinking enabled — needs reasoning for adversarial analysis)
**Prompt:** `review.md` (minor updates)

**Skills (keeps Cloudflare — needs to verify patterns):**

- adversarial-reviewer
- cloudflare-agents-sdk — to verify Workers/DO patterns in implemented code
- cloudflare-durable-objects — to verify DO state patterns
- openviking-agent-config

**Role:** Adversarial code review. Verifies testing gates were passed (does NOT re-run tests). Checks logic, SQL, i18n, RTL, CSRF, auth, migrations, indexes. Verdict: PASS → github, FAIL → back to code/site-builder.

### 5. GitHub (keep, unchanged)

**Model:** `DeepSeek-V4-Flash-none` (no thinking — mechanical PR creation)
**Prompt:** `github.md` (unchanged)
**Skills:** openviking-agent-config

**Role:** Pipeline terminus. Runs final quality gate verification, creates PR with template.

## Eliminated Agents

| Agent            | Why                                                                                                                                                      | Migration                                                                                         |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `plan`           | Thin routing layer. Architect already knows the pipeline and can dispatch directly.                                                                      | Routing table moves to architect.md                                                               |
| `designer`       | Serial bottleneck between screenshot and site-builder. Architect can produce design briefs via `designer-reference` skill.                               | Design brief format moves to architect handoff template                                           |
| `plugin-builder` | Plugins are code. Same implementation patterns as core features. Artificially splitting creates maintenance burden (two copies of implementation rules). | Plugin-specific patterns documented in `creating-plugins` skill, loaded by code agent when needed |

## Skills Distribution (Post-Restructure)

```
Architect:
  cloudflare-agents-sdk ← research, Worker architecture decisions
  cloudflare-durable-objects ← DO state model design
  designer-reference ← visual design analysis
  openviking-agent-config

Code (both variants):
  openviking-agent-config
  emdash-cli ← test commands, seeding

Site-builder (both variants):
  building-emdash-site ← authoritative API reference
  emdash-cli
  openviking-agent-config

Review:
  adversarial-reviewer
  cloudflare-agents-sdk ← verify Worker patterns in code
  cloudflare-durable-objects ← verify DO patterns in code
  openviking-agent-config

GitHub:
  openviking-agent-config
```

## Research Separation Principle

**Doers do not carry Cloudflare skills.** The architect has already researched all Cloudflare-specific concerns and baked them into the design. When code or site-builder receives a handoff, it includes:

- Complete API contracts
- DB schema with migrations
- Route contract table
- Edge cases documented
- Any Cloudflare-specific implementation notes (e.g., "use DurableObjectStorage.getAlarm() for this scheduled task, not setInterval")

If the doer encounters ambiguity, it flags back to the architect — it does not research Cloudflare docs itself. This keeps sessions short, focused, and cost-effective.

## Parallel Execution Pattern

The architect can dispatch multiple doers simultaneously for independent sub-tasks within a stage:

```
Stage: "Build the ATS job board"
  ├── Task 1: "API routes for jobs/list, jobs/create" → code-senior
  ├── Task 2: "Admin UI for job management" → code-junior
  └── Task 3: "Public job listing page and seed file" → site-builder-junior

All three run in parallel.
Result: 3 implementations that review integrates at stage end.
```

The stage-gate pattern:

1. Architect designs the full system
2. Doers implement independently in parallel
3. Review verifies each implementation
4. GitHub creates PR

## Testing — When and Who

Testing is a **quality gate** for code and site-builder agents, NOT a separate agent:

| When                     | Who                 | What                                                                             |
| ------------------------ | ------------------- | -------------------------------------------------------------------------------- |
| During implementation    | code / site-builder | Write unit tests alongside code (TDD for bugs)                                   |
| Before handoff to review | code / site-builder | Run full test suite: `pnpm test` + typecheck + lint                              |
| After handoff            | review              | Verifies tests were run and pass. Does NOT re-run. Focuses on adversarial review |
| Before PR                | github              | Verifies all quality gates passed                                                |

**Test tiers and when they run:**

| Tier               | Command                    | Runs When                    | Agent              |
| ------------------ | -------------------------- | ---------------------------- | ------------------ |
| Lint               | `pnpm --silent lint:quick` | Every edit                   | code, site-builder |
| Typecheck          | `pnpm typecheck`           | After each round of edits    | code, site-builder |
| Unit + Integration | `pnpm test`                | Before handoff to review     | code, site-builder |
| Admin component    | `pnpm test:browser`        | If admin UI changed          | code               |
| E2E                | `pnpm test:e2e`            | If full-stack flows affected | code               |
| Format             | `pnpm format`              | Before commit                | code, site-builder |

## Implementation Plan

### Phase 1: New Agent Entries in Config

Add to `~/.config/kilo/kilo.jsonc`:

- `code-junior` → DeepSeek-V4-Flash-none
- `code-senior` → DeepSeek-V4-Flash-high
- `site-builder-junior` → DeepSeek-V4-Flash-none
- `site-builder-senior` → DeepSeek-V4-Flash-high

### Phase 2: Agent Prompt Updates

- `architect.md` — add routing/dispatch logic, add `designer-reference` skill, add task complexity assessment criteria, add pipeline routing table
- `code.md` — remove Cloudflare skills, add testing gate section, add model output mode guidance (already done)
- `code-junior.md` — thin prompt referencing code.md with junior-specific notes
- `code-senior.md` — thin prompt referencing code.md with senior-specific notes
- `site-builder.md` — remove Cloudflare skills, add testing gate section, add model output mode guidance (already done)
- `site-builder-junior.md` — thin prompt referencing site-builder.md
- `site-builder-senior.md` — thin prompt referencing site-builder.md
- `review.md` — minor updates to verification checklist

### Phase 3: Archive Deprecated Agents

- Move `plan.md`, `designer.md`, `plugin-builder.md` to `.kilo/agent/deprecated/`
- Remove from `~/.config/kilo/kilo.jsonc`

### Phase 4: Architect Dispatch Logic

The architect needs clear criteria for choosing junior vs senior:

**Dispatch decision matrix:**

| Task Characteristics                                                   | Dispatch To         |
| ---------------------------------------------------------------------- | ------------------- |
| Boilerplate wiring, known pattern, design is complete                  | code-junior         |
| New route/handler from existing spec                                   | code-junior         |
| Simple admin UI component from design                                  | code-junior         |
| Straightforward Astro page from Design Brief                           | site-builder-junior |
| Seed file or collection definition                                     | site-builder-junior |
| Complex multi-step logic (auth flows, state machines, race conditions) | code-senior         |
| Debugging a hard-to-reproduce bug                                      | code-senior         |
| Performance optimization (N+1 queries, large datasets)                 | code-senior         |
| Complex Portable Text rendering logic                                  | site-builder-senior |
| Content query with joins, aggregation, or cursor pagination            | site-builder-senior |
| Layout debugging or responsive breakpoint issues                       | site-builder-senior |

## Cost Impact

| Metric                   | Current (8 agents)        | Proposed (5 slots)             |
| ------------------------ | ------------------------- | ------------------------------ |
| Agent count              | 8                         | 5 (+ 4 variant entries)        |
| Distinct roles           | 5                         | 3                              |
| Handoffs per pipeline    | 3–5                       | 2–4                            |
| Max parallel doers       | 1 (serial by role)        | 4 (junior + senior × 2)        |
| Default doer cost        | Flash-none (fixed)        | Flash-none (most tasks, ~80%)  |
| Complex task cost        | Flash-none (underpowered) | Flash-high (appropriate, ~20%) |
| Cloudflare skills loaded | 4 agents × sessions       | 2 agents (architect + review)  |

Average doer session cost goes down because junior handles ~80% of tasks at lowest tier. Senior is used only when complexity justifies it. Research overhead (Cloudflare docs lookups) is concentrated in the architect, not duplicated across doers.

## Open Questions

1. **Variant prompt files:** Duplicate code.md as code-junior.md and code-senior.md, or use thin wrapper prompts that reference code.md? The thin-wrapper approach reduces maintenance but may confuse Kilo's prompt loading.

2. **Architect as default:** Setting architect as the Kilo default agent requires changing the `default_mode` in Kilo config. Where is that set?

3. **Site-builder Cloudflare skills:** Currently site-builder loads `cloudflare-agents-sdk` and `cloudflare-durable-objects` in the demo config. Verify these are actually used by site-builder sessions before removing.

4. **Designer skill transition:** Does the architect need a vision-capable model to use `designer-reference` effectively? DeepSeek-V4-Pro-high supports vision.
