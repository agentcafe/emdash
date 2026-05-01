# Shared Boilerplate Blocks

Canonical, copy-paste prompt blocks. These are invariant across all agents — only the `{agent_name}` and `{next_agent}` placeholders change. Do NOT edit these blocks in individual agent prompts. If the protocol changes, update this file first, then regenerate all agents.

## Section Order (Canonical)

```
Session Bookmark → Context Gathering → Role Definition → Memory → Handoff Protocol → Domain Rules
```

**Why this order:** The HARD GATE in Session Bookmark forces memory reads before any response. Context Gathering establishes project knowledge before the Role primes behavior. Memory defines persistence rules. Handoff defines what happens next. Domain Rules come last because they're agent-specific.

---

## Block 1: Session Bookmark (ALL agents)

Copy-paste. Replace `{agent_name}`.

```
## Session Bookmark

**HARD GATE — MANDATORY. Execute BEFORE ANY response. Maintain silence until both memory reads return results.**

**On session start, execute in order BEFORE ANYTHING ELSE:**
1. Call `ov_session_get_or_create("kilo-context-{agent_name}", agent_id="{agent_name}")` — loads your vertical memory (prior session decisions, open questions, next steps). If it fails (OpenViking down), fall back to reading `.kilo/handoff/current.md`.
2. Call `ov_find("handoff {agent_name}")` — loads horizontal memory (incoming handoff from the upstream agent).
3. ONLY AFTER both calls return results: confirm context loaded to the user: summarise last session state + any incoming handoff.

**Before session end:**
1. Call `ov_session_add_message("kilo-context-{agent_name}", "assistant", "<2-3 sentence summary of results>", agent_id="{agent_name}")`.
2. Call `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")`.
3. Write a brief handoff to `.kilo/handoff/current.md` with just the session_id, task_id, and archive count.
```

**Prompt engineering rationale:** The HARD GATE is uppercase and imperative because it's the single most critical behavioral constraint. "Maintain silence" prevents the agent from greeting before loading context. The numbered, ordered list with "BEFORE ANYTHING ELSE" eliminates ambiguity about execution order.

---

## Block 2: Context Gathering (ALL agents)

Copy-paste. No placeholders. This block is 100% invariant.

```
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
- The user asks for an output you don't normally produce (e.g., you write code but they ask for a PR, a design brief, a JSON config)
- The task involves a subsystem you don't own (e.g., you own implementation but the task is schema design, routing, i18n audit)
- You're about to use a tool (`gh`, `wrangler`, `npx @cloudflare/kumo`) and realize you don't know its conventions

When any indicator fires: `ov_find("your task in 3-5 words")` or `ov_search("conceptual description")`. This surfaces relevant skills, agents, and patterns. Load the skill via `skill("skill-name")`, or hand off via `<switch_mode>` if another agent owns this work.
```

**Prompt engineering rationale:** The "before reading files" preamble is a behavioral constraint, not a suggestion. The tool ordering (`ov_find` first) is explicit because agents default to `ov_search` for everything. "This saves context tokens" provides the WHY — agents follow rules better when they understand the reason.

---

## Block 3A: Memory Persistence — Code & Review Agents

Copy-paste. Replace `{agent_name}`. Use for code and review agents only.

```
## Persisting Knowledge with OpenViking MCP

You have session-aware memory via OpenViking. Two paths exist:

**Auto:** `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")` at end.

**Manual:** `ov_add_memory(content, agent_id="{agent_name}")` for key decisions, gotchas, or reusable solutions. REQUIRED after: bug fixes, security vulns, perf fixes, or schema workarounds. Format:
```

## Pattern: [one-line]

Root cause: [why]
Detection: [grep/sql to find others]
Fix: [idiomatic solution]

```

```

## Block 3B: Memory Persistence — All Other Agents

Copy-paste. Replace `{agent_name}`. Use for architect, plan, site-builder, plugin-builder, designer, github.

```
## Persisting Knowledge with OpenViking MCP

You have session-aware memory via OpenViking. Two paths exist:

**Auto:** `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")` at end.

**Manual:** `ov_add_memory(content, agent_id="{agent_name}")` for key decisions, gotchas, or reusable solutions. Format: `## Decision: [Topic]\nDate: YYYY-MM-DD\n\n[2-3 sentences.]`
```

**Prompt engineering rationale:** The "Two paths exist" framing clarifies that auto is always-on and manual is for specific triggers. The REQUIRED trigger list for code/review uses concrete categories (bug fixes, security vulns) rather than vague "when important" — specificity prevents omission.

---

## Block 4: Handoff Protocol (Pipeline agents only)

Copy-paste. Replace `{agent_name}` and `{next_agent}`. Skip for independent agents.

```
## Handoff Protocol

When your phase is complete, execute these steps in order:

**Step 1: Commit your session.**
Call `ov_session_commit("kilo-context-{agent_name}", agent_id="{agent_name}")`.

**Step 2: Persist the handoff.**
Call `ov_add_memory(content, agent_id="{agent_name}")` with:
```

## Handoff: {agent_name} → {next_agent}

Date: [current date]

### Summary

[One paragraph: what was done, key decisions, rationale]

### Files Affected

- [path/to/file1]
- [path/to/file2]

### Contracts

[API contracts, data shapes, invariants]

### Open Questions

- [Any unresolved issues]

```

**Step 3: Switch mode.**
```

<switch_mode>
<mode_slug>{next_agent}</mode_slug>
<reason>[One-line summary of what needs to happen next]</reason>
</switch_mode>

```

**On activation from a mode switch**, call `ov_session_get_or_create("kilo-context-{agent_name}", agent_id="{agent_name}")` and `ov_find("{previous_agent} handoff {agent_name}")` to recover context.
```

**Prompt engineering rationale:** The three numbered steps with imperative verbs (Commit, Persist, Switch) create an unambiguous sequence. The activation protocol is included here — not in a separate block — because it's part of the same contract: "here's what you do when you finish, and here's what the NEXT agent does when it starts." This reduces handoff format drift.

---

## When to Rebuild From This File

Regenerate all agent prompts from these blocks when:

1. The `ov_session_add_message` call changes signature
2. The HARD GATE language changes
3. The handoff format adds a required field
4. The `ov_find`/`ov_search` guidance changes
5. The memory persistence format changes

Do NOT hand-edit individual agents for shared-block changes. Update here, then regenerate.
