---
description: Scaffold and implement an EmDash plugin
agent: plugin-builder
---

Build an EmDash plugin following the creating-plugins skill. Determine whether standard or native format is needed based on what $ARGUMENTS describes.

For standard plugins:

1. Create `src/index.ts` — descriptor factory with id, version, capabilities
2. Create `src/sandbox-entry.ts` — `definePlugin()` default export with hooks/routes
3. Ensure `package.json` exports `"."` and `"./sandbox"`
4. For admin pages/widgets, use Block Kit JSON (no React needed)
5. Run `pnpm typecheck` to verify

For native plugins (React admin UI or PT blocks):

1. All of the above plus `src/admin.tsx` (React) and/or `src/astro/index.ts`
2. Add `#admin/*` and `#astro/*` imports as needed

Always follow the descriptor/definition separation pattern from the creating-plugins skill.
