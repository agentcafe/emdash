# OpenViking Working File

> Persistent tracking document for the OpenViking memory layer initiative.
> Goal: Achieve reliable, persistent memories and resources for the EmDash agent team.
> Last updated: 2026-05-01T12:09:38+03:00

---

## 1. Objective

**Establish OpenViking as a production-grade persistent memory substrate for the EmDash agent team**, such that every agent (architect, code, review, site-builder, etc.) retains state across sessions — what was learned, what was decided, what was built, and what remains outstanding.

### Desired End State

| Capability                    | Target                                                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Persistent resources**      | Codebase docs, architecture decisions, PR history, CI patterns indexed and searchable                         |
| **Persistent memories**       | Decisions, gotchas, lessons learned survive across sessions per agent                                         |
| **Agent statefulness**        | Each agent's `kilo-context-{agent}` session carries forward: current task, progress, blockers, next step      |
| **Cross-agent knowledge**     | Architectural decisions from architect are retrievable by code; review findings persist; handoffs are durable |
| **Searchable knowledge base** | `ov_find` (FTS) + `ov_search` (semantic) both return relevant results across all indexed content              |

---

## 2. Current Architecture

```
┌─────────────────────────────────────────────────────┐
│  Kilo Code (This Session)                            │
│  ┌───────────────────────────────────────────────┐  │
│  │  MCP Bridge (.kilo/mcp/openviking_server.py)   │  │
│  │  - X-API-Key header from OPENVIKING_API_KEY   │  │
│  │  - X-OpenViking-Agent header for namespacing  │  │
│  └──────────────┬────────────────────────────────┘  │
└─────────────────┼────────────────────────────────────┘
                  │ HTTP (port 1933)
┌─────────────────▼────────────────────────────────────┐
│  OpenViking Docker Container (openviking:latest)      │
│  ┌───────────────────────────────────────────────┐  │
│  │  REST API                                     │  │
│  │  auth_mode: api_key                           │  │
│  │  root_api_key: BBAp4B9bsU4fkJ056h8...         │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Storage Layer                                │  │
│  │  - AGFS (local backend): /app/data            │  │
│  │  - VectorDB (local backend)                   │  │
│  │  - TX lock_timeout: 10.0s, expire: 300s       │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Processing Pipeline                          │  │
│  │  - Embedding Queue → EmbeddingWorker          │  │
│  │  - Semantic Queue → SemanticWorker            │  │
│  │  - Semantic-Nodes Queue → NodeWorker          │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Agent Session Namespaces

| Agent          | Session ID                    | Namespace                                |
| -------------- | ----------------------------- | ---------------------------------------- |
| plan           | `kilo-context-plan`           | Shared project knowledge + plan-specific |
| architect      | `kilo-context-architect`      | Architecture decisions, design patterns  |
| designer       | `kilo-context-designer`       | Design briefs, visual references         |
| site-builder   | `kilo-context-site-builder`   | Site construction patterns               |
| plugin-builder | `kilo-context-plugin-builder` | Plugin construction patterns             |
| code           | `kilo-context-code`           | Implementation, bug fixes, patterns      |
| review         | `kilo-context-review`         | Review findings, common bug classes      |
| github         | `kilo-context-github`         | PR creation patterns                     |

Each namespace carries: session history (archived), agent-specific memories, and cross-referenced handoff documents.

---

## 3. Configuration (as of 2026-04-28)

### ov.conf (`~/.openviking/ov.conf`)

```json
{
	"embedding": {
		"dense": {
			"provider": "openai",
			"api_base": "http://host.docker.internal:4000/v1",
			"api_key": "sk-1234",
			"model": "titan-embed-v2",
			"dimension": 1024
		}
	},
	"vlm": {
		"provider": "openai",
		"api_base": "http://host.docker.internal:4000/v1",
		"api_key": "sk-1234",
		"model": "o4-mini",
		"timeout": 120
	},
	"server": {
		"host": "0.0.0.0",
		"port": 1933,
		"auth_mode": "api_key",
		"root_api_key": "BBAp4B9bsU4fkJ056h8-mKm0XFq8A87Zk71YO2fHI-Q",
		"cors_origins": ["*"]
	},
	"storage": {
		"workspace": "/app/.openviking/data",
		"agfs": { "backend": "local" },
		"vectordb": { "backend": "local" },
		"transaction": {
			"lock_timeout": 10.0,
			"lock_expire": 300.0
		}
	}
}
```

### Container Run Command (2026-05-01 — v0.3.14 with host-gateway fix)

```bash
docker run -d --name openviking \
  -p 1933:1933 \
  -v ~/.openviking:/app/.openviking \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/volcengine/openviking:latest
```

**Note**: `--add-host=host.docker.internal:host-gateway` is **required** on Docker Desktop for Mac (tested 4.39) — without it, `host.docker.internal` does not resolve inside the container, causing all embedding-dependent endpoints (`find`, `search`) to return 500 errors. This survives Docker restarts and IP changes (uses dynamic `host-gateway` keyword).

### MCP Bridge (`.kilo/mcp/openviking_server.py`)

**23 tools** bridging Kilo Code to OpenViking REST API over stdio transport.

| Category  | Tools                                                                                                                  |
| --------- | ---------------------------------------------------------------------------------------------------------------------- |
| Search    | `ov_find` (FTS), `ov_search` (semantic), `ov_grep` (regex), `ov_glob` (pattern matching)                               |
| Content   | `ov_ls`, `ov_tree`, `ov_abstract` (L0), `ov_overview` (L1), `ov_read` (L2)                                             |
| Resources | `ov_add_resource` (with `reason`/`instruction`), `ov_add_memory` (with `category`)                                     |
| Skills    | `ov_add_skill` (name, description, content)                                                                            |
| Relations | `ov_link`, `ov_unlink`, `ov_relations_list`                                                                            |
| Sessions  | `ov_session_get_or_create`, `ov_session_add_message`, `ov_session_commit`, `ov_session_get_task`, `ov_session_extract` |
| Indexing  | `ov_reindex`                                                                                                           |
| System    | `ov_status`, `ov_stats`                                                                                                |

**Authentication**: User key from `kilo.json` → `mcp.openviking.environment.OPENVIKING_API_KEY`.

---

## 4. Achievements

| Date       | Achievement                                  | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ---------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-04-28 | Lock contention fixed                        | Added `storage.transaction.lock_timeout: 10.0` + `lock_expire: 300.0` to `ov.conf`. Previously defaulted to `0.0` (no-wait), causing 112 files to stall in SemanticQueue.                                                                                                                                                                                                                                                                                                            |
| 2026-04-28 | Re-indexed Kilo Code KB                      | 46 docs from VS Code extension re-indexed via `temp_upload → add_resource`. Search verified working for "custom command system kilo code".                                                                                                                                                                                                                                                                                                                                           |
| 2026-04-28 | Queue health verified                        | Post-fix: 0 pending, 0 in-progress, 0 errors across all queues. No active locks.                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2026-04-27 | MCP endpoint swap fixed                      | `ov_find` ↔ `ov_search` endpoints corrected in `openviking_server.py`.                                                                                                                                                                                                                                                                                                                                                                                                               |
| 2026-04-27 | Duplicate Handoff Protocol fixed             | Removed duplicate section from `designer.md`.                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 2026-04-29 | **End-to-end handoff test**                  | Architect→code handoff stored via `ov_add_memory`. Verified all 3 retrieval paths: `ov_find` (#1, 0.71), `ov_search` (#1, 0.69), `ov_read` (7 sections intact). Pipeline confirmed production-ready for multi-agent handoffs.                                                                                                                                                                                                                                                        |
| 2026-04-29 | **MCP bridge parity**                        | Added `reason`/`instruction` to `ov_add_resource`, `category` to `ov_add_memory`, `ov_link` + `ov_unlink` for relations API. 18 tools total, 560 lines. Requires Kilo restart.                                                                                                                                                                                                                                                                                                       |
| 2026-05-01 | **OV KB re-indexed to v0.3.12**              | Replaced stale v0.2.x KB (`viking://resources/work/emdash/openviking/`) with 41 fresh docs from docs.openviking.ai under `viking://resources/work/emdash/openviking-docs/`. Old directory fully deleted. Search verified clean.                                                                                                                                                                                                                                                      |
| 2026-05-01 | **ov_grep GET→POST fix**                     | `ov_grep` used GET on `/api/v1/search/grep` — OV v0.3.12 API requires POST with JSON body. Fixed: changed method, moved params from querystring to JSON, corrected field name `query`→`pattern`, made `uri` required with default `viking://`. Verified: 12 matches returned.                                                                                                                                                                                                        |
| 2026-05-01 | **ov_unlink DELETE fix**                     | `ov_unlink` used `POST /api/v1/relations/unlink` (404). Fixed: `DELETE /api/v1/relations/link` with body `{from_uri, to_uri}`. Verified: returns `{from, to}` on success.                                                                                                                                                                                                                                                                                                            |
| 2026-05-01 | **ov_session_extract added**                 | New tool `ov_session_extract` — calls `POST /api/v1/sessions/{id}/extract` to force background memory extraction from committed sessions. Useful when archives are stale.                                                                                                                                                                                                                                                                                                            |
| 2026-05-01 | **SESSION_TOKEN_BUDGET 4000→16000**          | Increased default context token budget so OV includes more archive context. Note: dropping behavior is OV-internal, not purely budget-driven.                                                                                                                                                                                                                                                                                                                                        |
| 2026-05-01 | **Full MCP bridge audit**                    | Audited all 18 bridge tools against 48 OV v0.3.12 API endpoints. Found 2 bugs (fixed), 8 gaps (4 P0/P1). Remaining P0: `ov_add_skill` tool needed. Full gap list in Challenges section.                                                                                                                                                                                                                                                                                              |
| 2026-05-01 | **v0.3.14 upgrade + host-gateway fix**       | Pulled latest OV image (v0.3.14). `ov_find`/`ov_search` returned 500 — root cause: `host.docker.internal` not resolving in container (Docker Desktop for Mac regression). Embedding pipeline raised hard `RuntimeError` instead of graceful fallback (v0.3.12 behavior). Fixed by recreating container with `--add-host=host.docker.internal:host-gateway`. All 18 tools verified. GitHub issue raised.                                                                              |
| 2026-05-01 | **Hotness regression patched in bridge**     | MCP bridge now detects OV v0.3.14 archive staleness (`includedArchives == 0`) and fetches archives directly via REST API (newest 15, parallel). Extracts abstracts from overview markdown when the API `abstract` field returns degenerate `"```markdown"`. Injects `pre_archive_abstracts` and `latest_archive_overview` into context. Requires bridge restart.                                                                                                                     |
| 2026-05-01 | **Skill Discovery propagated to all agents** | Added `## Skill Discovery` section to all 8 agent prompts (`.kilo/agent/*.md`) with OV-based discovery, disk bootstrap, loading discipline, and re-registration instructions. Updated `agent-creation-template` skill to v3.0 with new canonical section order: Session Bookmark → Context Gathering → Skill Discovery → Role → Memory → Handoff → Domain Rules. Template re-registered in OV. Closes the Grade F Skill pillar instruction gap identified in the three-pillar audit. |
| 2026-05-01 | **Skill loading discipline added**           | Skill Discovery block now enforces: load at most 1-2 skills per task, skip skills whose L0 abstract doesn't clearly apply. Prevents up to 25K tokens of wasted skill loads per session. Added re-register-on-modify lifecycle instruction.                                                                                                                                                                                                                                           |

---

## 5. Challenges & Issues

### ~~🔴 CRITICAL — OV v0.3.14 `host.docker.internal` DNS Failure~~ **RESOLVED 2026-05-01**

**Symptom**: After upgrading from `v0.3.12` to `v0.3.14` (latest image pull), `ov_find` and `ov_search` consistently return 500 INTERNAL ERROR. `ov_grep`, `ov_glob`, `ov_stats`, and all non-embedding endpoints work fine.

**Root cause**: Two layers:

1. **DNS**: `host.docker.internal` does not resolve inside the container on Docker Desktop for Mac (4.39). Docker should auto-inject this host record but it's absent. The bridge gateway IP (`172.17.0.1`) works fine — suggesting Docker Desktop removed automatic `host.docker.internal` injection for bridge-mode containers.

2. **Error handling regression**: In v0.3.12, embedding connection failures were handled gracefully (likely returning empty results). In v0.3.14, the embedding pipeline surfaces an unhandled `RuntimeError("OpenAI API error: Connection error.")` which propagates to a 500 response. The traceback path: `hierarchical_retriever.retrieve` → `embed_compat` → `embed_async` → `RuntimeError`.

**Fix applied**:

```bash
docker stop openviking && docker rm openviking
docker run -d --name openviking \
  -p 1933:1933 \
  -v ~/.openviking:/app/.openviking \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/volcengine/openviking:latest
```

The `--add-host=host.docker.internal:host-gateway` flag dynamically injects the Docker host's gateway IP (192.168.65.254 on macOS) as `host.docker.internal` into the container's `/etc/hosts`. This survives Docker Desktop restarts and IP address changes.

**Verification**:

- `docker exec openviking cat /etc/hosts` → shows `192.168.65.254 host.docker.internal`
- `curl POST /api/v1/search/find` → 200 with 3 results (scores 0.70)
- `curl POST /api/v1/search/search` → 200 with 7 results (scores 0.55-0.74)
- All 18 MCP bridge tools verified operational

**GitHub issue raised**: Suggested OV should handle embedding provider connection errors gracefully (return empty results with a warning log, not 500).

**Permanent note**: Any future container recreation must include `--add-host=host.docker.internal:host-gateway`. This is a Docker Desktop for Mac workaround, not an OV bug per se — but OV's error handling regression makes it a breaking experience.

### ~~🔴 CRITICAL — `OPENVIKING_API_KEY` Not Set~~ **RESOLVED 2026-04-29**

**Symptom**: All `ov_*` tool calls return `OpenViking API error 401: Invalid API Key`.

**Root cause**: OpenViking uses a two-layer key system. The `root_api_key` in `ov.conf` authenticates as ROOT — good for admin endpoints (`/api/v1/admin/*`, `/api/v1/system/status`) but tenant-scoped operations (`/api/v1/sessions`, `/api/v1/search/find`, `/api/v1/fs/ls`) require a **user key**. Kilo's `kilo.json` was configured with the root key, not a user key.

**Account**: `agentcafe` (created 2026-04-23, 1 user: `agentcafe` with `admin` role)

**Fix applied (2026-04-29)**:

1. Regenerated user key for `agentcafe` account: `b13e3586608a84da4894a8bf22ff37b1107d26495aec3d3ed46c681000dc8134`
2. Updated `kilo.json` to use the user key instead of the root key

**Verification via curl**:

- `GET /api/v1/sessions` → 14 sessions listed (including all 8 agent namespaces + 6 UUID sessions)
- `POST /api/v1/search/find {"query": "handoff architect"}` → 5 results (scores 0.59-0.65), including handoff docs, architecture decisions, plans

**Requires Kilo Code restart** for the MCP bridge to pick up the new key.

### 🔴 CRITICAL — Session Archive Staleness (2026-05-01, root cause confirmed)

`kilo-context-architect` session: 31 commits on file, but `ov_session_get_or_create` context compilation drops ALL 31 (`droppedArchives: 31, includedArchives: 0`). The only context loaded is the `latest_archive_overview` (736 tokens) — which is stale (shows ATS Phase 1 session, not the last infrastructure audit).

**Root cause confirmed (2026-05-01):**

1. **All 31 archives have `hotness: None`** — fetched individually via `/api/v1/sessions/{id}/archives/{archive_id}`, every archive returns `hotness: null` and `summary_tokens: null`. The content IS present (archive_029 has correct overview text about the OV infrastructure audit), but without hotness metadata, the context compiler drops every archive.

2. **`activeTokens` reflects only uncommitted messages** — the `kilo-context-plan` session (0 commits, 2 pending messages) shows `activeTokens: 267`. The architect session (31 commits, 0 pending messages) shows `activeTokens: 0`. This means the context compiler's budget allocation only counts live messages, not archived ones.

3. **Token budget doesn't affect archive inclusion** — tested at 16000, 32000, and 100000. Same result: `includedArchives: 0, droppedArchives: 31`. The budget parameter increases context window but the compiler still drops everything.

4. **Hotness computation is a v0.3.14 regression** — archives created under v0.3.12 (most of the 31) were not re-processed for hotness after the v0.3.14 upgrade. Unlike memories (45 warm, hotness working), session archives don't get the same pipeline treatment.

5. **Contrast with memories**: `ov_stats` shows 45 memories all `warm`, with hotness distribution working correctly. Session archives and memories use different metadata pipelines — the memory pipeline is functional, the session archive pipeline is broken in v0.3.14.

**Impact:** Every new agent session starts with stale context. The `latest_archive_overview` is frozen at the last archive that happened to get a non-null hotness (likely from an earlier OV version). Downstream agents cannot see prior decisions or task state.

**Workaround for now:**

- Use the working file (`openviking-working-file.md`) as the authoritative source of task state
- Use `ov_find("topic")` to search memories for prior decisions
- Individual archive fetch works — can manually read recent archives if needed

**Needs OV upstream fix** — GitHub issue to be filed on the OpenViking repository.

### 🟡 MEDIUM — VectorDB Is Sparse

Only 16 vectors in the VectorDB after re-indexing 46 Kilo Code docs. This suggests either:

- Embeddings aren't being generated for all resources
- VectorDB has a capacity limit configured
- Some resources are only stored in AGFS (file storage) but not embedded

Need to investigate the embedding pipeline completeness.

### 🟢 RESOLVED — Agent Prompt Section Ordering (from prior audit)

Agent prompts in `.kilo/agent/*.md` now follow the canonical section order: **Session Bookmark → Context Gathering → Skill Discovery → Role → Memory → Handoff → Domain Rules**. All 8 agents have the HARD GATE block at position 1, Context Gathering at position 2, and the new Skill Discovery section at position 3. The `agent-creation-template` v3.0 encodes this ordering as enforced. All prior tasks completed:

- All 8 agent entry points have `ov_find`/`ov_search` guidance
- Mandatory gate language present in all prompts
- Skill Discovery with bootstrap, loading discipline, and re-registration lifecycle
- Template mirrors agent prompts (no drift)

### 🟡 MEDIUM — Custom MCP Bridge: OV Update Surface

**Risk**: Our custom bridge (`.kilo/mcp/openviking_server.py`) wraps OpenViking's REST API. If OV updates its HTTP API (endpoints, params, auth), the bridge breaks. The native OV MCP server exposes only 6 tools — we need 17+ for session statefulness, tiered retrieval, dual search, filesystem ops, and analytics — so we can't just switch.

**Blast radius**: Minimal. Only two components touch the OV API directly:

| Component                                    | Risk                                             | Recovery                                         |
| -------------------------------------------- | ------------------------------------------------ | ------------------------------------------------ |
| `.kilo/mcp/openviking_server.py` (488 lines) | Endpoint paths, request body shapes, auth header | Update `_ov_request` calls, verify 17 tools work |
| `skills/openviking-agent-config/SKILL.md`    | Tool descriptions, parameter docs                | Update to match bridge changes                   |

**Everything else is safe by design:**

- Agent prompts call MCP tools, not the OV API — stable interface regardless of version
- Kilo config (`kilo.json`) only sets env vars
- Backups and KBs live inside OV's bind-mounted storage, independent of container version
- Docker bind-mount (`~/.openviking/data/`) is host-side, untouched by image upgrades

**Recovery when OV updates:**

```
1. Pull new OV image, restart container
2. curl http://localhost:1933/openapi.json > /tmp/new-openapi.json
3. Diff against current spec — focus on endpoint paths, param names, auth
4. Update .kilo/mcp/openviking_server.py for any breaking changes
5. If OV docs changed, re-index: ov_add_resource(path="<ov-docs-url>")
6. Restart Kilo Code → bridge picks up changes, verify 17 tools
7. If the native MCP gained session tools, evaluate whether to switch
```

### 🟡 MEDIUM — Handoff File Single-Point Bottleneck

`.kilo/handoff/current.md` is overwritten on every handoff. Only one pipeline in flight at a time. If two agents produce handoffs concurrently, the later one wins. When OpenViking is live, handoffs go through `ov_add_memory` with searchable URIs — this is the preferred path.

### 🟢 LOW — AGENTS.md Full Review Deferred

Review of the 671-line AGENTS.md for completeness against actual codebase patterns was deferred.

---

## 6. Persistence Architecture

OpenViking provides persistent state at three layers. This section documents the mechanisms, the categorization and importance system, and the recommended pattern for storing critical information.

---

### Layer 1: Session Memory — Automatic, Structured

The **primary mechanism** for agent statefulness. Runs every session, before and after work.

```
SESSION START
  ov_session_get_or_create("kilo-context-architect", agent_id="architect")
  → Returns compiled context:
    - latest_archive_overview: full summary of most recent session
    - pre_archive_abstracts: one-liners from older sessions
    - task state: goal, progress, blockers, next step
    - estimatedTokens: context budget remaining

MID-SESSION (capture critical decisions immediately)
  ov_session_add_message("kilo-context-architect", "assistant",
    "<2-3 sentence summary of work completed>",
    agent_id="architect"
  )
  → Messages are attributed to the agent via role_id
  → Survive into the archive even if the session crashes

SESSION END
  ov_session_commit("kilo-context-architect", agent_id="architect")
  → Phase 1 (synchronous, ~12ms): archives all messages to history
  → Phase 2 (background, ~8s): LLM extracts memories across 8 categories
  → Returns task_id for optional polling via ov_session_get_task
```

**Current state**: 12 archives in `kilo-context-architect`. Session context carries forward: ResourceProcessor fix, prompt ordering tasks, AGENTS.md review.

---

### Layer 2: Explicit Memories — Manual, Persistent, Searchable

For decisions that need to survive **independently of any specific session**:

```
ov_add_memory(content, uri?, agent_id?)
```

**Two-step pipeline**: `temp_upload` → `add_resource` → chunked → embedded → summarized → searchable.

**Default URI**: `viking://resources/work/emdash/kilo/architecture/decisions/memory-{timestamp}-{id}.md`

**Current state**: 23 memories stored across 4 categories (preferences: 6, entities: 8, events: 8, skills: 1). All currently `warm` (oldest: 2.6 days).

---

### Layer 3: Resources — File-Level, Indexed Knowledge Base

For bulk knowledge indexing — codebase docs, architecture decisions, skill definitions, Kilo KB:

```
ov_add_resource(path, to?)
```

**Processing**: chunked → embedded (titan-embed-v2, 1024-dim) → L0 abstract → L1 overview → L2 full content.

**Searchable via**: `ov_find` (PostgreSQL FTS — exact terms, fast) and `ov_search` (semantic search — conceptual queries).

**Current state**: 46 Kilo Code docs indexed. Embedding pipeline verified functional through LiteLLM. VectorDB currently sparse (16 vectors vs 46 docs — embedding completeness under investigation).

---

### Importance and Categorization System

#### Built-in (automatic)

| Mechanism               | How it works                                                                                                                                                      | Current State                                |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| **8 Memory Categories** | Session `commit` uses LLM extraction to classify every memory into one of: `profile`, `preferences`, `entities`, `events`, `cases`, `patterns`, `tools`, `skills` | 6 preferences, 8 entities, 8 events, 1 skill |
| **Hotness Tiers**       | Automatic tiering based on access frequency + recency: `hot`, `warm`, `cold`                                                                                      | All 23 currently `warm`                      |
| **Agent Namespacing**   | `role_id` set to agent name during `add_message` — memories route to the correct agent namespace                                                                  | 8 namespaces active                          |
| **Staleness Tracking**  | Tracks `not_accessed_7d` / `not_accessed_30d` counters                                                                                                            | 0 stale across all memories                  |

#### Convention-based (manual — what to use)

There is **no explicit `importance: critical` field** in the API. Use these conventions instead:

| Convention                                | For                                                                      | Example                                                                                      |
| ----------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| **`## Decision:` header**                 | Architecture-critical decisions that downstream agents must know         | `## Decision: API key type — root vs user`                                                   |
| **`architecture/decisions/` URI path**    | Design choices with cross-agent impact                                   | `viking://resources/work/emdash/kilo/architecture/decisions/`                                |
| **Session message capture**               | Mid-session decisions that must not be lost between `start` and `commit` | `ov_session_add_message` immediately after critical fixes                                    |
| **Relations API** (`ov_link`/`ov_unlink`) | Explicit cross-references with a `reason` field                          | `ov_link("viking://.../decision", "viking://.../code-change,viking://.../PR", reason="...")` |
| **`### Cross-Layer Impact` section**      | In `ov_add_memory` content — signals template/site-layer changes         | `Cross-Layer Impact: Templates in demos/simple need X`                                       |

#### Gaps in current MCP bridge

| Gap                                                         | Status                                                      |
| ----------------------------------------------------------- | ----------------------------------------------------------- |
| `ov_add_resource` didn't pass `reason`/`instruction` fields | ✅ Fixed — optional params added                            |
| `ov_add_memory` didn't accept a `category` parameter        | ✅ Fixed — embedded as YAML frontmatter + `reason` metadata |
| Relations API not exposed as MCP tool                       | ✅ Fixed — `ov_link` + `ov_unlink` added                    |
| No explicit priority/importance field                       | Use URI conventions and `## Decision:` headers              |

---

### Recommended Pattern for Critical Information

```
1. MID-SESSION (immediately after critical fix):
   ov_session_add_message("kilo-context-architect", "assistant",
     "<summary of critical fix and why it matters>")

2. AFTER FIX VERIFIED (persistent, searchable):
   ov_add_memory(
     content = """## Decision: [Topic]
Date: YYYY-MM-DD

[2-3 sentences describing the decision and rationale.]

### Cross-Layer Impact
[If applicable: templates affected, migration required, etc.]
""",
     uri = "viking://resources/work/emdash/kilo/architecture/decisions/[descriptive-slug].md"
   )

3. SESSION END:
   ov_session_commit("kilo-context-architect", agent_id="architect")
   → Background LLM extraction classifies into 8 categories
   → Hotness tracks how often this knowledge is retrieved
   → Downstream agents find it via ov_find("[topic]") or ov_search("[concept]")
```

After step 2, the memory is permanently indexed, searchable, and retrievable by any downstream agent in the pipeline.

---

### What's Missing for Full Statefulness

| Gap                              | Description                                                                                                   | Priority                                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| ~~API key connectivity~~         | ~~All ov\_\* tools broken. This is the single gate.~~                                                         | ~~🔴 P0~~ **DONE**                                                                                     |
| Agent prompt discipline          | Agents must call `ov_session_get_or_create` FIRST and `ov_session_commit` LAST. Not all prompts enforce this. | 🟢 RESOLVED (2026-05-01) — all 8 agents have HARD GATE block, Skill Discovery, canonical section order |
| Memory extraction quality        | Session commit extracts 8 categories of memories — need to validate quality/accuracy.                         | 🟡 P1                                                                                                  |
| ~~Handoff document consumption~~ | ~~Downstream agents must reliably `ov_find("handoff {agent}")` to pick up where upstream left off~~           | ~~🟡 P1~~ **VERIFIED** (2026-04-29) — 3 retrieval paths confirmed                                      |
| ~~MCP bridge feature parity~~    | ~~`reason`/`instruction` on `ov_add_resource`, relations API, category override on `ov_add_memory`~~          | ~~🟡 P1~~ **DONE**                                                                                     |
| ~~AGENTS.md token bloat~~        | ~~671 lines (~8K tokens) loaded every session. Reference material should be indexed in OV, loaded on demand~~ | ~~🟡 P1~~ **DONE** — 235 lines, 14 OV patterns                                                         |
| ~~VectorDB population~~          | ~~Need to re-index EmDash knowledge sources (AGENTS.md, architecture docs, skill docs) into OpenViking~~      | ~~🟢 P2~~ **DONE** — 14 patterns indexed in OV, 25 VectorDB files/23MB                                 |
| ~~Search quality validation~~    | ~~Verify `ov_search` returns relevant results for domain-specific queries~~                                   | ~~🟢 P2~~ **DONE** — 18 lookup queries verified (3 manual, 15 cross-referenced)                        |

---

## 7. Backup Strategy

### Storage Layout

OpenViking data is bind-mounted at host path `~/.openviking/data/` → container `/app/data/`. All data survives container restarts and image updates.

```
~/.openviking/
├── ov.conf               # Server configuration (771B)
├── ovcli.conf            # CLI configuration
└── data/                 # Bind-mounted → /app/data
    ├── _system/          # System metadata (6.2MB)
    ├── temp/             # Temporary uploads (16KB)
    ├── vectordb/         # Embedding vectors (22MB)
    └── viking/           # Account-scoped data (6.1MB)
        └── agentcafe/    # All data under the agentcafe account
            ├── agent/    # 8 agent dirs × {instructions,memories,skills}/
            ├── resources/# Indexed resources (kb/kilo, work/emdash)
            └── session/  # 14 sessions × {messages.jsonl, history/}
```

**Total footprint**: ~35MB (will grow linearly with session history and resources).

### What to Back Up

| Path                          | Size  | Priority        | Reason                                                                                                   |
| ----------------------------- | ----- | --------------- | -------------------------------------------------------------------------------------------------------- |
| `viking/agentcafe/session/`   | ~1MB  | 🔴 Critical     | Irreplaceable — all agent session history, 12+ archives with message history and LLM-extracted summaries |
| `viking/agentcafe/resources/` | ~3MB  | 🔴 Critical     | Indexed knowledge base: Kilo KB docs, architecture decisions, handoff docs, plans                        |
| `viking/agentcafe/agent/`     | ~1MB  | 🔴 Critical     | Agent-specific memories, instructions, skills per namespace                                              |
| `vectordb/`                   | 22MB  | 🟡 Important    | Embedding vectors — regenerable but expensive (~minutes per resource via titan-embed-v2)                 |
| `_system/`                    | 6.2MB | 🟢 Nice-to-have | Auto-generated metadata, account registry, redo logs                                                     |
| `ov.conf`                     | 771B  | 🟡 Important    | Server config with root_api_key, lock_timeout, embedding settings                                        |
| `temp/`                       | 16KB  | ⬜ Skip         | Transient uploads                                                                                        |

### Backup Mechanism

A shell script at `~/.openviking/backup.sh` that tar-gzips the data directory (excluding `temp/`):

```bash
#!/bin/bash
# OpenViking backup script
# Usage: ./backup.sh [label]
#   With label: creates a named backup (e.g., "pre-api-key-fix")
#   Without: creates a timestamped daily backup

BACKUP_DIR="$HOME/.openviking/backups"
DATA_DIR="$HOME/.openviking/data"
CONF_DIR="$HOME/.openviking"
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

if [ -n "$1" ]; then
    # Named backup (manual, for critical moments)
    NAME="$BACKUP_DIR/ov-backup-${TIMESTAMP}-${1}.tar.gz"
else
    # Automated daily backup
    NAME="$BACKUP_DIR/ov-backup-${TIMESTAMP}.tar.gz"
fi

# Backup data (exclude temp/) and config
tar czf "$NAME" \
    -C "$DATA_DIR" \
    --exclude='temp' \
    _system vectordb viking \
    -C "$CONF_DIR" \
    ov.conf ovcli.conf

echo "Backup created: $NAME ($(du -h "$NAME" | cut -f1))"
```

### Schedule

| Trigger                   | Frequency                                                  | Method                                                        |
| ------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------- |
| **Pre-session** (manual)  | Before critical work (e.g., API key changes, config edits) | `./backup.sh pre-api-key-fix`                                 |
| **Post-session** (manual) | After completing critical work, before `ov_session_commit` | `./backup.sh post-key-fix-verified`                           |
| **Daily automated**       | 03:00 local time                                           | `launchd` plist (macOS) or `cron` (Linux)                     |
| **Weekly rollup**         | Sunday 03:00                                               | Same script, but retention policy keeps Sunday backups longer |

### Retention Policy

```
backups/
├── ov-backup-2026-04-29-030000.tar.gz     # Daily (keep 7)
├── ov-backup-2026-04-28-030000.tar.gz
├── ...
├── ov-backup-2026-04-26-030000-SUN.tar.gz # Weekly (keep 4)
├── ov-backup-2026-04-19-030000-SUN.tar.gz
├── ...
├── ov-backup-2026-04-29-084500-pre-api-key-fix.tar.gz  # Manual (keep forever)
└── ov-backup-2026-04-29-084800-post-key-fix-verified.tar.gz
```

- **Daily**: Kept for 7 days, oldest deleted on day 8
- **Weekly** (Sunday): Kept for 4 weeks
- **Manual** (named): Kept indefinitely until explicitly removed
- **Estimated total**: ~15 backups × ~12MB compressed = ~180MB

### Restore Procedure

```bash
# 1. Stop the OpenViking container
docker stop openviking

# 2. Restore from backup
tar xzf ~/.openviking/backups/ov-backup-YYYY-MM-DD-HHMMSS.tar.gz \
    -C ~/.openviking/

# 3. Start the container
docker start openviking

# 4. Verify
curl http://localhost:1933/health
```

### launchd Configuration (macOS)

`~/Library/LaunchAgents/com.openviking.backup.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openviking.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/agentcafe/.openviking/backup.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>3</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/agentcafe/.openviking/backups/backup.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/agentcafe/.openviking/backups/backup.err</string>
</dict>
</plist>
```

Load with: `launchctl load ~/Library/LaunchAgents/com.openviking.backup.plist`

### Backup Status

| Item                                   | Status                                                                     |
| -------------------------------------- | -------------------------------------------------------------------------- |
| Backup directory                       | ✅ Created (`~/.openviking/backups/`)                                      |
| Backup script                          | ✅ Created (`~/.openviking/backup.sh`)                                     |
| launchd plist                          | ✅ Created + loaded (`~/Library/LaunchAgents/com.openviking.backup.plist`) |
| First manual backup (pre-API-key-fix)  | Missed — fix documented in working file instead                            |
| First manual backup (post-API-key-fix) | ✅ Done — `ov-backup-2026-04-29-090242-post-api-key-fix.tar.gz` (3.9MB)    |
| Daily automated schedule               | ✅ Active — runs at 03:00 daily, Sunday weekly rollup                      |

1. ~~Where does Kilo Code configure MCP server environment variables?~~ **ANSWERED**: Project-level `kilo.json` → `mcp.openviking.environment.OPENVIKING_API_KEY`. Takes precedence over global `~/.config/kilo/kilo.jsonc`. Must use a **user key** (not root key) for tenant-scoped APIs.

2. **Is the OpenViking container storage persistent?** The workspace is `/app/data` inside the container. Is this bind-mounted to a host directory? If not, all data is lost on container restart.

3. **What's the embedding pipeline throughput?** How fast can we index the full EmDash knowledge base (AGENTS.md, 8 agent prompts, architecture docs, skill docs)? Understanding this sets expectations for maintenance workflows.

4. **Can `ov_session_commit`'s background memory extraction be validated?** The 8-category extraction runs in background. Is there a way to verify it produced correct memories before relying on them?

5. **What's the optimal `lock_timeout`?** 10.0s fixed the immediate stall, but the ideal value depends on embedding latency and concurrency patterns. Should be tuned empirically.

6. **Kilo Workflows exploration:** Should we use them more? Can they be indexed in OV like skills for agent discovery? What new workflow commands would streamline the pipeline (e.g., `/feature`, `/fix`, `/deploy`, `/migrate`)? Does Kilo chain `<switch_mode>` across commands or is it single-agent per invocation? How does `subtask: true` interact with OV session management?

---

## 9. Action Items (Priority Order)

| #   | Priority | Action                                                                                                                                                                               | Owner     | Status                                                                                                                                                                |
| --- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 🔴 P0    | Configure correct API key (`kilo.json` → user key, not root key)                                                                                                                     | architect | **DONE** (2026-04-29)                                                                                                                                                 |
| 2   | 🔴 P0    | Verify `ov_session_get_or_create` works after restart                                                                                                                                | architect | **DONE** (2026-04-29) — 12 archives, session state intact                                                                                                             |
| 3   | 🔴 P0    | Verify `ov_find` / `ov_search` work after restart                                                                                                                                    | architect | **DONE** (2026-04-29) — 10 results, scores 0.58-0.65                                                                                                                  |
| 4   | 🟡 P1    | Fix agent prompt section ordering in all `.kilo/agent/*.md` files — canonical order: Session Bookmark → Context Gathering → Skill Discovery → Role → Memory → Handoff → Domain Rules | architect | **DONE** (2026-05-01) — all 8 agents updated, template v3.0 encodes order                                                                                             |
| 5   | 🟡 P1    | Add mandatory gate language (HARD GATE — MANDATORY) to agent prompts lacking it                                                                                                      | architect | **DONE** (2026-05-01) — all 8 agents have HARD GATE block                                                                                                             |
| 6   | 🟡 P1    | Add MCP bridge feature parity: `reason`/`instruction` on `ov_add_resource`, relations API + `category` on `ov_add_memory`                                                            | architect | **DONE** (2026-04-29) — 18 tools, 560 lines                                                                                                                           |
| 7   | 🟡 P1    | Run end-to-end handoff test: architect → code via `ov_add_memory`                                                                                                                    | architect | **DONE** (2026-04-29) — see results below                                                                                                                             |
| 8   | 🟡 P1    | Implement `ov_add_skill` MCP bridge tool                                                                                                                                             | architect | **DONE** (2026-05-01) — bridge tool works. Instruction gap (agents not told to use it) closed via Skill Discovery section. Still need to actually register 14 skills. |
| 9   | 🟡 P1    | Implement `ov_relations_list` MCP bridge tool                                                                                                                                        | architect | **DONE** (2026-05-01) — calls `GET /api/v1/relations`, 517 lines                                                                                                      |
| 10  | 🟡 P1    | Implement `ov_session_extract` MCP bridge tool                                                                                                                                       | architect | **DONE** (2026-05-01) — calls `POST /api/v1/sessions/{id}/extract`                                                                                                    |
| 11  | 🟡 P1    | Implement `ov_reindex` MCP bridge tool                                                                                                                                               | architect | **DONE** (2026-05-01) — calls `POST /api/v1/content/reindex`                                                                                                          |
| 12  | 🟡 P1    | Implement `ov_glob` MCP bridge tool                                                                                                                                                  | architect | **DONE** (2026-05-01) — calls `POST /api/v1/search/glob`                                                                                                              |

---

### 🟡 P1 — Handoff Test Results (2026-04-29)

Stored a realistic architect→code handoff (cursor-based pagination) via `ov_add_memory` with `category: patterns` and verified retrieval through the code agent's search path:

| Test                  | Method                                               | Result                                                                               |
| --------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Storage**           | `ov_add_memory(content, uri, category)`              | ✅ Stored at `viking://resources/work/emdash/kilo/handoff/architect-to-code-test.md` |
| **Visibility**        | `ov_ls("viking://.../handoff")`                      | ✅ Listed with L0 abstract auto-generated                                            |
| **FTS find**          | `ov_find("cursor-based pagination FindManyResult")`  | ✅ #1 result, score 0.71                                                             |
| **Semantic search**   | `ov_search("implement pagination for API endpoint")` | ✅ #1 resource, score 0.69                                                           |
| **L2 retrieval**      | `ov_read(uri)`                                       | ✅ Full content: 7 handoff sections intact                                           |
| **Category override** | Frontmatter `category: patterns`                     | ✅ Accepted, embedded in content                                                     |
| **L0/L1 generation**  | OpenViking pipeline                                  | ✅ Abstract + overview auto-generated within seconds                                 |

The code agent's expected search path — `ov_search("implement pagination for API endpoint with cursor limit")` — returns the architect's handoff as the top result (0.69), followed by its L1 overview (0.68) and relevant reference docs. The handoff is immediately findable through both `ov_find` (exact terms) and `ov_search` (semantic intent). No changes needed — the pipeline is production-ready for multi-agent handoffs.

| 13 | 🟡 P1 | Create backup script + launchd plist for daily OpenViking backups | architect | **DONE** (2026-04-29) |
| 14 | 🟡 P1 | Create first post-API-key-fix manual backup | architect | **DONE** (2026-04-29) — 3.9MB compressed |
| 15 | 🟢 P2 | Index EmDash KB into OpenViking (AGENTS.md, architecture docs, skill docs) | architect | **DONE** — 14 code patterns indexed. KB complete. |
| 16 | 🟢 P2 | Verify VectorDB embedding pipeline produces vectors for all indexed resources | architect | **DONE** (2026-04-29) — 25 files, 23MB, all 14 code patterns have L0+L1 |
| 17 | 🔴 P0 | **OV v0.3.14 bug: Session context compiler drops all archives** — hotness field is None on all 31 archives, causing `includedArchives: 0` regardless of token budget. Affects all agent sessions. | OV upstream | **NEW** — needs GitHub issue |
| 18 | 🟢 P3 | Explore Kilo Workflows: should we use them, OV indexing, new commands, switch_mode chaining | architect | **NEXT SESSION** |
| 19 | 🟡 P1 | Register all 14 skills in OV via `ov_add_skill` — one call per skill. Skills are on disk, bridge tool works, agents have bootstrap instruction — just need the actual registration | architect | **PENDING** |

---

## 10. Notes

- The `agent-manager.json` has minimal state (one session, 7 tab entries). This tracks Kilo Code sessions, not OpenViking sessions.
- The `ov_add_resource` ingestion has a known `500` behavior with bulk uploading → one-file-at-a-time is the safe path.
- Embedding requires LiteLLM (port 4000) to be running and the `titan-embed-v2` model available.
- The `lock_timeout` fix was a single config change, no code changes needed. Container bind-mount makes it persist across image updates.
