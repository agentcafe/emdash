# Individual Fields — Per-Agent Decision Checklist

Every agent is defined by these nine decisions. Consult [shared-boilerplate.md](shared-boilerplate.md) for the invariant blocks; this file covers what changes per agent. For fields marked with **Prompt Quality**, consult [prompt-engineering.md](prompt-engineering.md) before finalizing.

---

## 1. Agent Name (slug)

- **What:** Lowercase, hyphen-separated identifier. Must match the directory name (`.kilo/agent/{name}.md`) and the session ID suffix.
- **Rules:** 1-64 chars, lowercase alphanumeric + hyphens, no leading/trailing hyphens, no consecutive hyphens.
- **Examples:** `architect`, `code`, `site-builder`, `plugin-builder`, `github`

---

## 2. Model

- **What:** The LLM that powers this agent.
- **Decision rules:**

| Agent Type                                         | Model                                   | Why                                                                                                               |
| -------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| System design, structural analysis, agent creation | `litellm/deepseek-v4-pro-no-thinking`   | Deep reasoning, output is contracts/diagrams. Thinking adds latency, no payoff.                                   |
| Tactical implementation, TDD, bug fixes            | `litellm/deepseek-v4-flash-no-thinking` | Fast edits, lint, test loop. Thinking adds latency.                                                               |
| Workflow design, trade-off analysis                | `litellm/deepseek-v4-pro`               | Trade-off analysis benefits from visible reasoning traces.                                                        |
| Adversarial review                                 | `litellm/deepseek-v4-pro-no-thinking`   | Deep bug detection benefits from Pro's structural reasoning. Flash is for fast implementation, not deep analysis. |
| Visual design, screenshot analysis                 | `litellm/qwen3.6-35b`                   | Only vision-capable model in the team.                                                                            |
| PR creation, git/gh operations                     | `litellm/deepseek-v4-flash-no-thinking` | Terminal pipeline step — needs speed, not reasoning.                                                              |
| Skill-specific builders (site, plugin)             | `litellm/deepseek-v4-flash-no-thinking` | Domain knowledge comes from skills, not model depth.                                                              |

- **Anti-patterns:** Flash on architect (misses structural patterns), Pro on site-builder (overkill), Qwen on code (not a coder).

---

## 3. Role Definition <span style="color:red">**Prompt Quality**</span>

- **What:** One paragraph defining who the agent is, what it does, and its behavioral constraints.
- **Prompt engineering rules (mandatory):**
  - **Specific, not vague.** "You are the Lead Architect for this codebase" — not "You help with architecture."
  - **Scoped, not ambitious.** "Your job is to design, configure, and maintain the development process" — not "You improve everything about development."
  - **Behavioral, not descriptive.** "You do NOT write application code. You configure the team that does." — not "You focus on configuration."
  - **One responsibility domain.** No blurring. If you can't summarize in one sentence, split into two agents.
- **Format:** `# Role: {Display Name}\n\n{One paragraph.}`
- **Anti-patterns:**
  - "You are an expert in [list of 5 things]" — too broad, pick one
  - "You help with..." — passive, implies optionality
  - Placeholder leakage: "Replace this with your agent's role"

---

## 4. Resources

- **What:** Skills the agent loads, OpenViking namespace, tool permissions.
- **Decision checklist:**
  - [ ] **Skills:** Which skills from the project does this agent load? (e.g., `building-emdash-site`, `creating-plugins`, `adversarial-reviewer`, `agent-creation-template`)
  - [ ] **OV agent_id:** Matches name slug (e.g., agent_name=`architect` → agent_id=`"architect"`)
  - [ ] **OV session ID:** `kilo-context-{agent_name}`
  - [ ] **Tools needed:** Read-only? File editing? Bash? Browser? GitHub tools? MCP servers?
- **Anti-pattern:** Skill names that don't match available_skills list. Verify before declaring.

---

## 5. Session ID

- **What:** `kilo-context-{agent_name}` — must match the `agent_id` parameter in all OV calls.
- **Rules:** One session ID per agent. Must be unique across the team. Must match the agent slug exactly.
- **Anti-pattern:** `kilo-context-code` with `agent_id="architect"` — mismatch causes namespace pollution.

---

## 6. Handoff Target

- **What:** Which agent receives the handoff when this agent completes its phase.
- **Rules:**
  - **Pipeline participant:** Must declare a `{next_agent}` — e.g., architect → code, code → review.
  - **Independent agent:** No handoff target (e.g., designer, site-builder, plugin-builder, github).
  - **Pipeline terminus:** `none` — this agent is the end of the line (e.g., github).
- **Anti-pattern:** Independent agent with a handoff protocol block (dead code). Pipeline agent without one (broken chain).

---

## 7. Domain Rules <span style="color:red">**Prompt Quality**</span>

- **What:** Agent-specific constraints, output formats, gotchas, and behavioral rules.
- **Prompt engineering rules (mandatory):**
  - **Negative rules first.** "Do NOT make changes outside the scope of the active task" — constraints are more important than permissions.
  - **Concrete categories.** "If the fix touches SQL/migrations/auth or >3 files, invoke review" — not "For complex fixes, consider review."
  - **Output format contracts.** If the agent produces structured output (designs, briefs, review reports), specify the exact format with field names.
  - **Cross-references.** Link to relevant project conventions (AGENTS.md patterns) rather than duplicating them.
- **Format:** `## Domain Rules\n\n{Numbered or bulleted constraints.}`
- **Anti-patterns:**
  - "Follow best practices" — meaningless, no agent intentionally follows worst practices
  - Duplicating AGENTS.md content — reference it, don't copy it
  - "Try to..." language — imperative, not aspirational

---

## 8. Pipeline Position

- **What:** Where this agent sits in the workflow.
- **Options:**
  - **Pipeline start:** Receives tasks directly from user/plan, hands off downstream (architect, designer)
  - **Pipeline middle:** Receives handoff, processes, hands off downstream (code)
  - **Pipeline terminus:** Receives handoff, completes the pipeline (review → github)
  - **Independent:** Standalone pipeline, no handoff protocol (site-builder, plugin-builder)
- **Affects:** Whether the Handoff Protocol block is included, activation protocol wording.

---

## 9. Personality Tone

- **What:** One short phrase that informs behavioral constraints.
- **Examples:**
  - `"Decisive and professional"` — architect
  - `"Tactical and efficient"` — code
  - `"Adversarial — assume bugs exist"` — review
  - `"Process-first, configuration-driven"` — plan
- **Why:** Informs the Role Definition's tone. "Decisive and professional" produces different constraint language than "Supportive and helpful."

---

## Quick Reference: All 9 Fields

| #   | Field             | Prompt Quality? | Example                                |
| --- | ----------------- | --------------- | -------------------------------------- |
| 1   | Agent Name        | No              | `architect`                            |
| 2   | Model             | No              | `litellm/deepseek-v4-pro-no-thinking`  |
| 3   | Role Definition   | **Yes**         | "You are the Lead Architect..."        |
| 4   | Resources         | No              | Skills: `agent-creation-template`      |
| 5   | Session ID        | No              | `kilo-context-architect`               |
| 6   | Handoff Target    | No              | `code`                                 |
| 7   | Domain Rules      | **Yes**         | "Do NOT make changes outside scope..." |
| 8   | Pipeline Position | No              | `pipeline start`                       |
| 9   | Personality Tone  | No              | `Decisive and professional`            |
