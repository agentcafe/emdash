# EmDash Agentic Project — Architecture Report

> Delivered by the architect agent (DeepSeek V4 Pro)
> Date: 2026-04-27

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

Overlaid on the EmDash codebase is a **structured multi-agent development team** configured via Kilo CLI. The agents collaborate through formal handoff protocols, shared memory (OpenViking MCP), and mode-switching to develop EmDash itself — and, increasingly, to build systems *on top of* EmDash (like the ATS).

---

## 2. Objectives

The agent team's purpose is to **automate the full software development lifecycle** for the EmDash ecosystem:

1. **Design** — structural system design (architect), visual/UX design for sites (designer)
2. **Implement** — core code changes (code), Astro site pages (site-builder), EmDash plugins (plugin-builder)
3. **Quality gate** — adversarial code review (review), lint/typecheck/test gates (code)
4. **Release** — well-formed PRs with complete templates and changesets (github)

The pipeline is also designed to support **long-running product work** on top of EmDash — specifically, an AI-native Applicant Tracking System (ATS) detailed in `.kilo/architecture/ats-vision.md`, which will run on Cloudflare Durable Objects + Workers AI (Gemma 4).

---

## 3. Who Are the Agent Team?

Eight agents, each with a distinct role, model assignment, and memory namespace:

| Agent | Model | Role | Session |
|---|---|---|---|
| **plan** | DeepSeek V4 Pro | Workflow router. Receives user task → routes to correct pipeline. Does NOT write code. | `kilo-context-plan` |
| **architect** | DeepSeek V4 Pro (no-thinking) | System design, contracts, dependency analysis. Read-only structural analysis. Produces structured Design documents. | `kilo-context-architect` |
| **designer** | Qwen3.6-35B (vision) | Visual/UX designer. Reviews screenshots, produces Design Briefs for site-builder. | `kilo-context-designer` |
| **site-builder** | DeepSeek V4 Flash (no-thinking) | Builds Astro sites: pages, collections, seed files, Portable Text, menus, widgets. Loads `building-emdash-site` + `emdash-cli` skills. | `kilo-context-site-builder` |
| **plugin-builder** | DeepSeek V4 Flash (no-thinking) | Creates EmDash plugins: hooks, storage, admin UI, API routes, PT block types. Loads `creating-plugins` skill. | `kilo-context-plugin-builder` |
| **code** | DeepSeek V4 Flash (no-thinking) | Implementation engine. Writes code, runs lint/typecheck/tests, applies format. Executes designs — does not produce them. | `kilo-context-code` |
| **review** | DeepSeek V4 Flash (no-thinking) | Adversarial code review. Loads `adversarial-reviewer` skill. 127-line checklist: SQL injection, locale filters, CSRF, TOCTOU races, i18n/RTL regressions, O(n²) patterns. | `kilo-context-review` |
| **github** | DeepSeek V4 Flash (no-thinking) | Pipeline terminus. Creates well-formed PRs after all quality gates pass. | `kilo-context-github` |

Plus two auxiliary agents:

- **debug** — diagnostics and exploration (no pipeline role)
- **orchestrator** — agent routing and dispatching (no pipeline role, potentially redundant with plan)

All model bindings are in `~/.config/kilo/kilo.jsonc`. All agent prompts are in `.kilo/agent/*.md` (version controlled).

---

## 4. How Do They Work Together?

### The Pipeline (from `plan.md`)

```
user → plan ──┬──→ architect → code → review → github
              ├──→ designer → site-builder → code → review → github
              ├──→ site-builder → code → review → github
              ├──→ plugin-builder → code → review → github
              └──→ code → review → github  (direct bug fix)
```

### Collaboration Mechanism: The Three-Layer Handoff

Each agent transition uses a **three-layer bridge**:

1. **`ov_session_commit`** — archives the current agent's session to persistent memory (vertical plane)
2. **`ov_add_memory`** — writes a structured handoff document to OpenViking's shared `viking://resources/` (horizontal plane, formatted for the downstream agent)
3. **`switch_mode`** — transfers execution to the next agent in the pipeline

The downstream agent, on activation, calls `ov_session_get_or_create` to recover its own history, then `ov_find("handoff {agent}")` to find the incoming handoff document.

### Quality Gates (enforced by code agent)

Before code hands off to review:

- `pnpm --silent lint:quick` → zero diagnostics
- `pnpm typecheck` → no errors
- `pnpm format` → applied
- `pnpm test` → all passing
- Changeset present if `packages/` changed

### Context Flow

Every agent loads context before responding, and the full AGENTS.md (671 lines) is injected into every agent's system prompt — giving all agents shared domain knowledge about EmDash's architecture, patterns, and constraints.

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

#### Gap 1: Pipeline Mechanics — No Error Recovery

The pipeline is strictly linear: architect → code → review → github. There is **no defined path for review rejection**. When review finds bugs:
- It switches to `code` for fixes
- But code then hands off back to review
- There's no loop detection or state tracking to prevent infinite review→fix→review cycles

The handoff documents don't carry a retry counter or iteration index. A persistent bug class could cycle indefinitely.

**Severity: MEDIUM** — doesn't block basic flows, but lacks guardrails for complex PRs.

#### Gap 2: No CI/CD Gating Hook

The review agent checks 127 items, but the **github agent** also runs lint checks before creating the PR. This is redundant — the code agent already verified lint. But more importantly, **neither agent verifies that CI actually passes.** The github agent creates the PR and reports the URL, but doesn't poll CI status or handle CI failure.

**Severity: MEDIUM** — a red CI PR is created without the pipeline knowing.

#### Gap 3: The Designer → Site-Builder Gap Is the Weakest Link

The designer agent runs on Qwen3.6-35B, a vision-capable model. It produces a Design Brief. The site-builder agent on DeepSeek Flash implements it. But:

- **The designer cannot verify its output.** Qwen has no browser access. The designer produces a brief, hands it off, and never sees the result.
- **No visual feedback loop.** There's no mechanism for taking a screenshot of the built site and feeding it back to the designer for iteration.
- **The brief format is untested.** There are zero examples of designer→site-builder handoffs in the archives, suggesting this pipeline path has never been exercised end-to-end.

**Severity: HIGH** — this pipeline path is theoretically complete but practically unvalidated.

#### Gap 4: No Schema/Seed Validation in the Pipeline

The site-builder builds pages and seed files, but seed validation (`npx emdash seed seed/seed.json --validate`) is in the `seed-site` slash command — not in any quality gate. The code agent checks lint/typecheck/tests, but doesn't validate the seed file. A seed with a mismatched taxonomy name (e.g., `categories` vs `category`) would pass the pipeline and only fail at runtime on the Astro site.

**Severity: MEDIUM** — runtime failures bypass lint and typecheck.

#### Gap 5: ATS Is Designed But Not Integrated into the Pipeline

The `.kilo/architecture/ats-vision.md` is a 349-line design document covering the full ATS architecture (7 collections, pipeline stages, Durable Object agents, Workers AI with LoRA adapters). But there is **no agent in the team with ATS-specific skills**. No agent loads Cloudflare Durable Object patterns, Workers AI patterns, or LoRA training patterns. The architect has ATS domain knowledge in its prompt, but the implementing agents don't.

**Severity: MEDIUM** — the ATS work will require improvised patterns unless skills are created first.

#### Gap 6: No Cross-Agent Testing

Quality gates test code correctness. They do not test **agent collaboration correctness**. There's no integration test that verifies:
- An architect design can be consumed by code without ambiguity
- A designer brief can be consumed by site-builder without guesswork
- A review handoff back to code is formatted correctly for downstream consumption

**Severity: LOW** — would detect handoff format drift before it causes real failures.

#### Gap 7: The Handoff Protocol Is Fragile for Parallel Pipelines

The handoff uses `.kilo/handoff/current.md` as a fallback, but:
- It's overwritten on every handoff — only one handoff in flight at a time
- If two pipelines run concurrently (e.g., a core change + a site change), the handoff file is a shared bottleneck with last-write-wins semantics
- The `ov_find("handoff {agent}")` search is imprecise — if multiple handoffs accumulate without being consumed, there's no FIFO guarantee

**Severity: LOW** — only relevant in parallel pipeline scenarios, which are rare.

#### Gap 8: No Active Pipeline Monitoring

The `agent-manager.json` tracks sessions and worktrees, but there's no dashboard or health check that shows:
- Which pipelines are currently active
- Who is blocked waiting for whom
- How many review→fix cycles a PR has gone through
- Memory/stats drift across agents

**Severity: LOW** — operational visibility gap, not a correctness gap.

#### Gap 9: Skills Are Agent-Local but Not Compositionally Shared

The skills system is designed for agent-specific loading. But there's no mechanism for **cross-agent skill composition**. For example, `building-emdash-site` is loaded by site-builder, but the architect might need a subset of it to validate cross-layer impact. The architect currently has to maintain duplicate EmDash domain knowledge inline.

**Severity: LOW** — works, but duplicates knowledge and creates drift risk.

#### Gap 10: No Agent Upgrades or Rotation Strategy

Agents run on specific models (V4 Pro, V4 Flash, Qwen). There's no documented process for:
- Upgrading models when new versions arrive
- Rotating a model out when it degrades
- Comparing agent performance across model versions
- Fallback models if a primary model is unavailable

**Severity: LOW** — production concern, not an immediate issue.

---

## 6. Resolved Issues (Since Last Audit)

Two bugs from the April 27 audit were fixed:

| Bug | File | Status |
|---|---|---|
| MCP endpoint swap (ov_find ↔ ov_search) | `.kilo/mcp/openviking_server.py` | **FIXED** |
| Duplicate Handoff Protocol section | `.kilo/agent/designer.md` | **FIXED** |

---

## 7. Summary Assessment

The agent team is **well-architected on paper** — roles are clear, handoffs are formal, quality gates are extensive. The weakest points are:

1. **The pipeline has never been tested end-to-end for complex paths** (particularly designer→site-builder)
2. **Error recovery is ad-hoc** — no iteration tracking, no loop detection
3. **Cross-agent validation is missing** — seed files, ATS patterns, visual feedback loops

The team is ready for **basic feature work** (core code → review → PR) but is **unproven for complex cross-layer changes** that span core + templates + plugins + ATS. The next milestone should be an end-to-end smoke test of each pipeline path.

---

## 8. Recommended Next Actions (Priority Order)

| Priority | Action | Owner |
|---|---|---|
| P0 | End-to-end smoke test of architect→code→review→github path | plan |
| P0 | End-to-end smoke test of site-builder→code→review→github path | plan |
| P1 | Create seed validation quality gate in code agent | plan |
| P1 | Add review iteration counter to handoff (reject→fix→review loop) | plan |
| P2 | End-to-end smoke test of designer→site-builder→code→review→github path | plan |
| P2 | Create ATS-specific skill document (`ats-development`) | architect |
| P2 | Add CI polling to github agent (post-PR status check) | plan |
| P3 | Add pipeline monitoring dashboard or health check | plan |
| P3 | Implement skill composition for cross-agent reuse | plan |
| P3 | Document model upgrade/rotation process | plan |
