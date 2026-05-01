# OV Three-Pillar Audit — 2026-05-01

> Full audit of OpenViking Resource, Memory, and Skill pillars against OV v0.3.14 intended design. Produced from indexed OV KB (41 docs) cross-referenced against live `ov_tree`/`ov_stats`/`ov_search` data.

---

## Executive Summary

| Pillar       | Grade | One-Sentence Assessment                                                                                                                                                                        |
| ------------ | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Resource** | B     | Well-indexed knowledge base with good L0/L1/L2 coverage, but has stale duplicates, missing cross-links, and kb/work namespace fragmentation.                                                   |
| **Memory**   | D     | Session extraction works, but only architect has agent-scoped data; patterns/cases/profile are empty; zero "hot" memories; soul/identity are unfilled templates.                               |
| **Skill**    | F     | ZERO skills registered as invocable capabilities. All 14 skills exist on disk but are indexed as Resources (passive docs), not as Skills (active capabilities). Agent-skill binding is absent. |

**Overall**: We use OV as a **searchable document store** (Resource pillar), not as a **three-pillar agent brain**. Memory and Skill pillars are effectively dead.

---

## Pillar 1: Resources — Grade B

### OV Docs Prescription

> "Resources are external knowledge that Agents can reference. User-driven, long-term, relatively static. Organized by project or topic in directory hierarchy with multi-layer information extraction."

### Current State

| Metric                 | Value                                 |
| ---------------------- | ------------------------------------- |
| Root trees             | 2 (`kb/` + `work/`)                   |
| EmDash-specific docs   | ~60 entries under `work/emdash/kilo/` |
| Code patterns indexed  | 14 (all have L0 + L1, most have L2)   |
| OV docs indexed        | 41 pages under `openviking-docs/`     |
| Agent docs indexed     | 5 agent files as resources            |
| Plans indexed          | 2 plans                               |
| Handoff docs indexed   | 5 handoff records                     |
| Architecture decisions | 40+ timestamped entries               |

### Strengths

1. **Code pattern library is production-grade.** 14 patterns (SQL, pagination, migrations, RTL, CSRF, error handling, Kumo components, Lingui, etc.) with full L0/L1/L2 across all 14. This is the strongest single asset.
2. **OV KB is current.** 41 docs from docs.openviking.ai re-indexed to v0.3.12 on 2026-05-01. Fresh and searchable.
3. **Decisions are timestamped.** Architecture decisions follow `memory-YYYY-MM-DD-HHMMSS-{uuid}.md` naming convention, consistently applied.

### Critical Issues

#### 1. KB Duplication — `kb/kilo/` vs `work/emdash/kilo/`

Two separate trees cover Kilo Code knowledge. `viking://resources/kb/kilo/` (46 docs from VS Code extension) and `viking://resources/work/emdash/kilo/` (60+ EmDash-specific docs) overlap on agent config, commands, and patterns. Agents searching for "agent prompt section order" get results from both trees with different freshness.

**Fix**: Consolidate. Move stale `kb/kilo/` entries into `work/emdash/kilo/` or delete the kb/ tree entirely (it was indexed pre-emdash in April 2026).

#### 2. OV Docs in Wrong Namespace

`viking://resources/work/emdash/openviking-docs/` — OpenViking documentation is a reference resource, not EmDash work product. It should be under `kb/openviking/` or `resources/openviking/`.

**Fix**: Move to `viking://resources/openviking-docs/` (no namespace pollution).

#### 3. Zero Cross-Links via Relations API

40+ architecture decisions, 14 code patterns, 5 handoff docs — and ZERO `ov_link` relations between them. A decision about "ATS uses Content API" should link to the Content Table Lifecycle code pattern. The handoff "architect-to-code-test.md" should link to the pagination pattern.

**Fix**: Create a maintenance habit: when storing a decision, link it to its code patterns. When storing a handoff, link it to the design it implements.

#### 4. Stale Test Data

`viking://resources/test-reason/download.md` — 154 bytes, from 2026-04-29, was a test upload. Still present. This is cruft.

**Fix**: Delete it.

#### 5. No L0 Abstracts on Event Directories

`viking://user/agentcafe/memories/events/2026/04/27` through `05/01` all return "[Directory abstract is not ready]". The pipeline is supposed to generate these automatically.

**Fix**: Trigger `ov_reindex` on the events tree.

### Optimization Roadmap

| #   | Priority | Action                                                               | Effort        |
| --- | -------- | -------------------------------------------------------------------- | ------------- |
| R1  | P1       | Delete `viking://resources/test-reason/`                             | 1 min         |
| R2  | P1       | Consolidate `kb/kilo/` into `work/emdash/kilo/` or delete            | 10 min        |
| R3  | P2       | Move `openviking-docs/` to `viking://resources/openviking-docs/`     | 5 min         |
| R4  | P2       | Create `ov_link` relations: decisions → patterns, handoffs → designs | Ongoing habit |
| R5  | P3       | Run `ov_reindex` on events tree for missing abstracts                | 2 min + async |

---

## Pillar 2: Memory — Grade D

### OV Docs Prescription

> "Memories are divided into user memories and agent memories, representing learned knowledge about users and the world. Agent-driven, dynamically updated from interactions. 8 categories with specific update strategies (merge, append, no-update)."

### Current State

| Metric                        | Value                       |
| ----------------------------- | --------------------------- |
| Total memories                | 44                          |
| By category: preferences      | 6                           |
| By category: entities         | 8                           |
| By category: events           | 21                          |
| By category: tools            | 4                           |
| By category: skills           | 5                           |
| By category: profile          | **0**                       |
| By category: cases            | **0**                       |
| By category: patterns         | **0**                       |
| Hotness: hot                  | **0**                       |
| Hotness: warm                 | 44                          |
| Agents with agent-scoped data | **1 of 8** (architect only) |

### Strengths

1. **Session extraction pipeline works.** 44 memories across 64 sessions (archives 001-030) means ~1.47 memories per session — the pipeline is extracting, just slowly.
2. **Event timeline functional.** Year/month/day directory hierarchy correctly organizes 21 event records.
3. **Tool tracking started.** 4 tool memories (search.md, read.md) in `agent/architect/memories/tools/`.

### Critical Issues

#### 1. Only Architect Learns — Seven Agents Are Amnesiac

`viking://agent/` contains only `architect/`. The code, review, site-builder, plugin-builder, designer, plan, and github agents have no agent-scoped memories, cases, or patterns. Every session, they start from zero.

**Root cause**: `ov_session_commit` extracts memories to `viking://user/agentcafe/memories/` (shared user space), not agent-scoped `viking://agent/{name}/memories/`. The `role_id` field exists in `session_add_message` but the extraction pipeline doesn't route to agent namespaces.

**Fix**: The OV docs say agent memories go to `viking://agent/{name}/memories/`. We need to verify if v0.3.14 supports agent-scoped extraction, or if we need to manually `ov_add_memory` with agent-specific URIs after each session.

#### 2. Three Categories Are Dead — profile, cases, patterns = 0

OV prescribes 8 categories with specific update strategies. We use 4 (preferences, entities, events, tools/skills). The most valuable categories for agent improvement — **cases** (specific problems + solutions) and **patterns** (reusable best practices) — are completely empty.

**Impact**: The architect agent has diagnosed 10+ bugs (ov_grep GET→POST, ov_unlink DELETE, host.docker.internal DNS, session archive staleness, lock contention, API key root vs user, prompt section ordering, etc.) but stored **zero** as learnable cases. The next architect session will hit the same errors with no recall.

#### 3. soul.md and identity.md Are Unfilled Templates

```
# identity.md - Who Am I?
_Fill this in during your first conversation. Make it yours._
- **Name:** architect
- **Creature:**        ← EMPTY
```

The soul.md file is generic "be helpful, be concise" boilerplate — zero EmDash-specific personality, no accumulated wisdom, no project history.

#### 4. Duplicate Memory Files

`cloudflare_workers_dev.md` and `cloudflare-workers-dev.md` are likely identical content under different filenames. Same for `workers_ai_patterns.md` / `workers-ai-patterns.md`. This is data corruption — OV's FTS will return both, wasting context tokens.

#### 5. Zero Hot Memories

All 44 memories are "warm" — none have been accessed frequently enough to reach "hot" status. This confirms that agents don't retrieve memories during sessions. The memory loop is write-only: commit extracts → stores → never reads.

#### 6. Events Category Dominates (48% of All Memories)

21 of 44 memories are events — raw session transcript summaries. Events have "no update" strategy per OV docs — they're immutable historical records. But they're treated as the primary memory type, crowding out higher-value categories (cases, patterns).

### Optimization Roadmap

| #   | Priority | Action                                                                                                                                   | Effort                 |
| --- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| M1  | 🔴 P0    | Manually store top 5 bugs as **cases** (`ov_add_memory` → `viking://agent/architect/memories/cases/{bug-name}.md`)                       | 15 min                 |
| M2  | 🔴 P0    | Manually store top 5 design decisions as **patterns** (`ov_add_memory` → `viking://agent/architect/memories/patterns/{pattern-name}.md`) | 15 min                 |
| M3  | 🔴 P0    | Fill `soul.md` with EmDash architect-specific identity: role, project history, key constraints, known pitfalls                           | 10 min                 |
| M4  | 🔴 P0    | Fill `identity.md` with actual agent identity                                                                                            | 5 min                  |
| M5  | 🟡 P1    | Enable agent-scoped memory extraction for all 8 agents (verify OV v0.3.14 capability or implement post-commit manual routing)            | Investigation + 30 min |
| M6  | 🟡 P1    | Delete duplicate memory files (`cloudflare_workers_dev`, `workers_ai_patterns` variants)                                                 | 5 min                  |
| M7  | 🟡 P1    | Add "Search OV for related memories before starting" to all agent prompts                                                                | 10 min per agent       |
| M8  | 🟢 P2    | Rebalance extraction toward cases/patterns — post-session, the architect should manually store 1-2 learnings per session                 | Ongoing habit          |

---

## Pillar 3: Skill — Grade F

### OV Docs Prescription

> "Skills are capabilities that Agents can invoke. Defined capabilities, relatively static, callable. Agent decides when to use which skill. Stored at `viking://agent/skills/{skill-name}/` with L0 abstract, L1 SKILL.md, and L2 full definition."

### Current State

| Metric                                        | Value                                                      |
| --------------------------------------------- | ---------------------------------------------------------- |
| Skills on disk (filesystem)                   | 14                                                         |
| Skills registered in OV via `ov_add_skill`    | **0**                                                      |
| Agent skill bindings                          | **0 of 8 agents**                                          |
| Skills found via `ov_find("skill")` as Skills | 0 (only as Resources)                                      |
| Skill search returns                          | Generic ".abstract.md" files with "Agent's skill registry" |

### Strengths

1. **14 high-quality skills exist on disk.** `adversarial-reviewer`, `building-emdash-site`, `creating-plugins`, `cloudflare-agents-sdk`, `cloudflare-durable-objects`, etc. are well-documented with SKILL.md format.
2. **`ov_add_skill` tool is implemented** in the MCP bridge (lines 380-458 of `openviking_server.py`). The capability exists — it's just never been used.
3. **Skills are indexed as Resources.** They're searchable via `ov_find`/`ov_search` — just not through the Skill retrieval path.

### Critical Issues

#### 1. ZERO Skills Registered

Despite 14 skills on disk and the `ov_add_skill` tool being available since 2026-04-29, not a single skill has been registered. Skills exist AS RESOURCES (searchable docs) but NOT AS SKILLS (invocable capabilities indexed under `viking://agent/skills/`).

**What it means**: When an agent calls `ov_search("how to build an emdash site")`, it hits the indexed resource chunks of `building-emdash-site/SKILL.md`. But when it calls `ov_find("skill", target_uri="viking://agent/skills/")`, it gets nothing. The Skill pillar's discovery mechanism is non-functional.

#### 2. Skills Aren't Bound to Agents

OV docs prescribe: `viking://agent/{name}/skills/{skill-name}/`. Currently, `viking://agent/architect/skills/` contains only auto-generated `.abstract.md`. None of the 14 skills are bound to their appropriate agents:

| Skill                        | Should Be Bound To | Currently |
| ---------------------------- | ------------------ | --------- |
| `adversarial-reviewer`       | review             | ❌        |
| `building-emdash-site`       | site-builder       | ❌        |
| `creating-plugins`           | plugin-builder     | ❌        |
| `cloudflare-agents-sdk`      | code, architect    | ❌        |
| `cloudflare-durable-objects` | architect          | ❌        |
| `agent-browser`              | code               | ❌        |
| `emdash-cli`                 | site-builder       | ❌        |
| ... (7 more)                 | ...                | ❌        |

#### 3. Orphaned Cloudflare Skills Are a Known Gap

The 2026-04-30 audit at `viking://user/agentcafe/memories/events/2026/04/30/cloudflare_skill_audit.md` explicitly identified that `cloudflare-agents-sdk` and `cloudflare-durable-objects` are "orphaned — not registered in any agent's skills: []". The code agent implementing `CreationAgent` DO class has zero injected knowledge of the Agents SDK API surface (`Agent` class, `@callable`, `setState`, `this.env`). This gap was identified but never closed.

#### 4. Skill Discovery Uses Wrong Search Path

Agents search for skills as Resources (`ov_search("how to build plugin")`), not as Skills (`ov_find("creating-plugins", target_uri="viking://agent/skills/")`). This means:

- Skills aren't discoverable as a distinct concept type
- Agent can't list "what skills do I have?"
- No skill invocation metadata (when to use, success rates, optimal params)

### Optimization Roadmap

| #   | Priority | Action                                                                                                                                                                                                                                                          | Effort                                                    |
| --- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| S1  | 🔴 P0    | Register all 14 skills via `ov_add_skill(name, description, content)` — one call per skill                                                                                                                                                                      | 30 min                                                    |
| S2  | 🔴 P0    | Bind skills to agents: review ← `adversarial-reviewer`, site-builder ← `building-emdash-site` + `emdash-cli`, plugin-builder ← `creating-plugins`, code ← `agent-browser`, architect ← `cloudflare-durable-objects`, code + architect ← `cloudflare-agents-sdk` | Done as part of S1 (registration auto-places under agent) |
| S3  | 🟡 P1    | Update agent prompts to search Skills pillar first: `ov_find("{skill-name}", target_uri="viking://agent/skills/")`                                                                                                                                              | 5 min per agent                                           |
| S4  | 🟡 P1    | Store skill usage memories in `viking://agent/{name}/memories/skills/` — track success rates, optimal params, when to use                                                                                                                                       | Ongoing habit                                             |
| S5  | 🟢 P2    | Create `ov_list_skills` tool in MCP bridge for agent self-discovery                                                                                                                                                                                             | 30 min                                                    |

---

## Cross-Pillar Synthesis

### What We're Doing Right

1. **Resource pillar is the workhorse.** 14 code patterns, 41 OV docs, 40+ decisions, 5 handoffs — all with full L0/L1/L2 indexing. This is a production-grade knowledge base.
2. **Session pipeline is operational.** 30 archives, 44 memories extracted, 8-category classification active. The plumbing works.
3. **MCP bridge is feature-complete.** 18 tools covering all three pillars — the tools exist, they're just underutilized for Memory and Skill.

### What We're Doing Wrong (Systemic)

1. **We built a search engine, not an agent brain.** Resources (passive knowledge) get all the attention. Memory (active learning) gets session-commit fire-and-forget. Skill (invocable capabilities) gets nothing. The three-pillar design works when all three work together — agents find knowledge (Resources), learn from experience (Memory), and invoke capabilities (Skills). We have only the first.

2. **The memory loop is broken — write-only, never read.** Session commit extracts → stores → never retrieved. All 44 memories are "warm" (medium access), zero "hot" (frequent access). Agents don't search their own memory before starting work.

3. **Agent prompts don't mandate OV retrieval.** The Session Bookmark calls `ov_session_get_or_create` (loads archive summary) but doesn't call `ov_find("pattern related to {task}")` or `ov_search("{concept}"). The code agent starts naive every session (miscellaneous.md §2 documents this).

4. **Skills are a document format, not a system feature.** 14 SKILL.md files with excellent content — but they're loaded as Kilo system prompts, not as OV-invokable capabilities. The Skill pillar's purpose (agent self-discovery, invocation tracking, usage optimization) is completely unused.

### The Fix Is Three Habits

| Habit                  | When                          | What                                                                                                      |
| ---------------------- | ----------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Pre-task search**    | Before ANY agent starts work  | `ov_find("exact term")` + `ov_search("concept")` for related patterns, cases, and decisions               |
| **Post-task capture**  | After ANY agent finishes work | `ov_add_memory` → agent-scoped: cases for bugs fixed, patterns for solutions found, tools for what worked |
| **Skill registration** | Once (now), then maintain     | Register all 14 skills, bind to agents, track usage                                                       |

These three habits convert OV from a search engine to an agent brain. The tools exist. The infrastructure works. The gap is purely operational — we're not using what we built.
