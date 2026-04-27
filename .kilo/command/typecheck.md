---
description: Run type checking across the monorepo
---

Run full type checking:

```bash
pnpm typecheck
pnpm typecheck:demos
```

If $ARGUMENTS specifies a package, scope to that package:

```bash
pnpm --filter $1 typecheck
```

Report any errors with file paths, line numbers, and suggested fixes. Fixes must be minimal — don't touch code outside the scope of the type error.
