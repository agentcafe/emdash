---
description: Run full quality gates and create PR (code → review → github pipeline)
agent: code
---

Run the full release pipeline on the current branch:

1. Run `pnpm --silent lint:quick` — fix any issues
2. Run `pnpm typecheck` — fix any issues
3. Run `pnpm test` — all must pass
4. Run `pnpm format` — apply formatting
5. Verify changeset exists if `packages/` changed
6. Hand off to `review` for adversarial review
7. If review passes, hand off to `github` for PR creation

This is the full code → review → github pipeline without going through `plan` for routing.
