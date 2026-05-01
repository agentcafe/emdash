# Miscellaneous — Things to Fix

> Running list of issues noticed during sessions. Add entries without disrupting active work.
> Review periodically; promote items to issues/PRs when ready.

---

## 1. Designer agent skips Session Bookmark on startup

**Date:** 2026-04-29
**Agent:** designer (qwen3.6-35b)
**Severity:** Medium — breaks memory continuity, but agent recovers when prompted

**Observed behavior:**
User sends "hi". Designer responds with "Hello. I'm ready to help with visual design tasks..." — a friendly greeting, but it skipped the mandatory Session Bookmark protocol entirely.

**Expected behavior:**
On session start, the designer agent MUST execute these steps BEFORE ANY response:

1. `ov_session_get_or_create("kilo-context-designer", agent_id="designer")` — loads vertical memory
2. `ov_find("handoff designer")` — loads horizontal memory (incoming design task)
3. Only after both return: confirm context loaded, summarize last session state + incoming handoff

**Root cause likely:** The Session Bookmark is a `HARD GATE` in the architect's and designer's prompts, but qwen3.6-35b may not parse it as strictly as deepseek-v4-pro. The agent treated "hi" as a conversational trigger instead of a session-start trigger.

**Fix needed:** Either:

- Make the Session Bookmark framing more assertive ("DO NOT respond to any user message until..." instead of "Execute BEFORE ANY response")
- Add a model-specific override for qwen that re-emphasizes this
- Add a startup hook check in the agent framework itself

**Workaround:** Prompt the designer with "Did you read your system prompt?" — it catches on and executes the calls.

---

## 2. Code agent hits same boundary errors across sessions — no OV pattern recall

**Date:** 2026-04-30
**Agent:** code (qwen3-coder-next / deepseek-v4-flash-no-thinking)
**Severity:** High — causes repeated failures at the same architectural boundary

**Observed behavior:**
Code agent starts naive each session. It does not search OV for previously documented decisions or lessons. Pattern observed twice in one day:

| Session           | Error                                                                                    | Already documented?                                                                         |
| ----------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Step 3, attempt 1 | Wrote skeleton handlers with `// Note: no DB access` — didn't know `ctx.content` pattern | Yes — architect session had stored decision "ATS Plugin Uses Standard Format + Content API" |
| Step 4, attempt 1 | Hit `Ai` type error, didn't know workaround                                              | Yes — architect had established "minimal inline type" pattern earlier in same session       |

**Expected behavior:**
Before implementing, code agent should query OV for related patterns: `ov_find("content API plugin handler")` or `ov_search("ATS plugin database access pattern")`. This would surface stored decisions and prevent repeating known errors.

**Root cause:** Code agent's system prompt does not include OV search instructions. The agent treats OV as a session-commit sink, not a pattern-retrieval source. Its HARD GATE loads `kilo-context-code` for task state but doesn't instruct "search OV for patterns related to your task before coding."

**Fix needed:** Add to code agent's prompt:

```
### Pre-Implementation Pattern Check
Before writing any code, search OV for related decisions:
- ov_find("exact technical term") for known patterns
- ov_search("conceptual description") for broader context
If a decision exists, follow it. If a lesson exists, don't repeat the mistake.
```

**Workaround:** Architect inlines all patterns in handoffs — which works but defeats OV's purpose as a team memory layer. The code agent must learn to fish.

---

## 3. LiteLLM API keys in plaintext YAML — move to .env + rotate

**Date:** 2026-05-01
**Severity:** Medium — keys on local disk outside git, but exposed in agent conversation logs

**Observed behavior:**
`~/litellm_config.yaml` contains three hardcoded API keys repeated across 10+ model entries:

- `DEEPSEEK_API_KEY` (`sk-ca2de64d...`) — used by 8 DeepSeek V4 tier models
- `OPENAI_API_KEY` (`sk-proj-VX5x...`) — used by o4-mini
- `LITELLM_MASTER_KEY` (`sk-1234`) — dev default, low risk

A stale copy exists at `~/Developer/Letta/litellm_config.yaml` with same keys + additional model entries.

**Fix needed:**

1. Rotate all three keys (they've been displayed in agent conversation)
2. Add to `.env`: `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, `LITELLM_MASTER_KEY`
3. Replace inline values in `litellm_config.yaml` with `os.environ/VAR_NAME` references
4. Recreate Docker container with `--env-file /Users/agentcafe/Developer/emdash/.env`
5. Delete stale duplicate at `~/Developer/Letta/litellm_config.yaml`
6. Add `.env.example` with documented (empty) variable templates

**Dependency:** Must recreate Docker container when applying; simple restart won't inject host env vars. If keys are changed in YAML without `--env-file`, all non-Bedrock models will return 401 and the agent team goes offline.
