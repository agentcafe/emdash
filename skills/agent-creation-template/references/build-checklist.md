# Build Checklist — Ordered Agent Construction

This is a sequential build list. Work through it in order. Each step references either a shared boilerplate block (copy-paste) or an individual field (design). At step 4, a **mandatory prompt engineering review gate** assesses writing quality before continuing.

**Pre-build prerequisite:** Read [skills-spec.md](skills-spec.md) if this is your first agent. Read [shared-boilerplate.md](shared-boilerplate.md) to understand the invariant blocks.

---

## Step 1: Fill Out the Individual Fields

Use [individual-fields.md](individual-fields.md) as your reference. Complete all 9 fields:

- [ ] **Agent Name** — slug, matches `.kilo/agent/{name}.md`
- [ ] **Model** — consulting the model decision table
- [ ] **Role Definition** — one paragraph (will be reviewed at step 4)
- [ ] **Resources** — skills, OV namespace, tools
- [ ] **Session ID** — `kilo-context-{name}`
- [ ] **Handoff Target** — downstream agent or `none`
- [ ] **Domain Rules** — agent-specific constraints (will be reviewed at step 4)
- [ ] **Pipeline Position** — start / middle / terminus / independent
- [ ] **Personality Tone** — one phrase

---

## Step 2: Copy Shared Boilerplate Blocks

From [shared-boilerplate.md](shared-boilerplate.md), copy into your agent prompt:

- [ ] **Block 1: Session Bookmark** — replace `{agent_name}` only
- [ ] **Block 2: Context Gathering** — copy as-is, no changes
- [ ] **Block 3: Memory Persistence** — choose variant (code/review pattern format vs standard decision format)
- [ ] **Block 4: Handoff Protocol** — only if pipeline participant. Replace `{agent_name}` and `{next_agent}`

---

## Step 3: Assemble the Prompt

Combine all blocks in canonical section order:

```
1. Session Bookmark      (shared, copy-pasted)
2. Context Gathering     (shared, copy-pasted)
3. Role Definition       (individual, written by you)
4. Memory                (shared, copy-pasted)
5. Handoff Protocol      (shared, copy-pasted — skip if independent)
6. Domain Rules          (individual, written by you)
```

Register the agent:

- **Option A:** `.kilo/agent/{name}.md` (project-level, recommended)
- **Option B:** `~/.config/kilo/kilo.jsonc` (global)

---

## Step 4: Prompt Engineering Review Gate ⚠️ MANDATORY

**Read [prompt-engineering.md](prompt-engineering.md) before proceeding.** Then assess:

### Role Definition Quality

| Check                       | Test                                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Specific?**               | If someone reads only the Role Definition, do they know exactly what this agent does?                                                       |
| **Scoped?**                 | Does it describe ONE responsibility domain? If you can replace "and" with a period and the sentence still works, it's probably two domains. |
| **Behavioral?**             | Does it say what the agent DOES and does NOT do? "You do NOT write code" is behavioral. "You focus on design" is descriptive.               |
| **No placeholder leakage?** | Search for `{placeholder}`, `[TODO]`, `[insert here]`. Remove all.                                                                          |

### Domain Rules Quality

| Check                           | Test                                                                                                                          |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Negative first?**             | Does the first rule constrain behavior ("Do NOT...")? Constraints prevent more bugs than permissions.                         |
| **Concrete?**                   | Would a new agent know exactly when a rule applies? "If the fix touches SQL/migrations/auth" — yes. "For complex fixes" — no. |
| **Output contracts?**           | If this agent produces structured output (designs, briefs, reviews), is the format specified with field names?                |
| **Referenced, not duplicated?** | Cross-references to AGENTS.md patterns? Not copy-pasting them?                                                                |

### Prompt Structure Quality

| Check                      | Test                                                                                                           |
| -------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Section order correct?** | Session Bookmark → Context Gathering → Role → Memory → Handoff → Domain Rules. Verify.                         |
| **HARD GATE intact?**      | "MANDATORY. Execute BEFORE ANY response. Maintain silence until both memory reads return results." — verbatim? |
| **No ambiguous verbs?**    | Search for "try to", "consider", "may want to". Replace with imperative: "do", "run", "check".                 |

**If any check fails:** fix it now. Do not proceed to validation.

---

## Step 5: Validate

Run through the Validation Loop from the main SKILL.md:

- [ ] Session bookmark present with correct `agent_id`
- [ ] Context gathering present with `ov_find` first rule
- [ ] Memory persistence present with correct variant
- [ ] Handoff protocol present (pipeline agents only) with structured format
- [ ] Switch targets defined (pipeline agents only)
- [ ] Session ID consistent with `agent_id`
- [ ] Mode switch XML block ready to test

---

## Step 6: Test Mode Switch

Before declaring the agent done:

1. Start a session with the new agent
2. Verify it loads context via `ov_session_get_or_create` first (no greeting before context)
3. For pipeline agents: verify the handoff works (commit → persist → switch → next agent finds the handoff via `ov_find`)
4. Verify the agent does NOT exceed its scope (e.g., architect doesn't edit files unless explicitly writing designs)

---

## Quick Summary Card

```
1. Fill individual-fields.md  →  9 decisions made
2. Copy shared-boilerplate.md →  4 blocks pasted
3. Assemble in order          →  SKILL.md or kilo.jsonc ready
4. Prompt engineering gate    ←  ⚠️ DO NOT SKIP
5. Validate                   →  7 validation checks
6. Test mode switch           →  End-to-end pipeline verified
```
