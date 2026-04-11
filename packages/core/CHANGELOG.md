# emdash

## 0.2.0

### Minor Changes

- [#367](https://github.com/emdash-cms/emdash/pull/367) [`8f44ec2`](https://github.com/emdash-cms/emdash/commit/8f44ec23a4b23f636f9689c075d29edfa4962c7c) Thanks [@ttmx](https://github.com/ttmx)! - Adds `content:afterPublish` and `content:afterUnpublish` plugin hooks, fired after content is published or unpublished. Both are fire-and-forget notifications requiring `read:content` capability, supporting trusted and sandboxed plugins.

- [#111](https://github.com/emdash-cms/emdash/pull/111) [`87b0439`](https://github.com/emdash-cms/emdash/commit/87b0439927454a275833992de4244678b47b9aa3) Thanks [@mvanhorn](https://github.com/mvanhorn)! - Adds repeater field type for structured repeating data

### Patch Changes

- [#182](https://github.com/emdash-cms/emdash/pull/182) [`156ba73`](https://github.com/emdash-cms/emdash/commit/156ba7350070400e5877e3a54d33486cd0d33640) Thanks [@masonjames](https://github.com/masonjames)! - Fixes media routes so storage keys with slashes resolve correctly.

- [#94](https://github.com/emdash-cms/emdash/pull/94) [`da957ce`](https://github.com/emdash-cms/emdash/commit/da957ce8ec18953995e6e00e0a38e5d830f1a381) Thanks [@eyupcanakman](https://github.com/eyupcanakman)! - Reject dangerous URL schemes in menu custom links

- [#148](https://github.com/emdash-cms/emdash/pull/148) [`1989e8b`](https://github.com/emdash-cms/emdash/commit/1989e8b4c432a05d022baf2196dec2680b2e2fd0) Thanks [@masonjames](https://github.com/masonjames)! - Adds public plugin settings helpers.

- [#72](https://github.com/emdash-cms/emdash/pull/72) [`724191c`](https://github.com/emdash-cms/emdash/commit/724191cf96d5d79b22528a167de8c45146fb0746) Thanks [@travisbreaks](https://github.com/travisbreaks)! - Fix CLI login against remote Cloudflare-deployed instances by unwrapping API response envelope and adding admin scope

- [#119](https://github.com/emdash-cms/emdash/pull/119) [`e1014ef`](https://github.com/emdash-cms/emdash/commit/e1014eff18301ff68ac75d19157d3500ebe890c5) Thanks [@blmyr](https://github.com/blmyr)! - Fix plugin `page:metadata` and `page:fragments` hooks not firing for anonymous public page visitors. The middleware's early-return fast-path for unauthenticated requests now initializes the runtime (skipping only the manifest query), so plugin contributions render via `<EmDashHead>`, `<EmDashBodyStart>`, and `<EmDashBodyEnd>` for all visitors. Also adds `collectPageMetadata` and `collectPageFragments` to the `EmDashHandlers` interface.

- Updated dependencies [[`3b6b75b`](https://github.com/emdash-cms/emdash/commit/3b6b75b01b5674776cb588506d75042d4a2745ea), [`87b0439`](https://github.com/emdash-cms/emdash/commit/87b0439927454a275833992de4244678b47b9aa3), [`5eeab91`](https://github.com/emdash-cms/emdash/commit/5eeab918820f680ea8b46903df7d69969af8b8ee), [`e3f7db8`](https://github.com/emdash-cms/emdash/commit/e3f7db8bb670bb7444632ab0cd4e680e4c9029b3)]:
  - @emdash-cms/admin@0.2.0

## 0.1.1

### Patch Changes

- [#200](https://github.com/emdash-cms/emdash/pull/200) [`422018a`](https://github.com/emdash-cms/emdash/commit/422018aeb227dffe3da7bfc772d86f9ce9c2bcd1) Thanks [@ascorbic](https://github.com/ascorbic)! - Replace placeholder text branding with proper EmDash logo SVGs across admin UI, playground loading page, and preview interstitial

- [#206](https://github.com/emdash-cms/emdash/pull/206) [`4221ba4`](https://github.com/emdash-cms/emdash/commit/4221ba48bc87ab9fa0b1bae144f6f2920beb4f5a) Thanks [@tsikatawill](https://github.com/tsikatawill)! - Fixes multiSelect custom fields rendering as plain text inputs instead of a checkbox group.

- [#133](https://github.com/emdash-cms/emdash/pull/133) [`9269759`](https://github.com/emdash-cms/emdash/commit/9269759674bf254863f37d4cf1687fae56082063) Thanks [@kyjus25](https://github.com/kyjus25)! - Fix auth links and OAuth callbacks to use `/_emdash/api/auth/...` so emailed sign-in, signup, and invite URLs resolve correctly in EmDash.

- [#365](https://github.com/emdash-cms/emdash/pull/365) [`d6cfc43`](https://github.com/emdash-cms/emdash/commit/d6cfc437f23e3e435a8862cab17d2c19363847d7) Thanks [@ascorbic](https://github.com/ascorbic)! - Fixes migration 033 failing with "index already exists" on databases where the schema registry had already created composite indexes on content tables.

- [#313](https://github.com/emdash-cms/emdash/pull/313) [`1bcfc50`](https://github.com/emdash-cms/emdash/commit/1bcfc502112d8756e34a720b8a170eb5486b425a) Thanks [@mvanhorn](https://github.com/mvanhorn)! - Remove FTS5 integrity-check from startup verification to prevent D1 shadow table corruption

- [#262](https://github.com/emdash-cms/emdash/pull/262) [`8c693b5`](https://github.com/emdash-cms/emdash/commit/8c693b582d7c5e29bd138161e81d9c8affb53689) Thanks [@BenjaminPrice](https://github.com/BenjaminPrice)! - Fix media upload OOM on Cloudflare Workers for large images by generating blurhash from client-provided thumbnails instead of decoding full-resolution images server-side

- [#330](https://github.com/emdash-cms/emdash/pull/330) [`5b3e33c`](https://github.com/emdash-cms/emdash/commit/5b3e33c26bc2eb30ab2a032960a5d57eb06f148a) Thanks [@MattieTK](https://github.com/MattieTK)! - Fixes migration 033 (optimize content indexes) not being registered in the static migration runner, so the composite and partial indexes it defines are now actually applied on startup.

- [#181](https://github.com/emdash-cms/emdash/pull/181) [`9d10d27`](https://github.com/emdash-cms/emdash/commit/9d10d2791fe16be901d9d138e434bd79cf9335c4) Thanks [@ilicfilip](https://github.com/ilicfilip)! - fix(admin): use collection urlPattern for preview button fallback URL

- [#363](https://github.com/emdash-cms/emdash/pull/363) [`91e31fb`](https://github.com/emdash-cms/emdash/commit/91e31fb2cab4c0470088c5d61bab6e2028821569) Thanks [@ascorbic](https://github.com/ascorbic)! - Fixes sandboxed plugin entries failing when package exports point to unbuilt TypeScript source. Adds build-time and bundle-time validation to catch misconfigured plugin exports early.

- [#298](https://github.com/emdash-cms/emdash/pull/298) [`f112ac4`](https://github.com/emdash-cms/emdash/commit/f112ac48194d1c2302e93756d54b116d3d207c22) Thanks [@BenjaminPrice](https://github.com/BenjaminPrice)! - Fixes install telemetry using an unstable hash that inflated install counts. Uses the site's request origin as a stable hash seed for accurate per-site deduplication. Denormalizes install_count on the marketplace plugins table for query performance.

- [#214](https://github.com/emdash-cms/emdash/pull/214) [`e9a6f7a`](https://github.com/emdash-cms/emdash/commit/e9a6f7ac3ceeaf5c2d0a557e4cf6cab5f3d7d764) Thanks [@SARAMALI15792](https://github.com/SARAMALI15792)! - Optimizes D1 database indexes to eliminate full table scans in admin panel. Adds
  composite indexes on ec\_\* content tables for common query patterns (deleted_at +
  updated_at/created_at + id) and rewrites comment counting to use partial indexes.
  Reduces D1 row reads by 90%+ for dashboard operations.

- [#107](https://github.com/emdash-cms/emdash/pull/107) [`b297fdd`](https://github.com/emdash-cms/emdash/commit/b297fdd88dadcabeb93f47abea9f24f70b7d4b71) Thanks [@mvanhorn](https://github.com/mvanhorn)! - Allows public access to search API for frontend LiveSearch

- [#225](https://github.com/emdash-cms/emdash/pull/225) [`d211452`](https://github.com/emdash-cms/emdash/commit/d2114523a55021f65ee46e44e11157b06334819e) Thanks [@seslly](https://github.com/seslly)! - Adds `passkeyPublicOrigin` on `emdash()` so WebAuthn `origin` and `rpId` match the browser when dev sits behind a TLS-terminating reverse proxy. Validates the value at integration load time and threads it through all passkey-related API routes.

  Updates the admin passkey setup and login flows to detect non-secure origins and explain that passkeys need HTTPS or `http://localhost` rather than implying the browser lacks WebAuthn support.

- [#105](https://github.com/emdash-cms/emdash/pull/105) [`8e28cfc`](https://github.com/emdash-cms/emdash/commit/8e28cfc5d66f58f0fb91aa35c02afdd426bb6555) Thanks [@ascorbic](https://github.com/ascorbic)! - Fix CLI `--json` flag so JSON output is clean. Previously, `consola.success()` and other log messages leaked into stdout alongside the JSON data, making it unparseable by scripts. Log messages now go to stderr when `--json` is set.

- [#83](https://github.com/emdash-cms/emdash/pull/83) [`38af118`](https://github.com/emdash-cms/emdash/commit/38af118ad517fd9aa83064368543bf64bc32c08a) Thanks [@antoineVIVIES](https://github.com/antoineVIVIES)! - Sanitize WordPress post type slugs during import. Fixes crashes when importing sites using plugins (Elementor, WooCommerce, ACF, etc.) that register post types with hyphens, uppercase letters, or other characters invalid in EmDash collection slugs. Reserved collection slugs are prefixed with `wp_` to avoid conflicts.

- Updated dependencies [[`12d73ff`](https://github.com/emdash-cms/emdash/commit/12d73ff4560551bbe873783e4628bbd80809c449), [`422018a`](https://github.com/emdash-cms/emdash/commit/422018aeb227dffe3da7bfc772d86f9ce9c2bcd1), [`9269759`](https://github.com/emdash-cms/emdash/commit/9269759674bf254863f37d4cf1687fae56082063), [`71744fb`](https://github.com/emdash-cms/emdash/commit/71744fb8b2bcc7f48acea41f9866878463a4f4f7), [`018be7f`](https://github.com/emdash-cms/emdash/commit/018be7f1c3a8b399a9f38d7fa524e6f2908d95c3), [`9d10d27`](https://github.com/emdash-cms/emdash/commit/9d10d2791fe16be901d9d138e434bd79cf9335c4), [`d211452`](https://github.com/emdash-cms/emdash/commit/d2114523a55021f65ee46e44e11157b06334819e), [`ab21f29`](https://github.com/emdash-cms/emdash/commit/ab21f29f713a5aa4c087c535608e1a2cab2ef9e0), [`bfcda12`](https://github.com/emdash-cms/emdash/commit/bfcda121400ee2bbbc35d666cc8bed38e0eba8ea), [`5f448d1`](https://github.com/emdash-cms/emdash/commit/5f448d1035073283fd7435d2f320d1f3c94898a0)]:
  - @emdash-cms/admin@0.1.1
  - @emdash-cms/auth@0.1.1

## 0.1.0

### Minor Changes

- [#14](https://github.com/emdash-cms/emdash/pull/14) [`755b501`](https://github.com/emdash-cms/emdash/commit/755b5017906811f97f78f4c0b5a0b62e67b52ec4) Thanks [@ascorbic](https://github.com/ascorbic)! - First beta release

### Patch Changes

- Updated dependencies [[`755b501`](https://github.com/emdash-cms/emdash/commit/755b5017906811f97f78f4c0b5a0b62e67b52ec4)]:
  - @emdash-cms/admin@0.1.0
  - @emdash-cms/auth@0.1.0
  - @emdash-cms/gutenberg-to-portable-text@0.1.0

## 0.0.3

### Patch Changes

- [#8](https://github.com/emdash-cms/emdash/pull/8) [`3c319ed`](https://github.com/emdash-cms/emdash/commit/3c319ed6411a595e6974a86bc58c2a308b91c214) Thanks [@ascorbic](https://github.com/ascorbic)! - Fix crash on fresh deployments when the first request hits a public page before setup has run. The middleware now detects an empty database and redirects to the setup wizard instead of letting template helpers query missing tables.

- Updated dependencies [[`3c319ed`](https://github.com/emdash-cms/emdash/commit/3c319ed6411a595e6974a86bc58c2a308b91c214)]:
  - @emdash-cms/admin@0.0.2

## 0.0.2

### Patch Changes

- [#2](https://github.com/emdash-cms/emdash/pull/2) [`b09bfd5`](https://github.com/emdash-cms/emdash/commit/b09bfd51cece5e88fe8314668a591ab11de36b4d) Thanks [@ascorbic](https://github.com/ascorbic)! - Fix virtual module resolution errors when emdash is installed from npm on Cloudflare. The esbuild dependency pre-bundler was encountering `virtual:emdash/*` imports while crawling dist files and failing to resolve them. These are now excluded from the optimizeDeps scan.
