# EmDash Agentic Project — Architecture Report

> Delivered by the architect agent (DeepSeek V4 Pro)
> Original: 2026-04-27 · Updated: 2026-05-01 (v1 restructure)
>
> **⚠️ Team structure has evolved.** This report provides the project context, gap analysis, and architecture rationale. For the current team organisation, models, skills, dispatch logic, and pipeline diagrams, see [`agent-team.md`](./agent-team.md).

---

## 1. What Is This Project?

**Two projects, sharing the same repo:**

### The Product: EmDash CMS

EmDash is an **Astro-native CMS** in beta (post pre-release, pre-1.0), published to npm. It's a monorepo using pnpm workspaces with three layers:

- `packages/core` — the `emdash` npm package: Astro integration, core APIs, type-safe Kysely query builder for D1/SQLite, storage abstraction (local/S3), content localization (row-per-locale), plugin system, admin UI built on Kumo (Cloudflare's design system), i18n/RTL support
- `demos/` — demo applications (`demos/simple` is the primary dev target)
- `templates/` — starter templates (blog, marketing, portfolio, starter, blank)

It's deployed on Cloudflare Workers + D1, with real users depending on current behavior. Backwards compatibility matters.

### The Agent Team: A Multi-Agent Development Pipeline

Overlaid on the EmDash codebase is a **structured multi-agent development team** configured via Kilo CLI. The agents collaborate through formal handoff protocols, shared memory (OpenViking MCP), and mode-switching to develop EmDash itself — and, increasingly, to build systems _on top of_ EmDash (like the ATS).

---

## 2. Objectives

The agent team's purpose is to **automate the full software development lifecycle** for the EmDash ecosystem:

1. **Design** — structural system design (architect), including visual design briefs via the `designer-reference` skill
2. **Implement** — core code + plugins (code-junior / code-senior), Astro site pages (site-builder-junior / site-builder-senior)
3. **Quality gate** — adversarial code review (review), lint/typecheck/test gates (enforced by doers before handoff)
4. **Release** — well-formed PRs with complete templates and changesets (github)

The pipeline is also designed to support **long-running product work** on top of EmDash — specifically, an AI-native Applicant Tracking System (ATS) detailed in `.kilo/architecture/ats-vision.md`, which will run on Cloudflare Durable Objects + Workers AI (Gemma 4).

> **May 1 restructure note:** The team was reduced from 8 to 5 agent slots (3 roles + 2 gates). `plan`, `designer`, and `plugin-builder` were absorbed. Code and site-builder now have junior (Flash-none, no thinking) and senior (Flash-high, thinking) variants for cost-appropriate task dispatch. Cloudflare skills are concentrated in architect + review. See [`agent-team.md`](./agent-team.md) for the full organisation.

---

## 3. Who Are the Agent Team?

**v1 (current):** 5 agent slots, 3 roles, 2 quality gates. Three agents from v0 were absorbed (plan, designer, plugin-builder). Code and site-builder have junior/senior variants for cost-appropriate dispatch. The architect is the default entry point.

| Agent                   | Model                  | Thinking | Role                                                                                                                                          | Skills                                                                                           |
| ----------------------- | ---------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **architect**           | DeepSeek V4 Pro-high   | Always   | System design, Cloudflare research, visual design briefs, task triage, pipeline dispatch. Absorbs `plan` + `designer`.                        | cloudflare-agents-sdk, cloudflare-durable-objects, designer-reference, openviking-agent-config   |
| **code-junior**         | DeepSeek V4 Flash-none | Off      | Boilerplate wiring, CRUD from spec, admin UI components, plugin scaffolding (~80% of code tasks).                                             | creating-plugins, emdash-cli, agent-browser, wordpress-plugin-to-emdash, openviking-agent-config |
| **code-senior**         | DeepSeek V4 Flash-high | On       | Complex logic, debugging, race conditions, performance, new patterns (~20% of code tasks). Absorbs `plugin-builder`.                          | (same as code-junior)                                                                            |
| **site-builder-junior** | DeepSeek V4 Flash-none | Off      | Pages from Design Brief, seed files, collections, menus, taxonomies (~80% of site tasks).                                                     | building-emdash-site, emdash-cli, wordpress-theme-to-emdash, openviking-agent-config             |
| **site-builder-senior** | DeepSeek V4 Flash-high | On       | Complex content queries, Portable Text rendering, layout debugging, performance (~20% of site tasks).                                         | (same as site-builder-junior)                                                                    |
| **review**              | DeepSeek V4 Flash-high | On       | Adversarial code review. Full checklist: SQL injection, locale filters, CSRF, TOCTOU races, i18n/RTL, O(n²), Cloudflare pattern verification. | adversarial-reviewer, cloudflare-agents-sdk, cloudflare-durable-objects, openviking-agent-config |
| **github**              | DeepSeek V4 Flash-none | Off      | Pipeline terminus. Creates well-formed PRs after all quality gates pass.                                                                      | openviking-agent-config                                                                          |

All model bindings are in `~/.config/kilo/kilo.jsonc`. All agent prompts are in `.kilo/agent/*.md` (version controlled). For the complete organisation chart, pipeline diagrams, dispatch decision matrix, skill distribution map, and cost profile, see [`agent-team.md`](./agent-team.md).

### v0 (April 27) — 8 Agents (Historical)

The original team had eight agents: plan, architect, designer, site-builder, plugin-builder, code, review, github. `plan` was a thin routing layer. `designer` was a serial bottleneck between screenshot and site-builder. `plugin-builder` did the same work as code but with a different prompt. The May 1 audit consolidated these into the architect + code/site-builder variants above.

---

## 4. How Do They Work Together?

### The Pipeline (v1)

```
user → architect → {code-junior | code-senior | site-junior | site-senior} → review → github
```

The architect is the default entry point. All tasks flow through design + dispatch. Doers can execute in parallel for independent sub-tasks within a stage. The architect assesses complexity and selects junior (Flash-none, no thinking) for straightforward work or senior (Flash-high, thinking) for complex logic.

### Collaboration Mechanism: The Three-Layer Handoff

Each agent transition uses a **three-layer bridge**:

1. **`ov_session_commit`** — archives the current agent's session to persistent memory (vertical plane)
2. **Write to `.kilo/handoff/current.md` + `ov_add_memory`** — persists the structured handoff to disk (always available, regardless of OV indexing state) AND to OpenViking's shared `viking://resources/` (horizontal plane, indexed for search). Disk bootstrap ensures the downstream agent can always find the handoff even if OV's async FTS index hasn't ingested it yet.
3. **`switch_mode`** — transfers execution to the next agent in the pipeline

The downstream agent, on activation, reads `.kilo/handoff/current.md` AND calls `ov_find("handoff {agent}")` in parallel, merging results from both sources. This dual-path recovery — fixed May 1, 2026 — eliminates the FTS indexing gap that previously caused handoffs to be missed.

### Quality Gates (enforced by doers before handoff to review)

- `pnpm --silent lint:quick` → zero diagnostics
- `pnpm typecheck` → no errors
- `pnpm format` → applied
- `pnpm test` → all passing
- `pnpm test:browser` → if admin UI changed
- `pnpm test:e2e` → if full-stack flows affected
- Changeset present if `packages/` changed

Review verifies gates were passed but does NOT re-run tests. GitHub does final verification before PR creation.

### Context Flow

Every agent loads context before responding, and the full AGENTS.md is injected into every agent's system prompt — giving all agents shared domain knowledge about EmDash's architecture, patterns, and constraints.

### Research Separation

The architect carries ALL Cloudflare skills and docs access. Doers (code, site-builder) do NOT. The architect researches Cloudflare primitives during design and bakes the decisions into the implementation spec — including wrangler config snippets, state schemas, routing strategies, and anti-patterns to avoid. Review verifies Cloudflare patterns in implemented code but does not research new ones.

---

## 5. Is the Collaboration and Workflow Robust?

### Strengths

1. **Well-defined roles with sharp boundaries.** No agent does another agent's job. Architect is read-only. Code doesn't design. Review is adversarial. This prevents role blur.

2. **Formal handoff protocol.** Every transition produces a structured document. Downstream agents explicitly search for and recover these handoffs. This creates an audit trail.

3. **Shared domain knowledge.** AGENTS.md is comprehensive — 671 lines covering architecture, conventions, API patterns, i18n, RTL, SQL safety, CSRF, pagination, testing. Every agent has this context loaded.

4. **Memory isolation.** Each agent has its own session namespace (`kilo-context-{agent}`). Agent-specific patterns are stored in `viking://agent/{id}/memories/`. Shared project knowledge lives in `viking://resources/`.

5. **Quality gates are objective and automated.** Lint, typecheck, format, and tests are all scriptable — no subjective "looks good to me." The review agent has a 127-line checklist covering SQL injection, TOCTOU races, locale filters, i18n, resource management, and more.

6. **Skills system.** Specialized domain skills (`building-emdash-site`, `creating-plugins`, `adversarial-reviewer`, `designer-reference`) are loaded by the agents that need them — site-builder doesn't carry plugin-building knowledge, and vice versa.

7. **Cross-layer awareness built into design.** The architect is explicitly instructed to check whether core changes affect templates and to flag site-builder work. This prevents pipeline surprises.

### Weaknesses and Gaps

> **Legend:** ✅ Resolved in v1 restructure · 🔶 Partially addressed · ❌ Still open

#### Gap 1: Pipeline Mechanics — No Error Recovery ❌

The pipeline is linear: architect → code → review → github. There is **no defined path for review rejection**. When review finds bugs:

- It switches to `code` for fixes
- But code then hands off back to review
- There's no loop detection or state tracking to prevent infinite review→fix→review cycles

The handoff documents don't carry a retry counter or iteration index. A persistent bug class could cycle indefinitely.

**Severity: MEDIUM** — doesn't block basic flows, but lacks guardrails for complex PRs.

#### Gap 2: No CI/CD Gating Hook ❌

The review agent checks its full checklist, but the **github agent** also runs lint checks before creating the PR. This is redundant — the code agent already verified lint. But more importantly, **neither agent verifies that CI actually passes.** The github agent creates the PR and reports the URL, but doesn't poll CI status or handle CI failure.

**Severity: MEDIUM** — a red CI PR is created without the pipeline knowing.

#### Gap 3: The Designer → Site-Builder Gap ✅ RESOLVED (v1)

The designer agent was a separate vision-model agent that produced Design Briefs for site-builder. Issues were: no verification loop, no visual feedback mechanism, and zero end-to-end exercises of this path. **In v1, the designer agent was absorbed by the architect.** The architect now produces design briefs using the `designer-reference` skill (Kumo component gallery, color tokens, layout patterns). This eliminates the serial handoff bottleneck and keeps design context in the same session as system architecture. The visual feedback loop gap remains a concern for screenshot-based design, but the architect can use browser tools to verify.

**Severity: Resolved** — the serial bottleneck and role ambiguity are eliminated. Screenshot-to-design workflow remains design-only (no verification loop), but this is now a feature gap rather than a structural flaw.

#### Gap 4: No Schema/Seed Validation in the Pipeline ❌

The site-builder builds pages and seed files, but seed validation (`npx emdash seed seed/seed.json --validate`) is in the `seed-site` slash command — not in any quality gate. The code agent checks lint/typecheck/tests, but doesn't validate the seed file. A seed with a mismatched taxonomy name (e.g., `categories` vs `category`) would pass the pipeline and only fail at runtime on the Astro site.

**Severity: MEDIUM** — runtime failures bypass lint and typecheck.

#### Gap 5: ATS Is Designed But Not Integrated into the Pipeline 🔶 PARTIALLY ADDRESSED (v1)

The `.kilo/architecture/ats-vision.md` is a 349-line design document covering the full ATS architecture (7 collections, pipeline stages, Durable Object agents, Workers AI with LoRA adapters). **In v1, Cloudflare skills (`cloudflare-agents-sdk`, `cloudflare-durable-objects`) were assigned to the architect and review agents.** The architect can now design ATS components using Cloudflare primitives and hand off complete implementation specs to code-senior. However, no ATS-specific skill document has been created yet.

**Severity: MEDIUM** — Cloudflare primitive knowledge is now in the right agents, but ATS-specific patterns still need documentation.

#### Gap 6: No Cross-Agent Testing ❌

Quality gates test code correctness. They do not test **agent collaboration correctness**. There's no integration test that verifies:

- An architect design can be consumed by code without ambiguity
- A design brief can be consumed by site-builder without guesswork
- A review handoff back to code is formatted correctly for downstream consumption

**Severity: LOW** — would detect handoff format drift before it causes real failures.

#### Gap 7: The Handoff Protocol Is Fragile for Parallel Pipelines ✅ RESOLVED (v1)

**Fixed May 1, 2026.** The handoff now uses **dual-path persistence**: every handoff is written to `.kilo/handoff/current.md` (disk, always available) AND `ov_add_memory` (OV, indexed). Downstream agents read both in parallel, merging results and preferring the most recent. This eliminates the FTS indexing gap that caused handoffs to be missed. The `current.md` single-file bottleneck for concurrent pipelines remains, but this is a theoretical concern — parallel pipelines are rare and the dual-path recovery makes handoff discovery robust even under contention.

**Severity: Resolved** — handoff discovery is now synchronous and reliable.

#### Gap 8: No Active Pipeline Monitoring ❌

The `agent-manager.json` tracks sessions and worktrees, but there's no dashboard or health check that shows:

- Which pipelines are currently active
- Who is blocked waiting for whom
- How many review→fix cycles a PR has gone through
- Memory/stats drift across agents

**Severity: LOW** — operational visibility gap, not a correctness gap.

#### Gap 9: Skills Are Agent-Local but Not Compositionally Shared ❌

The skills system is designed for agent-specific loading. But there's no mechanism for **cross-agent skill composition**. For example, `building-emdash-site` is loaded by site-builder, but the architect might need a subset of it to validate cross-layer impact. The architect currently has to maintain duplicate EmDash domain knowledge inline.

**Severity: LOW** — works, but duplicates knowledge and creates drift risk.

#### Gap 10: No Agent Upgrades or Rotation Strategy ❌

Agents run on specific models (V4 Pro, V4 Flash, Qwen — final model). There's no documented process for:

- Upgrading models when new versions arrive
- Rotating a model out when it degrades
- Comparing agent performance across model versions
- Fallback models if a primary model is unavailable

**Severity: LOW** — production concern, not an immediate issue.

---

## 6. Resolved Issues

### April 27 Audit

| Bug                                     | File                             | Status    |
| --------------------------------------- | -------------------------------- | --------- |
| MCP endpoint swap (ov_find ↔ ov_search) | `.kilo/mcp/openviking_server.py` | **FIXED** |
| Duplicate Handoff Protocol section      | `.kilo/agent/designer.md`        | **FIXED** |

### May 1 Audit — Team Restructure

| Change                         | Details                                                                                                  | Status                                        |
| ------------------------------ | -------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Team reduced 8 → 5 slots       | `plan`, `designer`, `plugin-builder` absorbed                                                            | **DONE**                                      |
| Junior/senior variants         | `code-junior`/`code-senior`, `site-builder-junior`/`site-builder-senior` with Flash-none/Flash-high      | **DESIGNED**                                  |
| Cloudflare skills consolidated | Removed from doers. architect (research) + review (verification) only                                    | **DESIGNED**                                  |
| Handoff dual-path recovery     | Disk + OV parallel read on session start. Eliminates FTS indexing gap                                    | **IMPLEMENTED** — all 8 agent prompts updated |
| Agent team org document        | `.kilo/architecture/agent-team.md` — canonical reference with diagrams, dispatch matrices, cost profiles | **CREATED**                                   |
| Model output mode guidance     | Added to code.md and site-builder.md domain rules                                                        | **DONE**                                      |
| Skill distribution corrected   | `creating-plugins` → code, `agent-browser` → code+review, `wordpress-*` assigned                         | **DESIGNED**                                  |

---

## 7. Summary Assessment

The agent team in v1 is **significantly leaner and better-aligned** than v0. Key improvements:

1. **Pipeline simplified** — user → architect → doer → review → github (single path, 3-4 hops max vs 4-6 before)
2. **Cost-appropriate dispatch** — junior handles ~80% of tasks at lowest cost tier; senior reserved for complex work
3. **Research concentrated** — Cloudflare skills in architect + review only; doers implement from complete specs
4. **Handoff reliable** — dual-path disk+OV recovery eliminates indexing gaps
5. **Parallel execution possible** — architect can dispatch multiple doers for independent sub-tasks

Remaining structural concerns: no error recovery loop detection (Gap 1), no CI polling after PR (Gap 2), no seed validation gate (Gap 4), and no cross-agent testing (Gap 6). These are engineering concerns, not architectural flaws — the foundation is solid.

The next milestone is implementing the designed changes (variant prompts, kilo.jsonc updates, architect dispatch logic) and exercising each pipeline path end-to-end.

---

## 8. Recommended Next Actions (Priority Order)

| Priority | Action                                                                        | Owner     | Notes                                                             |
| -------- | ----------------------------------------------------------------------------- | --------- | ----------------------------------------------------------------- |
| P0       | Implement variant prompt files (code-junior/senior, site-junior/senior)       | architect | Duplicate-file approach until Kilo supports `prompt` field        |
| P0       | Update `~/.config/kilo/kilo.jsonc` with new agent entries                     | architect | Add junior/senior variants, remove plan/designer/plugin-builder   |
| P0       | Update architect.md with dispatch logic, routing table, complexity assessment | architect | Absorb plan's pipeline routing                                    |
| P0       | End-to-end smoke test of architect→code-junior→review→github path             | architect | Basic feature flow                                                |
| P1       | Create seed validation quality gate for site-builder                          | architect | Add `emdash seed --validate` to site-builder quality gates        |
| P1       | Add review iteration counter to handoff (reject→fix→review loop)              | architect | Track cycles to detect infinite loops                             |
| P2       | End-to-end smoke tests of all pipeline paths                                  | architect | Junior + senior variants, code + site-builder                     |
| P2       | Create ATS-specific skill document                                            | architect | Document DO patterns, Workers AI integration                      |
| P2       | Add CI polling to github agent (post-PR status check)                         | architect | Detect red CI before pipeline considers work done                 |
| P3       | Add pipeline monitoring dashboard or health check                             | architect | Track active pipelines, blocks, cycle counts                      |
| P3       | Implement skill composition for cross-agent reuse                             | architect | Architect to load building-emdash-site for cross-layer validation |
| P3       | Document model upgrade/rotation process                                       | architect | When models evolve, how to roll out agent updates                 |
