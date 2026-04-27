---
name: openviking-agent-config
description: "Standard configuration pattern for Kilo agents using OpenViking memory. Provides session lifecycle (get_or_create → work → commit), tool selection guide (find vs search, add_memory scope), pattern persistence protocol, and fallback behavior. Use when creating a new agent, auditing agent configuration, or updating multi-agent memory patterns."
---

# OpenViking Agent Configuration

Standard configuration pattern for Kilo agents using OpenViking session-aware memory. Encodes the session lifecycle, tool selection rules, memory persistence protocol, and fallback behavior established across the architect, code, review, site-builder, plugin-builder, plan, and designer agents.

---

## Getting Started

> **Transport:** Our agents connect to OpenViking via HTTP SSE mode (`openviking-server` on port 1933). This is the recommended transport for multi-agent setups. stdio mode causes lock contention with multiple concurrent sessions. See `references/ov-mcp-integration.md`.

### Session Bookmark Block

Every agent prompt must include this block. Replace `{agent_name}` with the agent's name (e.g., `code`, `review`, `architect`).

**This block is a NON-NEGOTIABLE hard gate.** The agent MUST NOT respond to the user until all three memory reads complete. No greeting, no acknowledgement, no partial response — memory first, always.

On session start the agent must:
1. Call `ov_session_get_or_create` — loads vertical memory (last session decisions, open questions, next steps)
2. Call `ov_find("{previous_agent} handoff {agent_name}")` — loads horizontal memory (incoming handoff from upstream agent)
3. Only then confirm context to the user and proceed

```markdown
## Session Bookmark

**HARD GATE — do not respond to the user until all memory reads complete.**

**On session start, execute in order before anything else:**
1. Call `ov_session_get_or_create("kilo-context-{agent_name}", agent_id="{agent_name}")` — loads your vertical memory (prior session decisions, open questions, next steps). If it fails (OpenViking down), fall back to reading `.kilo/handoff/current.md`.
2. Call `ov_find("handoff {agent_name}")` — loads horizontal memory (incoming handoff from the upstream agent).
3. Confirm context loaded to the user: summarise last session state + any incoming handoff. Only then proceed.

**Before session end:** Call `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")`. Then write a brief handoff to `.kilo/handoff/current.md` with just the session_id, task_id, and archive count.
```

### Context Gathering Block

Teaches the agent to use the right search tool for the right job.

```markdown
## Context Gathering with OpenViking MCP

You have access to OpenViking MCP tools that index the full project knowledge base (AGENTS.md, all skills, agent prompts, commands, plans, and handoffs).

**Before reading files or implementing:**
1. Use `ov_find("exact term")` for known names, patterns, or code references (fast, FTS, no session context needed)
2. Use `ov_search("conceptual task")` for complex tasks, problem-solving, or discovering relevant patterns
3. Read L0 abstracts from results before loading full files
4. If no results, proceed with file-based discovery

Use `ov_find` first — it's faster. Use `ov_search` when you need semantic understanding.
```

### Memory Persistence Block

Two paths: automatic (session commit) and manual (`ov_add_memory`).

**For all agents (auto path):**

```markdown
**Auto:** `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")` at end.
```

**For code and review agents** (manual path with pattern trigger):

```markdown
**Manual:** `ov_add_memory(content, agent_id="{agent_name}")` for key decisions, gotchas, or reusable solutions. REQUIRED after: bug fixes, security vulns, perf fixes, or schema workarounds. Stores in shared resources (searchable by all agents). Format:
```
## Pattern: [one-line]
Root cause: [why]
Detection: [grep/sql to find others]
Fix: [idiomatic solution]
```
```

**For other agents** (manual path, decision format):

```markdown
**Manual:** `ov_add_memory(content, agent_id="{agent_name}")` for key decisions, gotchas, or reusable solutions. Format: `## Decision: [Topic]\nDate: YYYY-MM-DD\n\n[2-3 sentences.]`
```

### Complete Output Template

Copy-paste ready prompt block for a new agent. Sections MUST appear in this exact order — this is enforced, not advisory:

```
1. Session Bookmark    ← HARD GATE: memory reads before any response
2. Context Gathering   ← ov_find/ov_search before any file access
3. Role Definition     ← identity, informed by loaded memory
4. Memory              ← persistence rules (auto + manual)
5. Handoff Protocol    ← commit → persist → switch_mode
6. Domain Rules        ← agent-specific instructions
```

```markdown
## Session Bookmark

**HARD GATE — do not respond to the user until all memory reads complete.**

**On session start, execute in order before anything else:**
1. Call `ov_session_get_or_create("kilo-context-{name}", agent_id="{name}")` — loads your vertical memory (prior session decisions, open questions, next steps). If it fails (OpenViking down), fall back to reading `.kilo/handoff/current.md`.
2. Call `ov_find("handoff {name}")` — loads horizontal memory (incoming handoff from the upstream agent).
3. Confirm context loaded to the user: summarise last session state + any incoming handoff. Only then proceed.

**Before session end:** Call `ov_session_commit("kilo-context-{name}", agent_id="{name}")`. Then write a brief handoff to `.kilo/handoff/current.md` with just the session_id, task_id, and archive count.

## Context Gathering with OpenViking MCP

You have access to OpenViking MCP tools that index the full project knowledge base (AGENTS.md, all skills, agent prompts, commands, plans, and handoffs).

**Before reading files or implementing:**
1. Use `ov_find("exact term")` for known names, patterns, or code references (fast, FTS, no session context needed)
2. Use `ov_search("conceptual task")` for complex tasks, problem-solving, or discovering relevant patterns
3. Read L0 abstracts from results before loading full files
4. If no results, proceed with file-based discovery

Use `ov_find` first — it's faster. Use `ov_search` when you need semantic understanding.

This saves context tokens and gets you to the right information faster. Search first, read files second.

# Role: {Agent Display Name}

{Role definition — who the agent is, what it does, its constraints.}

## Memory

**Auto:** `ov_session_commit("kilo-context-{name}", agent_id="{name}")` at end.

**Manual:** `ov_add_memory(content, agent_id="{name}")` for key decisions, gotchas, or reusable solutions. [For code/review agents: REQUIRED after bug fixes, security vulns, perf fixes, or schema workarounds. Format:
```
## Pattern: [one-line]
Root cause: [why]
Detection: [grep/sql to find others]
Fix: [idiomatic solution]
```
For all other agents: Format: `## Decision: [Topic]\nDate: YYYY-MM-DD\n\n[2-3 sentences.]`]

## Handoff Protocol

When your task phase is complete, execute in order:

**Step 1:** Call `ov_session_commit("kilo-context-{name}", agent_id="{name}")`.

**Step 2:** Call `ov_add_memory(content, agent_id="{name}")` with:
```
## Handoff: {name} → {next_agent}
Date: [current date]

### Summary
[What was done, key decisions, rationale]

### Files Affected
- [paths]

### Open Questions
- [Any unresolved issues]
```

**Step 3:**
```
<switch_mode>
<mode_slug>{next_agent}</mode_slug>
<reason>[One-line summary]</reason>
</switch_mode>
```

## Domain Rules

{Agent-specific rules, constraints, output formats.}
```

---

## API

### Tool Selection Guide

| Tool | When | Latency | Session Context | Algorithm |
|---|---|---|---|---|
| `ov_find("exact term")` | Known names, code references, grep-style lookups | Low | Not needed | PostgreSQL FTS |
| `ov_search("conceptual")` | Complex tasks, problem-solving, discovering patterns | Higher | Required | LLM intent analysis → hierarchical vector search → rerank |
| `ov_session_get_or_create(...)` | Session start | Low | Creates it | Loads last archive overview + pre-archive abstracts |
| `ov_session_commit(...)` | Session end | Phase 1: sync (~12ms), Phase 2: async (~8s) | Updates it | Archive messages + LLM memory extraction |
| `ov_add_memory(content, agent_id)` | Mid-session | Low (write), async (vectors) | Uses current | Stores in `viking://resources/` (shared space) |

### MCP Tools to HTTP Endpoints

| MCP Tool | HTTP Endpoint | Method |
|---|---|---|
| `ov_status` | `/api/v1/system/status` | GET |
| `ov_ls` | `/api/v1/fs/ls` | GET |
| `ov_tree` | `/api/v1/fs/tree` | GET |
| `ov_read` | `/api/v1/content/read` | GET |
| `ov_abstract` | `/api/v1/content/abstract` | GET |
| `ov_overview` | `/api/v1/content/overview` | GET |
| `ov_search` | `/api/v1/search/search` | POST |
| `ov_find` | `/api/v1/search/find` | POST |
| `ov_grep` | `/api/v1/search/grep` | POST |
| `ov_add_resource` | `/api/v1/resources` | POST |
| `ov_add_memory` | `/api/v1/resources` (via temp_upload + add_resource) | POST |
| `ov_session_get_or_create` | `/api/v1/sessions` + `/api/v1/sessions/{id}` | POST + GET |
| `ov_session_commit` | `/api/v1/sessions/{id}/commit` | POST |
| `ov_session_add_message` | `/api/v1/sessions/{id}/messages` | POST |

### Error Codes

| Code | HTTP | Impact |
|---|---|---|
| `PERMISSION_DENIED` | 403 | Cross-agent namespace access blocked |
| `NOT_FOUND` | 404 | Namespace not yet created (expected before first commit) |
| `UNAUTHENTICATED` | 401 | Server auth issue |
| `SESSION_EXPIRED` | 410 | Re-create session |

---

## Concepts

### Storage Tiers

| Tier | URI Prefix | Visibility | Content |
|---|---|---|---|
| Shared resources | `viking://resources/` | All agents | Project knowledge, plans, handoffs, patterns via ov_add_memory |
| Shared user memories | `viking://user/agentcafe/memories/` | All agents | Preferences, entities, events (auto-extracted from session commits) |
| Agent-scoped memories | `viking://agent/{name}/memories/` | Only that agent (403) | Cases, patterns (auto-extracted from that agent's sessions) |
| Agent skills | `viking://agent/{name}/skills/` | Only that agent | Skill registries |

### URI Architecture

```
viking://
├── resources/              # Resources: project docs, code repos, web pages
│   └── work/emdash/        #   Project context
├── user/                   # User: preferences, habits
│   └── agentcafe/memories/ #   User memories
└── agent/                  # Agent: skills, instructions, task memories
    ├── architect/          #   Architect namespace
    │   ├── instructions/
    │   └── memories/
    ├── code/               #   Code agent namespace
    └── .../
```

### Content Levels (L0/L1/L2)

| Level | Name | Token Limit | Purpose |
|---|---|---|---|
| L0 | Abstract | ~100 tokens | Vector search, quick filtering |
| L1 | Overview | ~2K tokens | Rerank, content navigation |
| L2 | Detail | Unlimited | Full content, on-demand loading |

### Extraction Pipeline

```
ov_add_memory / session_commit
    ↓
Parser (sync, no LLM) → splits into ≤1024 token chunks
    ↓
TreeBuilder (sync) → moves to AGFS, queues for processing
    ↓
SemanticQueue (async, LLM) → generates L0 abstracts, L1 overviews, vectors
    ↓
Searchable via ov_find (immediate, FTS) + ov_search (after vectors built)
```

### Six Memory Categories

| Category | Owner | Mergeable | Description |
|---|---|---|---|
| profile | user | Yes | User identity/attributes |
| preferences | user | Yes | User preferences by topic |
| entities | user | Yes | Entities (people/projects) |
| events | user | No | Event records (decisions, milestones) |
| cases | agent | No | Learned problem/solution records |
| patterns | agent | Yes | Reusable best practices |

### Access Control

- `ov_search` and `ov_find` search all tiers the agent has permission to see
- Results tagged with `context_type`: `memory` (user or agent), `resource`, `skill`
- Cross-agent access to `viking://agent/{other}/` returns 403
- `ov_add_memory` stores in `viking://resources/` — all agents can find it
- `agent_id` parameter controls processing namespace, not storage location
- Agent namespaces are lazily created on first `ov_session_commit`

### Crash Recovery

| Crash Point | State | Recovery |
|---|---|---|
| During Phase 1 archive write | No redo marker | Incomplete archive; next commit rescans, unaffected |
| Phase 1 complete, messages not cleared | No redo marker | Archive complete + messages still present = redundant but safe |
| During Phase 2 memory extraction | Redo marker exists | LockManager.start() re-executes extraction from archive |
| After enqueue, before worker | QueueFS SQLite persists | Worker auto-pulls after restart |
| Process crash holding lock | Lock file remains | Stale detection auto-cleans after 300s default expiry |

---

## Guides

### Design Notes — Why This Skill Works

This skill was validated across 7 agents in the EmDash monorepo (architect, code, review, site-builder, plugin-builder, plan, designer) using DeepSeek V4 models. The agents successfully load prior session context, search shared and agent-scoped memories, persist discovered patterns, and commit session history. Key success factors:

1. **Single source of truth.** All 10 agent prompt entry points (`kilo.jsonc` + `.kilo/agent/*.md`) now reference the same pattern. Changes propagate to all agents in one edit.
2. **Gotchas are the highest-value content.** `ov_add_memory` stores in shared resources not agent-scoped memory, `ov_find` is faster than `ov_search` for exact terms, session bookmark must execute before any greeting. These non-obvious behaviors cause failures if undocumented.
3. **Output template anchors quality.** A concrete agent prompt block gives agent creators a target to pattern-match. Generic descriptions of the session lifecycle aren't enough.
4. **Tool selection is explicit.** `ov_find` vs `ov_search` is not guessable from tool names. The skill names the rule: find first for exact terms, search for semantic queries.
5. **Fallback path is documented.** When OpenViking is down, agents fall back to `.kilo/handoff/current.md`. Without this, agents stall on startup.
6. **Length target respected.** Fits alongside agent prompt and AGENTS.md without crowding.

### When to Use

USE this skill when:
- Creating a new Kilo agent that needs OpenViking memory integration
- Auditing existing agent configurations for memory coverage
- Updating session bookmark, context gathering, or memory persistence patterns across all agents
- Onboarding a new developer to the agent team's memory architecture
- OpenViking MCP server is updated and agent prompts need re-verification

DO NOT use this skill when:
- Debugging OpenViking server issues → check server logs and `ov_status`
- Writing code or implementing features → use the appropriate builder agent
- Designing schemas or architectures → use architect agent

### Prompt Section Ordering (CRITICAL)

**The order of sections in the agent prompt determines behavior.** If Context Gathering appears after Role/Core Behaviors, the agent will skip OV search and act on its identity priming. This has been reproduced across architect, code, and plan agents.

**MANDATORY order for all agent prompts:**

```
1. Session Bookmark          ← HARD GATE: ov_session_get_or_create + ov_find handoff BEFORE any response
2. Context Gathering         ← ov_find/ov_search before any file access
3. Role Definition           ← identity, now informed by loaded memory
4. Memory                    ← persistence rules (auto + manual)
5. Handoff Protocol          ← commit → persist → switch_mode
6. Domain Rules              ← agent-specific instructions
```

**Never place Context Gathering after Role Definition.** The agent must be told to search BEFORE being told "you are the lead architect, be decisive."

### Procedure

1. **Verify transport mode** — ensure the MCP server connects via HTTP SSE (not stdio). Multi-agent stdio causes lock contention.
2. **Define the agent's session ID** — `kilo-context-{agent_name}`, matching the `agent_id` parameter
3. **Add session bookmark block** — `ov_session_get_or_create` at start, `ov_session_commit` at end
4. **Add context gathering block** — `ov_find` for exact terms, `ov_search` for semantic queries. Place IMMEDIATELY after Session Bookmark, before any role definition.
5. **Add memory persistence block** — auto path (session commit), manual path (`ov_add_memory`)
6. **Add pattern persistence trigger** — REQUIRED for code/review agents after bug fixes, vulns, perf fixes
7. **Add handoff fallback** — `.kilo/handoff/current.md` when OpenViking is unreachable
8. **Verify section ordering** — Context Gathering MUST appear before Role. If Role comes first, reorder.
9. **Verify isolation** — confirm the agent's `agent_id` cannot access other agents' `viking://agent/{name}/` namespaces

### Validation Loop

1. **Check session bookmark** — does the agent call `ov_session_get_or_create` before any greeting? Is `agent_id` correct?
2. **Check context gathering** — does the agent know to use `ov_find` first, `ov_search` for semantic queries?
3. **Check section ordering** — does Context Gathering appear BEFORE Role Definition? If Role comes first, the agent will skip OV search (confirmed bug across architect, code, plan agents).
4. **Check memory persistence** — does the code/review agent have the REQUIRED pattern trigger?
5. **Check fallback** — is `.kilo/handoff/current.md` referenced as fallback?
6. **Check isolation** — if a new agent, verify `ov_ls` on another agent's namespace returns 403
7. **If any check fails**, the agent prompt is incomplete. Add the missing block or reorder sections.
8. **Once all checks pass**, the agent is ready for memory-integrated operation.

### Gotchas

- **Prompt section ordering is behavioral.** Context Gathering MUST appear before Role Definition. If Role comes first, the agent's identity priming ("you are the lead architect, be decisive") overrides the OV search instruction — the agent skips search and acts directly. Reproduced across architect, code, and plan agents. The section order is: Session Bookmark → Context Gathering → Role → everything else.
- **`ov_add_memory` stores in shared resources, not agent memory.** The `agent_id` parameter controls processing pipeline routing, not storage location. Explicit `viking://agent/` URIs are rejected. Memories written by one agent are searchable by all agents.
- **Session bookmark must run before any greeting.** The `ov_session_get_or_create` call loads prior context. If the agent greets first, it has no awareness of prior decisions or open questions.
- **`ov_find` is faster than `ov_search`.** `ov_find` uses PostgreSQL FTS with no session context overhead. `ov_search` uses LLM intent analysis + hierarchical vector search + rerank. Use `ov_find` for exact term lookups.
- **Agent namespaces are lazily created.** A `viking://agent/{name}/` namespace only appears after the agent's first `ov_session_commit`. Before that, `ov_ls` returns 404. This is expected, not an error.
- **`agent_id` must match session ID convention.** Session `kilo-context-architect` expects `agent_id="architect"`. Mismatched IDs cause cross-contamination.
- **Extraction is async.** After `ov_session_commit` or `ov_add_memory`, memories may take seconds to minutes before they're searchable via `ov_search`. `ov_find` works immediately (FTS).
- **Handoff file is the fallback.** If `ov_session_get_or_create` fails (OpenViking down), read `.kilo/handoff/current.md`. The file is overwritten each session — it contains last session's decisions, not full history.
- **Memory extraction is tunable.** OV supports custom prompt templates for `compression.memory_extraction` and `compression.dedup_decision` to control what gets extracted and how duplicates are handled. Custom memory schemas can encode domain-specific patterns (e.g., EmDash patterns with source file, code pattern, and fix fields). See `references/ov-prompt-customization.md` for details.

## References

### Project Files

- `AGENTS.md` — project constitution with code patterns and conventions
- `~/.config/kilo/kilo.jsonc` — global agent prompt configuration
- `.kilo/agent/*.md` — project-level agent prompt overrides
- `.kilo/handoff/current.md` — session handoff file (fallback when OpenViking is down)

### OpenViking Reference Documentation

- `references/ov-quick-start.md` — installation, Docker setup, configuration, model requirements
- `references/ov-server-mode.md` — HTTP server, client connections, cloud deployment
- `references/ov-configuration.md` — ov.conf sections, embedding, VLM, storage configuration
- `references/ov-api-overview.md` — connection modes, response formats, error codes, endpoint inventory
- `references/ov-mcp-integration.md` — MCP transport modes (HTTP SSE vs stdio), tool inventory, troubleshooting
- `references/ov-prompt-customization.md` — memory extraction tuning, custom memory schemas, dedup customization
- `references/ov-architecture.md` — product philosophy, URI architecture, context types, memory categories
- `references/ov-architecture-overview.md` — system architecture, core modules, data flow, design principles


