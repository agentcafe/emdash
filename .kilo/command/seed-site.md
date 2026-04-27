---
description: Build or update an EmDash site from seed file
agent: site-builder
---

Build or update an EmDash site. Use the building-emdash-site skill for all patterns.

If $ARGUMENTS includes references to a seed file:

1. Validate the seed: `npx emdash seed $1 --validate`
2. Review collection schemas, taxonomies, menus, widgets for correctness
3. Build pages following the querying-and-rendering reference

If no seed file is specified:

1. Start `npx emdash dev` to run the dev server
2. Generate types: `npx emdash types`
3. Work on the pages/components described in $ARGUMENTS

Always run `pnpm typecheck` and `pnpm format` after page changes.
