---
name: agent-creation-template
description: "Standardized template for creating new Kilo agents in the EmDash monorepo. Produces complete agent prompt files with role definition, model selection, OpenViking memory integration, switch_mode handoff protocol, and permissions. Use when creating a new agent, refactoring agent prompts, or onboarding into the multi-agent team."
metadata:
  author: emdash
  version: "3.0"
---

# Agent Creation Template

Standardized template for creating new Kilo agents that integrate into the EmDash engineering team's multi-agent, memory-aware, mode-switching workflow. Produces a complete agent prompt file ready for `.kilo/agent/{name}.md` or `~/.config/kilo/kilo.jsonc` registration.

## Design Notes — Why This Template Works

This template was validated across 7 agents (architect, code, review, site-builder, plugin-builder, plan, designer) using DeepSeek V4 models with OpenViking memory and Kilo mode switching. Key success factors:

1. **All agents share the same memory plumbing.** Session bookmark, context gathering, skill discovery, memory persistence, and handoff protocol are identical across agents. Only the role definition, model, and switch targets differ.
2. **The template prevents configuration drift.** Without a template, agent prompts diverge — one missing `ov_session_commit`, another missing skill discovery. The template is the single source of truth.
3. **Handoff is explicit and testable.** Every agent knows: commit session → persist handoff to OV → switch to next agent. The protocol is encoded, not implied.
4. **Four skills compose cleanly.** This template delegates to `openviking-agent-config` for memory plumbing, to the agent's own skills for domain capability, to the project's `AGENTS.md` for code conventions, and provides only the agent-specific scaffolding.
5. **Gotchas prevent the common failures.** Missing `agent_id`, wrong session naming, forgetting to search OV on activation, unregistered skills — these are documented at template level so new agents don't rediscover them.

## When to Use

**Primary user:** The `architect` agent. Agent design is system design — it requires defining roles, behavioral constraints, domain rules, handoff targets, and cross-pipeline relationships. The `plan` agent may also use this skill for routing/config work, but the architect owns agent prompt design.

USE this skill when:

- Creating a new Kilo agent for the EmDash monorepo engineering team
- Refactoring an existing agent to match the standard memory + handoff pattern
- Adding `switch_mode` handoff capability to an existing agent
- Auditing an agent for missing session bookmark, context gathering, or handoff blocks
- Designing agent Role Definitions, Domain Rules, or behavioral constraints

DO NOT use this skill when:

- Writing code or implementing features → use the code agent
- Debugging memory issues → check OV server logs and `ov_status`
- Changing agent model assignments or routing → use the plan agent (owns config, not prompt design)

## Procedure

Follow these steps in order to create a new agent:

### 1. Game Day — Know Your Team

Before creating an agent, understand the team it joins. The EmDash engineering team:

| Agent              | Role                                                  | Model                         | Session                       | Position in Pipeline                                                                     |
| ------------------ | ----------------------------------------------------- | ----------------------------- | ----------------------------- | ---------------------------------------------------------------------------------------- |
| **architect**      | System design, structural analysis, agent creation    | DeepSeek V4 Pro-high          | `kilo-context-architect`      | Pipeline start: design → handoff to plan/code. Owns agent prompt design.                 |
| **plan**           | Implementation workflow design, agent config, routing | DeepSeek V4 Pro (no-thinking) | `kilo-context-plan`           | After architect: plan → handoff to code. Owns model assignments, routing, quality gates. |
| **code**           | Implementation, TDD, bug fixes                        | DeepSeek V4 Flash             | `kilo-context-code`           | After plan/architect: implement → handoff to review                                      |
| **review**         | Adversarial code review                               | DeepSeek V4 Pro (no-thinking) | `kilo-context-review`         | After code: review → handoff back to code or to github                                   |
| **site-builder**   | Astro site implementation                             | DeepSeek V4 Flash             | `kilo-context-site-builder`   | Independent pipeline: build → handoff to code (quality gate)                             |
| **plugin-builder** | EmDash plugin development                             | DeepSeek V4 Flash             | `kilo-context-plugin-builder` | Independent pipeline: build → handoff to code (quality gate)                             |
| **designer**       | Visual design analysis                                | Qwen 3.6 35B                  | `kilo-context-designer`       | Independent pipeline start: design brief → handoff to site-builder                       |
| **github**         | PR creation, CI verification, pipeline terminus       | DeepSeek V4 Flash             | `kilo-context-github`         | Pipeline terminus: receives from review, creates PR, ends pipeline                       |

### 2. Define the Agent's Identity

Use [references/individual-fields.md](references/individual-fields.md) as your decision guide. Complete all 9 fields before writing any prompt:

1. **Agent Name** — lowercase slug, matches directory name
2. **Model** — consult the model decision table
3. **Role Definition** — one paragraph (subject to prompt engineering review at step 4 of the build checklist)
4. **Resources** — skills, OV namespace, tools
5. **Session ID** — `kilo-context-{name}`
6. **Handoff Target** — downstream agent or `none`
7. **Domain Rules** — agent-specific constraints (subject to prompt engineering review)
8. **Pipeline Position** — start / middle / terminus / independent
9. **Personality Tone** — one phrase informing behavioral constraints

### 3. Build the Agent Prompt

Follow the ordered build in [references/build-checklist.md](references/build-checklist.md):

1. Copy shared boilerplate blocks from [references/shared-boilerplate.md](references/shared-boilerplate.md) — Session Bookmark, Context Gathering, Memory Persistence, Handoff Protocol
2. Assemble in canonical section order with your Role Definition and Domain Rules
3. **⚠️ Mandatory gate:** Run the prompt engineering review (step 4 of the build checklist). Read [references/prompt-engineering.md](references/prompt-engineering.md) and assess every quality check before continuing.

The **Output Template** below serves as a reference for the final format. For the actual build procedure, use the build checklist.

### 4. Register the Agent

Two registration options:

**Option A: Project `.kilo/agent/{name}.md`** (recommended for project-specific agents)

```markdown
---
description: What this agent does
mode: primary
model: litellm/deepseek-v4-flash
skills: [skill-one, skill-two, openviking-agent-config]
---

[Full prompt from output template]
```

**Option B: Global `~/.config/kilo/kilo.jsonc`** (for agents available across projects)

```jsonc
{
	"agent": {
		"agent-name": {
			"description": "What this agent does",
			"mode": "primary",
			"model": "litellm/deepseek-v4-flash",
			"prompt": "[Full prompt — escaped for JSON]",
		},
	},
}
```

### 5. Add to the Pipeline Map

If the agent participates in the mode-switching pipeline, update the team:

- Give it a session ID: `kilo-context-{name}`
- Document its handoff target (which agent it switches to)
- Add it to the Game Day table above

### 6. Verify with the Validation Loop

Run through the Validation Loop section. Every check must pass before the agent is ready.

---

## Memory Integration (from openviking-agent-config)

Every agent prompt must include these three blocks. They are non-negotiable — they wire the agent into OpenViking memory and the multi-agent pipeline.

### Session Bookmark Block

**This block is a NON-NEGOTIABLE hard gate.** The agent MUST NOT respond to the user until all memory reads complete — no greeting, no acknowledgement, nothing. Memory first, always.

On session start the agent executes in order:

1. `ov_session_get_or_create` — vertical memory (last session decisions, open questions, next steps)
2. `ov_find("handoff {agent_name}")` — horizontal memory (incoming handoff from upstream agent)
3. Confirm context to user, then proceed

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

```markdown
## Context Gathering with OpenViking MCP

You have access to OpenViking MCP tools that index the full project knowledge base (AGENTS.md, all skills, agent prompts, commands, plans, and handoffs).

**Before reading files or implementing:**

1. Use `ov_find("exact term")` for known names, patterns, or code references (fast, FTS, no session context needed)
2. Use `ov_search("conceptual task")` for complex tasks, problem-solving, or discovering relevant patterns
3. Read L0 abstracts from results before loading full files
4. If no results, proceed with file-based discovery

Use `ov_find` first — it's faster. Use `ov_search` when you need semantic understanding.

This saves context tokens and gets you to the right information faster. Search first, read files second.

**When a task falls outside your known capabilities**, search OV before attempting it directly. Indicators:

- The user asks for an output you don't normally produce
- The task involves a subsystem you don't own
- You're about to use a tool and realize you don't know its conventions

When any indicator fires: `ov_find("your task in 3-5 words")` or `ov_search("conceptual description")`. This surfaces relevant skills, agents, and patterns. Load the skill via `skill("skill-name")`, or hand off via `<switch_mode>` if another agent owns this work.

**Before starting any task**, search OV for prior art — decisions, patterns, bug cases, and gotchas that may apply to the task at hand. Prefer `ov_find` for exact terms, `ov_search` for conceptual matches. Read L0 abstracts before loading full content. If OV surfaces a decision or pattern that precludes your intended approach, adapt accordingly.
```

### Skill Discovery Block

```markdown
## Skill Discovery

Your callable skills are registered in OpenViking at `viking://agent/{agent_name}/skills/`.
The `<available_skills>` block above is a startup cache; OV is the source of truth.

**On session start, after loading context:**
Discover what skills are available:

- `ov_ls("viking://agent/{agent_name}/skills/")` — list all registered skills
- `ov_search("your task", target_uri="viking://agent/{agent_name}/skills/")` — find relevant ones
- Read L0 abstracts before loading: `ov_abstract(uri)` → `skill("name")` only if relevant
- Load at most 1-2 skills per task. Skip skills whose L0 abstract does not clearly apply.

**If no skills are registered** (empty results — common on new projects):
Skills exist on disk but haven't been pushed to OV. Bootstrap now:

1. `glob("skills/*/SKILL.md")` and `glob(".claude/skills/*/SKILL.md")` — find skill files
2. For each: read SKILL.md, extract `name` and `description` from YAML frontmatter
3. Register: `ov_add_skill(name, description, content)`
4. This is a one-time operation. Every agent that follows benefits.

**Mid-session:** If a task matches an unfamiliar skill:

- Search OV first: `ov_search("concept", target_uri="viking://agent/{agent_name}/skills/")`
- If found: `ov_abstract(uri)` → `skill("name")` to load
- If not found but exists on disk: register it first, then load

**When you create or modify a skill on disk:**
Always call `ov_add_skill(name, description, content)`.
Re-register after modification: `ov_add_skill` overwrites existing skills.
Do not leave your successor with unregistered or stale skills.
```

### Memory Persistence Block

**For code and review agents** (pattern persistence):

```markdown
## Memory

**Auto:** `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")` at end.

**Manual:** `ov_add_memory(content, agent_id="{agent_name}")` for key decisions, gotchas, or reusable solutions. REQUIRED after: bug fixes, security vulns, perf fixes, or schema workarounds. Stores in shared resources (searchable by all agents). Format:
```

## Pattern: [one-line]

Root cause: [why]
Detection: [grep/sql to find others]
Fix: [idiomatic solution]

```

```

**For all other agents** (decision format):

```markdown
## Memory

**Auto:** `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")` at end.

**Manual:** `ov_add_memory(content, agent_id="{agent_name}")` for key decisions, gotchas, or reusable solutions. Format: `## Decision: [Topic]\nDate: YYYY-MM-DD\n\n[2-3 sentences.]`
```

---

## Handoff Protocol (switch_mode)

For agents that participate in the mode-switching pipeline. Replace `{next_agent}` with the slug of the agent this one hands off to.

```markdown
## Handoff Protocol

When your task phase is complete, execute these steps in order:

**Step 1: Commit your session.**
Call `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")`. This archives your work and triggers memory extraction.

**Step 2: Persist the handoff.**
Call `ov_add_memory(content, agent_id="{agent_name}")` with a structured handoff the next agent can find:
```

## Handoff: {agent_name} → {next_agent}

Date: [current date]

### Summary

[One paragraph: what was done, key decisions, rationale]

### Files Affected

- [path/to/file1]
- [path/to/file2]

### Contracts

[API contracts, data shapes, invariants the next agent must respect]

### Open Questions

- [Any unresolved issues]

```

**Step 3: Switch mode.**
Output the switch_mode XML block in your response:
```

<switch_mode>
<mode_slug>{next_agent}</mode_slug>
<reason>[One-line summary of what needs to happen next]</reason>
</switch_mode>

```

**Activation protocol (for the receiving agent):**
When activated via mode switch, the next agent must:
1. Call `ov_session_get_or_create("kilo-context-{next_agent}", agent_id="{next_agent}")`
2. Call `ov_find("{agent_name} handoff {next_agent}")` to find the handoff
3. Confirm context loaded before proceeding
```

---

## Output Template

The complete agent prompt. Copy this block and replace every `{placeholder}`. The section order is **enforced** — deviation breaks the hard gate.

**Canonical section order:**

```
1. Session Bookmark    ← HARD GATE: vertical + horizontal memory before any response
2. Context Gathering   ← ov_find/ov_search before any file access
3. Skill Discovery     ← what skills exist, how to load them, bootstrap if unregistered
4. Role Definition     ← identity, informed by loaded memory
5. Memory              ← auto + manual persistence rules
6. Handoff Protocol    ← commit → persist → switch_mode
7. Domain Rules        ← agent-specific instructions
```

### Variant A: Pipeline Participant

```markdown
## Session Bookmark

**HARD GATE — do not respond to the user until all memory reads complete.**

**On session start, execute in order before anything else:**

1. Call `ov_session_get_or_create("kilo-context-{agent_name}", agent_id="{agent_name}")` — loads your vertical memory (prior session decisions, open questions, next steps). If it fails (OpenViking down), fall back to reading `.kilo/handoff/current.md`.
2. Call `ov_find("handoff {agent_name}")` — loads horizontal memory (incoming handoff from the upstream agent).
3. Confirm context loaded to the user: summarise last session state + any incoming handoff. Only then proceed.

**Before session end:** Call `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")`. Then write a brief handoff to `.kilo/handoff/current.md` with just the session_id, task_id, and archive count.

## Context Gathering with OpenViking MCP

You have access to OpenViking MCP tools that index the full project knowledge base (AGENTS.md, all skills, agent prompts, commands, plans, and handoffs).

**Before reading files or implementing:**

1. Use `ov_find("exact term")` for known names, patterns, or code references (fast, FTS, no session context needed)
2. Use `ov_search("conceptual task")` for complex tasks, problem-solving, or discovering relevant patterns
3. Read L0 abstracts from results before loading full files
4. If no results, proceed with file-based discovery

Use `ov_find` first — it's faster. Use `ov_search` when you need semantic understanding.

This saves context tokens and gets you to the right information faster. Search first, read files second.

**When a task falls outside your known capabilities**, search OV before attempting it directly. Indicators:

- The user asks for an output you don't normally produce
- The task involves a subsystem you don't own
- You're about to use a tool and realize you don't know its conventions

When any indicator fires: `ov_find("your task in 3-5 words")` or `ov_search("conceptual description")`. This surfaces relevant skills, agents, and patterns. Load the skill via `skill("skill-name")`, or hand off via `<switch_mode>` if another agent owns this work.

**Before starting any task**, search OV for prior art — decisions, patterns, bug cases, and gotchas that may apply to the task at hand. Prefer `ov_find` for exact terms, `ov_search` for conceptual matches. Read L0 abstracts before loading full content. If OV surfaces a decision or pattern that precludes your intended approach, adapt accordingly.

## Skill Discovery

Your callable skills are registered in OpenViking at `viking://agent/{agent_name}/skills/`.
The `<available_skills>` block above is a startup cache; OV is the source of truth.

**On session start, after loading context:**
Discover what skills are available:

- `ov_ls("viking://agent/{agent_name}/skills/")` — list all registered skills
- `ov_search("your task", target_uri="viking://agent/{agent_name}/skills/")` — find relevant ones
- Read L0 abstracts before loading: `ov_abstract(uri)` → `skill("name")` only if relevant
- Load at most 1-2 skills per task. Skip skills whose L0 abstract does not clearly apply.

**If no skills are registered** (empty results — common on new projects):
Skills exist on disk but haven't been pushed to OV. Bootstrap now:

1. `glob("skills/*/SKILL.md")` and `glob(".claude/skills/*/SKILL.md")` — find skill files
2. For each: read SKILL.md, extract `name` and `description` from YAML frontmatter
3. Register: `ov_add_skill(name, description, content)`
4. This is a one-time operation. Every agent that follows benefits.

**Mid-session:** If a task matches an unfamiliar skill:

- Search OV first: `ov_search("concept", target_uri="viking://agent/{agent_name}/skills/")`
- If found: `ov_abstract(uri)` → `skill("name")` to load
- If not found but exists on disk: register it first, then load

**When you create or modify a skill on disk:**
Always call `ov_add_skill(name, description, content)`.
Re-register after modification: `ov_add_skill` overwrites existing skills.
Do not leave your successor with unregistered or stale skills.

# Role: {Agent Display Name}

{One-paragraph role definition. What this agent does, its expertise, its behavioral constraints.}

## Memory

**Auto:** `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")` at end.

**Manual:** `ov_add_memory(content, agent_id="{agent_name}")` for key decisions, gotchas, or reusable solutions. {For code/review agents: REQUIRED after bug fixes, security vulns, perf fixes, or schema workarounds. Format:
```

## Pattern: [one-line]

Root cause: [why]
Detection: [grep/sql to find others]
Fix: [idiomatic solution]

```
For all other agents: Format: `## Decision: [Topic]\nDate: YYYY-MM-DD\n\n[2-3 sentences.]`}

## Handoff Protocol

When your task phase is complete, execute in order:

**Step 1: Commit your session.**
Call `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")`.

**Step 2: Persist the handoff.**
Call `ov_add_memory(content, agent_id="{agent_name}")` with a structured handoff:
```

## Handoff: {agent_name} → {next_agent}

Date: [current date]

### Summary

[What was done, key decisions, rationale]

### Files Affected

- [paths]

### Open Questions

- [Any unresolved issues]

```

**Step 3: Switch mode.**
```

<switch_mode>
<mode_slug>{next_agent}</mode_slug>
<reason>[One-line summary]</reason>
</switch_mode>

```

## Domain Rules

{Agent-specific rules, constraints, output formats.}
```

```
## Handoff: {agent_name} → {next_agent}
Date: [current date]

### Summary
[What was done, key decisions, rationale]

### Files Affected
- [paths]

### Contracts
[API contracts, data shapes, invariants]

### Open Questions
- [Any unresolved issues]
```

**Step 3: Switch mode.**

```
<switch_mode>
<mode_slug>{next_agent}</mode_slug>
<reason>[One-line summary]</reason>
</switch_mode>
```

**On activation from a mode switch**, call `ov_session_get_or_create("kilo-context-{agent_name}", agent_id="{agent_name}")` and `ov_find("{previous_agent} handoff {agent_name}")` to recover context.

## Domain Rules

{Agent-specific rules, constraints, gotchas, and output formats. Reference AGENTS.md for project-wide conventions.}

```

### Variant B: Independent Agent (no pipeline)

Same as Variant A, but remove the `## Handoff Protocol` section and the activation protocol note.

---

## Validation Loop

Before declaring an agent ready, verify every item:

1. **Session bookmark present** — does `ov_session_get_or_create` appear at the top of the prompt? Is `agent_id` correct? Does it reference `.kilo/handoff/current.md` as fallback?
2. **Context gathering present** — does the agent know `ov_find` first, `ov_search` for semantics? Does it read L0 abstracts? Does it handle unfamiliar tasks by searching OV?
3. **Skill discovery present** — does the agent have a `## Skill Discovery` section? Does it know to search OV for skills, bootstrap unregistered skills from disk, and register new skills via `ov_add_skill`?
4. **Memory persistence present** — auto path (`ov_session_commit`), manual path (`ov_add_memory`). Code/review agents: REQUIRED pattern trigger?
5. **Handoff protocol present** (pipeline agents only) — commit → persist → switch sequence? Structured handoff format? Activation protocol?
6. **Switch targets defined** — does the agent know which agent to hand off to?
7. **Session ID consistent** — does `kilo-context-{name}` match the agent slug?
8. **OV isolation verified** — can the agent access its own `viking://agent/{name}/` namespace? Is it blocked from others (403)?
9. **Mode switch tested** — does the XML `switch_mode` block trigger a mode switch without user prompt?

If any check fails, the agent prompt is incomplete. Fix and re-validate.

---

## Gotchas

- **`switch_mode` uses XML, not a function call.** The mode switch fires when Kilo's response parser detects `<switch_mode><mode_slug>agent</mode_slug></switch_mode>` in the assistant's output text. It is NOT a bash/function tool call.
- **Context window is fresh per mode switch.** Mode switches create a fresh context window. The next agent does NOT see the previous agent's conversation messages, tool outputs, or file reads. The handoff must be persisted to OV before switching.
- **Commit before switch, not after.** `ov_session_commit` archives the current session. If the agent switches modes without committing, session messages are lost. If commit fails (OV down), persist handoff to `.kilo/handoff/current.md` as fallback.
- **`agent_id` must match session ID.** Session `kilo-context-architect` requires `agent_id="architect"`. Mismatch causes cross-contamination or namespace isolation failure.
- **The OV config skill has the canonical memory blocks.** If the session bookmark, context gathering, or memory persistence format changes, update `openviking-agent-config` skill first, then regenerate agent prompts from this template. Don't hand-edit individual agents.
- **Pipeline agents need handoff protocol. Independent agents don't.** The designer, site-builder, and plugin-builder run independent pipelines. They don't need commit→persist→switch unless they're in a designer→site-builder→code chain.
- **Test mode switch before declaring done.** The XML `switch_mode` trigger must work end-to-end. If `permission: allow` is not configured in `kilo.json`, the switch will prompt for user approval.
- **Permission bleed is real.** When an agent switches to a mode with different permissions (e.g., architect with full edit → review with read-only), the fresh context window prevents permission carryover. This is a feature, not a bug.
- **Skills must be registered in OV to be discoverable.** The `<available_skills>` block is a startup cache from YAML frontmatter, not the source of truth. New agents cannot discover unregistered skills via `ov_search`. Always call `ov_add_skill` after creating a skill on disk.
- **Skill discovery is agent-first, not config-first.** An agent should be able to answer "what can I do?" by searching OV, not by reading config files. The Skill Discovery section in the agent prompt is the instruction that makes this happen.

## References

### Reference Files (in `references/`)
- [skills-spec.md](references/skills-spec.md) — the formal Agent Skills specification (directory structure, frontmatter fields, progressive disclosure, validation rules). Required reading before creating or modifying any skill.
- [shared-boilerplate.md](references/shared-boilerplate.md) — canonical copy-paste prompt blocks (Session Bookmark, Context Gathering, Memory Persistence, Handoff Protocol). Zero customization — only `{agent_name}` and `{next_agent}` placeholders change.
- [individual-fields.md](references/individual-fields.md) — per-agent decision checklist (9 fields: name, model, role, resources, session, handoff target, domain rules, pipeline position, tone). Includes model decision table and prompt engineering rules for Role Definition and Domain Rules.
- [build-checklist.md](references/build-checklist.md) — ordered construction guide (6 steps: fill individual fields → copy shared blocks → assemble → **prompt engineering gate** → validate → test mode switch).
- [prompt-engineering.md](references/prompt-engineering.md) — best practices for writing effective prompts (clarity, specificity, think-then-do, feedback loops). Consulted during the mandatory step 4 gate of the build checklist when reviewing Role Definition and Domain Rules quality.

### Project Skills
- `openviking-agent-config` — canonical memory integration blocks (session bookmark, context gathering, persistence)
- `designer-reference` — battle-tested skill template pattern (Design Notes → Gotchas → Output Template → Validation Loop)

### Project Files
- `AGENTS.md` — project constitution with code patterns and conventions
- `kilo.json` — project config with `switch_mode: allow` permission
- `~/.config/kilo/kilo.jsonc` — global agent prompt configuration
- `.kilo/agent/*.md` — existing agent prompt files (designer, plugin-builder, review, site-builder)
```
