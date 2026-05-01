# Pipeline Architecture

Last updated: 2026-05-01

## Agent Team

Single entry point — all work flows through the architect.

| Agent | Model | Role | When Used |
|-------|-------|------|-----------|
| **architect** | DeepSeek-V4-Pro-high | Triages tasks, produces full implementation specs, dispatches to doers | Always (entry point) |
| **code-junior** | DeepSeek-V4-Flash-none | Straightforward implementation: CRUD, wiring endpoints, cloning components, scaffolding plugins | ~80% of code tasks |
| **code-senior** | DeepSeek-V4-Flash-high | Complex implementation: state machines, race conditions, N+1 queries, hard bugs, auth flows, data migrations | ~20% of code tasks |
| **site-builder-junior** | DeepSeek-V4-Flash-none | Straightforward pages: Astro templates from design briefs, seed files, menus, taxonomies | ~80% of site tasks |
| **site-builder-senior** | DeepSeek-V4-Flash-high | Complex pages: multi-join queries, custom Portable Text renders, layout debugging, perf optimization | ~20% of site tasks |
| **review** | DeepSeek-V4-Flash-high | Adversarial code review: SQL injection, locale filters, CSRF, TOCTOU races, i18n/RTL, O(n²), Cloudflare patterns | Before every PR |
| **github** | DeepSeek-V4-Flash-none | Pipeline terminus: creates well-formed PRs after all quality gates pass | After review passes |

## Complexity Assessment (architect)

Before dispatching, the architect runs through this checklist:

```
□ State machine or multi-step workflow?
□ Race condition or concurrency concern?
□ N+1 query or performance issue?
□ Hard-to-reproduce bug?
□ New pattern (not cloned from existing code)?
□ Complex auth flow?
□ Database migration with data transformation?
```

- **0 checks** → code-junior / site-builder-junior
- **1+ checks** → code-senior / site-builder-senior

## Worktree Strategy

Git worktrees are the concurrency primitive for parallel dispatch. Each doer gets an isolated checkout:

```
/Users/agentcafe/Developer/emdash/                        ← MAIN TREE (architect only)
/Users/agentcafe/Developer/emdash-worktrees/
  └── {branch-name}/                                      ← DOER TREE (isolated)
```

**Rules:**
- Always branch from `main` (our fork with `.kilo/architecture/` and `.kilo/spec/` committed)
- One worktree per doer per task
- Architect creates worktrees
- After PR merge, github agent prunes the worktree
- `.kilo/` runtime files (agent-manager, sessions, handoff) are gitignored — survive branch switches

**Creation:**
```bash
git worktree add ../emdash-worktrees/{branch-name} -b {branch-name} main
```

Then `pnpm install` in the worktree before dispatching.

## Pipeline Stages

```
user → architect (main tree, triage + spec + dispatch)
         │
         ├─→ code/site doer (worktree)
         │     │
         │     ├─ Writes code + tests (same pass)
         │     ├─ Runs quality gates locally:
         │     │   pnpm lint:quick → 0
         │     │   pnpm typecheck   → pass
         │     │   pnpm format      → clean
         │     │   pnpm test        → all pass
         │     ├─ Commits
         │     └─ Hands off to review
         │
         ├─→ review (adversarial)
         │     │
         │     ├─ SQL injection audit
         │     ├─ Locale filter correctness
         │     ├─ CSRF / TOCTOU races
         │     ├─ i18n / RTL compliance
         │     ├─ Performance (N+1, missing indexes)
         │     ├─ Cloudflare pattern verification
         │     │
         │     ├─ PASS → github agent
         │     └─ FAIL → back to doer
         │
         └─→ github (pipeline terminus)
               │
               ├─ Pushes branch to origin (agentcafe/emdash)
               ├─ Creates PR via gh pr create (targets upstream/main)
               ├─ Andy reviews and merges in GitHub web UI
               └─ After merge → prunes worktree
```

## GitHub Flow

We use a fork-based workflow.

| Remote | URL | Role |
|--------|-----|------|
| `origin` | `github.com/agentcafe/emdash` | Our fork — branches pushed here |
| `upstream` | `github.com/emdash-cms/emdash` | Main project — PRs target this |

**PR creation:** The github agent pushes the branch to origin, then creates the PR via `gh pr create --head agentcafe:{branch} --base main --repo emdash-cms/emdash`. Andy reviews, approves, and merges in the GitHub web UI.

## Handoff Protocol (architect → doer)

1. Write complete spec to `.kilo/spec/{task}.md` or `.kilo/architecture/talent247/{age}.md`
2. Commit session to OpenViking
3. Write handoff marker to `.kilo/handoff/current.md`
4. Dispatch via `<switch_mode>` with:
   - Agent selection (code-junior, code-senior, etc.)
   - Task summary
   - Complexity assessment
   - Worktree path and branch
   - Spec file location
   - Quality gates

## Quality Gates (standard for all doers)

```
pnpm --silent lint:json | jq '.diagnostics | length'  # Must be 0
pnpm typecheck                                          # Must pass
pnpm format                                             # Must be clean
pnpm test                                               # All tests pass
```

## Spec Locations

- Talent247 specs: `.kilo/architecture/talent247/` (not on disk yet — restore if needed)
- Task-level specs: `.kilo/spec/` (e.g. `.kilo/spec/phase-1-jobs-schema.md`)
- Pipeline architecture: `.kilo/architecture/pipeline.md` (this file)
