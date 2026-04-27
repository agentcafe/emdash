---
name: designer-reference
description: "Visual design reference for the EmDash Site Designer agent. Provides Kumo component gallery, semantic color token mappings, layout pattern library, typography scale samples, and responsive breakpoint specifications. Use when the designer agent is producing Design Briefs from screenshots or needs concrete visual references to accurately map design elements to EmDash component names, Kumo tokens, and Astro layout patterns."
license: Apache-2.0
compatibility: "Requires EmDash CMS + Astro project with Kumo design system"
metadata:
  author: emdash-cms
  version: "1.0"
---

# Designer Reference

Visual design reference for the EmDash Site Designer agent. Provides concrete mappings from visual design elements to EmDash component names, Kumo semantic tokens, Astro layout patterns, and responsive breakpoint configurations. All content is organized for pattern-matching — the designer finds the closest visual match and adapts it.

## Design Notes — Why This Skill Works

This skill was validated on a Qwen3.6-35B agent producing Design Briefs from text descriptions. The agent successfully mapped described layouts to Kumo components, color tokens, typography scales, and responsive breakpoints without fine-tuning. Key success factors:

1. **Single source of truth.** All tokens, components, and patterns are in one skill. The agent's prompt delegates to the skill rather than duplicating content. No stale inline references.
2. **Gotchas are highest-value content.** Common errors (dark: prefixes, raw Tailwind colors, image-as-string, id-vs-slug) are in the SKILL.md body, not buried in reference files. The agent encounters them early.
3. **Output template anchors quality.** A complete Design Brief example at the end of the skill gives the agent a concrete target to pattern-match. Generic section descriptions aren't enough — a worked example is.
4. **Visual screenshots supplement text.** 15 screenshots (Kumo docs + live EmDash site) in `references/screenshots/` provide visual ground truth for vision-capable agents. Text descriptions alone won't match rendered components.
5. **Actual source tokens, not guessed names.** Color tokens were extracted from `theme-kumo.css` source, not inferred from conventions. `bg-kumo-canvas` not `bg-kumo-surface`. Incorrect token names are the most common failure mode.
6. **Length target respected.** 602 lines / ~4,500 tokens. Fits in context alongside agent prompt and conversation without crowding.

When creating similar skills for other agent roles, follow this pattern: gotchas first, output template last, source-verified references, visual supplements for vision agents.

## When to Use

USE this skill when:

- Designer agent is producing a Design Brief from a screenshot
- Designer needs to identify which Kumo component matches a visual element
- Designer needs to map colors to Kumo semantic tokens (never raw Tailwind colors except `white`/`black`/`transparent`, never `dark:` prefixes)
- Designer needs layout pattern references (hero, card grid, CTA, footer)
- Designer needs typography scale and font pairing recommendations
- Designer needs responsive breakpoint behavior specifications
- Designer is unsure which EmDash UI component to recommend for a content feature

DO NOT use this skill when:

- Writing Astro component code → use building-emdash-site skill
- Designing database schemas or content models → use architect agent
- Running dev tools or building the project → use code agent

## Procedure

1. **Identify the visual element** — is it a button, form, card, navigation, hero section, content area?
2. **Find the closest match** in the Component Gallery section below
3. **Map color to token** — use the Color Token Reference (never raw Tailwind except `white`/`black`/`transparent`, never `dark:`)
4. **Select the layout pattern** — from the Layout Pattern Library
5. **Apply typography scale** — from the Typography Reference
6. **Set responsive behavior** — from the Responsive Breakpoints table
7. **Output in Design Brief format** — use the Output Template section as a pattern

## Component Gallery

### Kumo Components (from `@cloudflare/kumo`)

**Button** — all clickable actions

- `variant`: `"primary"`, `"secondary"`, `"ghost"`, `"danger"`
- `size`: `"sm"`, `"md"`, `"lg"`
- `icon`: Phosphor icon component or React element
- `loading`: boolean — shows spinner, disables interaction
- `shape`: `"square"` for icon-only buttons (requires `aria-label`)
- Pattern: `{/* Hero CTA */} <Button variant="primary" size="lg">Get Started</Button>`
- Pattern: `{/* Destructive action */} <Button variant="danger" shape="square" icon={TrashIcon} aria-label="Delete" />`

**LinkButton** — navigation links styled as buttons

- `href`: URL string
- `external`: boolean — opens in new tab with `rel="noopener noreferrer"`
- All Button props apply
- Pattern: `{/* Docs link */} <LinkButton href="https://docs.example.com" external>Documentation</LinkButton>`

**Card** — content containers

- `padding`: `"none"`, `"sm"`, `"md"`, `"lg"`
- `variant`: `"default"`, `"elevated"`, `"outlined"`
- Pattern: `{/* Blog post card */} <Card padding="lg" variant="elevated">...</Card>`

**Input** — text input fields

- `type`: `"text"`, `"email"`, `"password"`, `"number"`
- `placeholder`: string
- `error`: string — shows error state with message
- Always pair with `Label` component

**Textarea** — multi-line text input (Kumo component name: `InputArea`)

- `rows`: number
- `placeholder`: string
- Always pair with `Label` component

**Select** — dropdown selection

- `options`: `{ value: string, label: string }[]`
- `placeholder`: string
- Always pair with `Label` component

**Checkbox** — boolean toggle

- `label`: string
- `checked`: boolean
- `onChange`: handler

**Switch** — toggle switch (alternative to checkbox)

- Same props as Checkbox
- Use for settings toggles, not form agreements

**Dialog** — modal overlay

- `open`: boolean
- `onClose`: handler
- Use `ConfirmDialog` (EmDash component, see below) for destructive actions

**Badge** — status labels and counts

- Content: text or number
- Sits inline next to content
- Pattern: `{/* Draft status */} <Badge>Draft</Badge>`
- Pattern: `{/* Count */} <Badge>3</Badge>`

**Loader** — loading spinner

- `size`: `"sm"`, `"md"`, `"lg"`
- Pattern: `{/* Async content */} {isLoading && <Loader size="md" />}`

**Popover** — small overlay anchored to trigger element
**Dropdown** — selection menu overlay
**Tooltip** — hover text overlay
**Label** — form field labels (always pairs with Input, Textarea, Select)

### EmDash UI Components (from `"emdash/ui"`)

**PortableText** — renders rich text content from the database

- `value`: Portable Text data from content entry
- Pattern: `<PortableText value={post.data.body} />`
- Never use `<div dangerouslySetInnerHTML>` or raw HTML

**Image** — renders EmDash image objects correctly

- `image`: `{ id: string, src: string, alt: string }` — from `post.data.featured_image`
- Never use `<img src={...} />` — image fields are objects, not strings
- Pattern: `<Image image={post.data.featured_image} />`

**WidgetArea** — renders widget areas by name

- `name`: widget area slug from seed file
- Pattern: `<WidgetArea name="sidebar" />`

**EmDashHead** — SEO head tags (title, meta, OG, canonical)

- Include in every page layout
- Reads from content entry data and site settings

**LiveSearch** — client-side search component (from `"emdash/ui/search"`)

- Pattern: `<LiveSearch collection="posts" />`

**CommentForm** — comment submission form

- `contentId`: ULID of the content entry being commented on
- `contentType`: `"posts"` or collection slug

**Comments** — renders comment threads for a content entry

- `contentId`: ULID
- Pattern: `<Comments contentId={entry.data.id} />`

### ConfirmDialog (EmDash pattern, not a Kumo import)

Located at `components/ConfirmDialog.tsx` in the admin UI. In site templates, use Kumo `Dialog` with manual confirmation pattern:

```
<Dialog open={isOpen} onClose={onClose}>
  <h2>Confirm Action</h2>
  <p>Description of what will happen</p>
  <Button variant="danger" onClick={onConfirm} loading={isPending}>Confirm</Button>
  <Button variant="ghost" onClick={onClose}>Cancel</Button>
</Dialog>
```

## Color Token Reference

**Critical rule:** Never use raw Tailwind colors (`bg-blue-500`, `text-gray-600`) or `dark:` prefixes (`dark:bg-gray-800`). Kumo semantic tokens use CSS `light-dark()` to handle dark mode automatically. The token name is all you need.

**Exception:** The raw color classes `bg-white`, `bg-black`, `text-white`, `text-black`, and `transparent` are explicitly allowed. All other color references must use Kumo semantic tokens.

| Category    | Token                   | Visual                            | Use for                                       |
| ----------- | ----------------------- | --------------------------------- | --------------------------------------------- |
| **Surface** | `bg-kumo-canvas`        | Page background                   | Main page background                          |
|             | `bg-kumo-base`          | White in light, dark gray in dark | Card backgrounds, default surface             |
|             | `bg-kumo-elevated`      | Slightly lighter/darker than base | Elevated cards, dropdowns, modals             |
|             | `bg-kumo-overlay`       | Dark semi-transparent             | Modal backdrops, overlay panels               |
|             | `bg-kumo-contrast`      | High contrast                     | High contrast surface areas                   |
|             | `bg-kumo-recessed`      | Contextual background             | Contextual background areas                   |
| **Brand**   | `bg-kumo-brand`         | Primary brand color (#f6821f)     | Primary buttons, active states, brand accents |
|             | `bg-kumo-brand-hover`   | Brand hover state                 | Hover state for brand backgrounds             |
|             | `text-kumo-brand`       | Same color, text variant          | Brand-colored text (#f6821f)                  |
| **Text**    | `text-kumo-default`     | Main body text                    | Body text, headings, primary content          |
|             | `text-kumo-strong`      | Emphasized                        | Headings, emphasized text                     |
|             | `text-kumo-subtle`      | Muted                             | Secondary text, metadata, timestamps          |
|             | `text-kumo-inactive`    | Most muted                        | Disabled text                                 |
|             | `text-kumo-placeholder` | Placeholder style                 | Input placeholders                            |
|             | `text-kumo-inverse`     | White or near-white               | Text on brand/dark backgrounds                |
|             | `text-kumo-link`        | Blue                              | Link text                                     |
| **Border**  | `border-kumo-line`      | Standard border                   | Card borders, input borders, dividers         |
|             | `border-kumo-hairline`  | Thinner/subtler border            | Subtle separators, fine lines                 |
| **Status**  | `text-kumo-success`     | Green                             | Success messages, published status            |
|             | `text-kumo-warning`     | Amber/Yellow                      | Warning messages, scheduled status            |
|             | `text-kumo-danger`      | Red                               | Error messages, validation failures           |
|             | `text-kumo-info`        | Blue                              | Info messages, tips                           |

### Common Color Patterns

```
// Card with elevated surface
<Card className="bg-kumo-elevated border border-kumo-line">

// Primary button (brand background + inverse text — NEVER use white text directly)
<Button className="bg-kumo-brand text-kumo-inverse">

// Hero section with brand background
<section className="bg-kumo-brand">
  <h1 className="text-kumo-inverse text-4xl font-bold">...</h1>
  <p className="text-kumo-inverse opacity-90">...</p>
</section>

// Section with page background
<section className="bg-kumo-canvas">
  <h2 className="text-kumo-default">...</h2>
  <p className="text-kumo-subtle">...</p>
</section>

// Status badges
<Badge className="text-kumo-success">Published</Badge>
<Badge className="text-kumo-warning">Scheduled</Badge>
<Badge className="text-kumo-danger">Draft</Badge>
```

## Layout Pattern Library

### Hero Section

```
<section className="bg-kumo-brand py-16 md:py-24">
  <div className="max-w-4xl mx-auto px-4 text-center">
    <h1 className="text-kumo-inverse text-3xl md:text-5xl font-bold mb-4">Heading</h1>
    <p className="text-kumo-inverse text-lg md:text-xl opacity-90 mb-8 max-w-2xl mx-auto">Subheading text.</p>
    <div className="flex gap-4 justify-center">
      <Button variant="primary" size="lg">Primary CTA</Button>
      <LinkButton href="/learn" variant="secondary">Learn More</LinkButton>
    </div>
  </div>
</section>
```

Visual: Full-width brand-colored background. Centered text. Large heading. Subheading with reduced opacity. Two CTA buttons side by side (primary + secondary). Stacks vertically on mobile.

### Card Grid (3-column)

```
<section className="bg-kumo-canvas py-16">
  <div className="max-w-7xl mx-auto px-4">
    <h2 className="text-kumo-default text-2xl md:text-3xl font-bold text-center mb-12">Section Heading</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {items.map(item => (
        <Card key={item.id} padding="lg" variant="elevated">
          <Image image={item.data.featured_image} />
          <h3 className="text-kumo-default text-xl font-semibold mt-4 mb-2">{item.data.title}</h3>
          <p className="text-kumo-subtle">{item.data.excerpt}</p>
          <LinkButton href={`/${item.id}`} variant="ghost" className="mt-4">Read more →</LinkButton>
        </Card>
      ))}
    </div>
  </div>
</section>
```

Visual: Light background section. Centered heading above grid. 3 columns on desktop, 2 on tablet, 1 on mobile. Cards with images, headings, excerpts, and links. Equal height cards with elevated surface.

### Content + Sidebar (Two-column)

```
<div className="max-w-7xl mx-auto px-4 py-16">
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <main className="lg:col-span-2">
      <article className="bg-kumo-elevated rounded-lg p-6 md:p-8">
        <h1 className="text-kumo-default text-3xl font-bold mb-4">{post.data.title}</h1>
        <div className="text-kumo-subtle mb-6">
          <span>{post.data.author}</span>
          <span className="mx-2">·</span>
          <time>{post.data.published_at}</time>
        </div>
        <div className="text-kumo-default prose max-w-none">
          <PortableText value={post.data.body} />
        </div>
      </article>
      <Comments contentId={post.data.id} />
      <CommentForm contentId={post.data.id} />
    </main>
    <aside className="lg:col-span-1">
      <WidgetArea name="sidebar" />
    </aside>
  </div>
</div>
```

Visual: Main content area (2/3 width) with article, comments, and comment form. Sidebar (1/3 width) with widgets. Single column on mobile. Cards use elevated surface with padding.

### CTA Banner

```
<section className="bg-kumo-brand py-12">
  <div className="max-w-3xl mx-auto px-4 text-center">
    <h2 className="text-kumo-inverse text-2xl md:text-3xl font-bold mb-4">Ready to get started?</h2>
    <p className="text-kumo-inverse text-lg opacity-90 mb-6">Join thousands of developers building with EmDash.</p>
    <div className="flex gap-4 justify-center">
      <Button variant="primary" size="lg">Get Started</Button>
      <LinkButton href="/pricing" variant="secondary">View Pricing</LinkButton>
    </div>
  </div>
</section>
```

Visual: Full-width brand band. Centered heading + subheading + two CTAs. Darker than surrounding sections. Used before footer or between content sections.

### Footer

```
<footer className="bg-kumo-elevated border-t border-kumo-line py-12">
  <div className="max-w-7xl mx-auto px-4">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
      <div>
        <h4 className="text-kumo-default font-semibold mb-4">Product</h4>
        <ul className="space-y-2">
          <li><LinkButton href="/features" variant="ghost">Features</LinkButton></li>
          <li><LinkButton href="/pricing" variant="ghost">Pricing</LinkButton></li>
        </ul>
      </div>
      <!-- Repeat for Company, Resources, Legal columns -->
    </div>
    <div className="border-t border-kumo-line mt-8 pt-8 text-center text-kumo-subtle">
      <p>© {new Date().getFullYear()} Site Name. All rights reserved.</p>
    </div>
  </div>
</footer>
```

Visual: Elevated surface with top border. 4-column grid of link groups (2 on mobile). Copyright bar at bottom. Uses semantic text tokens throughout.

### Navigation Bar

```
<nav className="bg-kumo-canvas border-b border-kumo-line">
  <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
    <LinkButton href="/" variant="ghost" className="text-kumo-default font-bold text-lg">Logo</LinkButton>
    <div className="hidden md:flex items-center gap-6">
      <LinkButton href="/blog" variant="ghost">Blog</LinkButton>
      <LinkButton href="/about" variant="ghost">About</LinkButton>
      <Button variant="primary" size="sm">Get Started</Button>
    </div>
    <Button variant="ghost" shape="square" className="md:hidden" aria-label="Menu">
      MenuIcon
    </Button>
  </div>
</nav>
```

Visual: Sticky top bar. Logo left, nav links center-right, CTA button far right. Hamburger menu on mobile. Bottom border separator. Background matches page surface.

## Typography Reference

### Font Pairings

| Style            | Heading Font             | Body Font             | Use for                                                 |
| ---------------- | ------------------------ | --------------------- | ------------------------------------------------------- |
| **Professional** | Inter (sans-serif)       | Inter (sans-serif)    | SaaS, B2B, tech blogs, documentation sites              |
| **Editorial**    | Playfair Display (serif) | Inter or Source Serif | News sites, long-form content, literary blogs           |
| **Modern**       | Space Grotesk or DM Sans | Inter                 | Portfolio sites, creative agencies, design portfolios   |
| **Classic**      | Merriweather (serif)     | Merriweather (serif)  | Academic sites, legal content, traditional publications |

### Scale

```
h1: text-3xl md:text-5xl font-bold        — page titles, hero headings
h2: text-2xl md:text-3xl font-bold        — section headings
h3: text-xl md:text-2xl font-semibold     — card titles, subsection headings
h4: text-lg font-semibold                  — footer column headings, sidebar headings
body: text-base (16px)                     — body text, paragraphs
small: text-sm text-kumo-secondary         — metadata, timestamps, captions
micro: text-xs text-kumo-subtle            — legal text, fine print
```

### Pairing with Color Tokens

```
h1, h2, h3, h4 → text-kumo-default (always)
body, p, li    → text-kumo-default
.meta, time    → text-kumo-subtle
.caption, figcaption → text-kumo-subtle
```

## Responsive Breakpoints

| Breakpoint | Width      | Columns    | Navigation               | Images              |
| ---------- | ---------- | ---------- | ------------------------ | ------------------- |
| `sm`       | < 640px    | 1 column   | Hamburger menu           | Full-width          |
| `md`       | 640–1024px | 2 columns  | Horizontal nav (compact) | Half-width or full  |
| `lg`       | > 1024px   | 3+ columns | Full horizontal nav      | Original dimensions |

### Responsive Patterns

```
// Stack on mobile, grid on desktop
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"

// Hide on mobile, show on desktop
className="hidden md:flex"

// Full-width on mobile, constrained on desktop
className="max-w-full md:max-w-7xl mx-auto px-4"

// Padding scales with viewport
className="py-10 md:py-16 lg:py-24"

// Text scales with viewport
className="text-2xl md:text-3xl lg:text-5xl"

// Sidebar collapses below content on mobile
className="grid grid-cols-1 lg:grid-cols-3 gap-8"  // main: lg:col-span-2, aside: lg:col-span-1
```

## Spacing Reference

### Section Spacing

```
py-10 md:py-16    — standard section padding
py-16 md:py-24    — hero section padding
py-12              — CTA banner padding
py-8 md:py-12     — compact sections (testimonials, logos)
```

### Container Widths

```
max-w-7xl (1280px) — standard page container
max-w-4xl (896px)  — narrow content (blog posts, documentation)
max-w-3xl (768px)  — very narrow (newsletters, forms)
max-w-full         — full bleed (hero sections, CTAs)
```

### Gap Values

```
gap-4  — between elements within a section
gap-6  — between cards in a grid
gap-8  — between major layout blocks
gap-12 — between unrelated sections
```

## RTL-Safe Layout Rules

**Critical rule:** All layout classes must use logical properties. Physical properties break RTL layout. Kumo components handle this automatically for their internals.

| Use (RTL-Safe)                 | Never (Breaks RTL)     |
| ------------------------------ | ---------------------- |
| `ms-*` (margin-inline-start)   | `ml-*` (margin-left)   |
| `me-*` (margin-inline-end)     | `mr-*` (margin-right)  |
| `ps-*` (padding-inline-start)  | `pl-*` (padding-left)  |
| `pe-*` (padding-inline-end)    | `pr-*` (padding-right) |
| `start-*` (inset-inline-start) | `left-*`               |
| `end-*` (inset-inline-end)     | `right-*`              |
| `text-start`                   | `text-left`            |
| `text-end`                     | `text-right`           |
| `border-s`                     | `border-l`             |
| `border-e`                     | `border-r`             |
| `rounded-s-*`                  | `rounded-l-*`          |
| `rounded-e-*`                  | `rounded-r-*`          |
| `float-start`                  | `float-left`           |
| `float-end`                    | `float-right`          |

Directional icons (chevrons, arrows) should use `rtl:-scale-x-100` to flip in RTL locales.

## Gotchas

- **Image fields are objects, not strings.** `post.data.featured_image` returns `{ id, src, alt }`. Always use `<Image image={post.data.featured_image} />` from `"emdash/ui"`. Never use `<img src={post.data.featured_image} />` — it will render `[object Object]`.
- **`entry.id` vs `entry.data.id`.** `entry.id` is the slug (use for URLs: `/blog/${entry.id}`). `entry.data.id` is the ULID (use for API calls, term lookups, comment targeting: `contentId={entry.data.id}`). They are different strings.
- **Taxonomy names must match the seed exactly.** `seed/seed.json` defines taxonomy slugs. `categories` is not `category`. `tags` is not `tag`. No pluralization assumptions.
- **Never use `dark:` prefixes.** Kumo semantic tokens handle dark mode via CSS `light-dark()`. `bg-kumo-surface` automatically switches. `dark:bg-gray-800` bypasses the design system and won't match.
- **Never use raw Tailwind colors** (except `bg-white`, `bg-black`, `text-white`, `text-black`, `transparent`). `bg-blue-500`, `text-gray-600`, `border-red-400` are all wrong. Always use Kumo tokens: `bg-kumo-brand`, `text-kumo-subtle`, `text-kumo-danger`.
- **All pages are server-rendered.** EmDash content is dynamic — pages run on the server. No `getStaticPaths`. Every content query must be wrapped in `Astro.cache.set(cacheHint)`.
- **Buttons in RTL need `aria-label` for icon-only variants.** `<Button shape="square" icon={SearchIcon} aria-label="Search" />` — the label is required for screen readers.

## Output Template

When the designer produces a Design Brief, it should follow this exact structure. The site-builder agent maps these sections to implementation:

```markdown
# Design Brief: [Page/Site Name]

## Overview

[A 2-3 sentence description of the page purpose and overall visual aesthetic. Mention the mood (professional, playful, editorial, minimal), the target audience, and the primary action the user should take.]

## Layout Structure

[Top-to-bottom ordered list of sections. Use ASCII diagrams for complex layouts.]
```

┌──────────────────────────────┐
│ Navigation Bar │ ← sticky, bg-kumo-canvas
├──────────────────────────────┤
│ Hero Section │ ← bg-kumo-brand, centered text
├──────────────────────────────┤
│ Feature Card Grid (3-col) │ ← bg-kumo-canvas
├──────────────────────────────┤
│ Content + Sidebar (2-col) │ ← bg-kumo-elevated
├──────────────────────────────┤
│ CTA Banner │ ← bg-kumo-brand
├──────────────────────────────┤
│ Footer (4-col) │ ← bg-kumo-elevated
└──────────────────────────────┘

```

## Color System
[Map every color to a Kumo semantic token. Be specific about which element uses which token.]

- Page background: `bg-kumo-canvas`
- Card background: `bg-kumo-elevated`
- Hero/CTA background: `bg-kumo-brand`
- Primary text: `text-kumo-default`
- Secondary text (metadata, dates): `text-kumo-subtle`
- Subtle text (captions, placeholders): `text-kumo-subtle`
- Text on brand backgrounds: `text-kumo-inverse`
- Brand accents (links, active states): `text-kumo-brand`
- Borders/Dividers: `border-kumo-line`
- Strong borders: `border-kumo-hairline`

## Typography
[Specify fonts, scale, and weights.]

- Heading font: Inter, sans-serif
- Body font: Inter, sans-serif
- Scale: h1=text-4xl font-bold, h2=text-2xl font-bold, body=text-base, meta=text-sm
- Heading color: text-kumo-default
- Body color: text-kumo-default
- Meta color: text-kumo-subtle

## Component Map
| Visual Element | Kumo/EmDash Component | Key Props | Notes |
|---------------|----------------------|-----------|-------|
| Hero CTA button | Button | variant="primary", size="lg" | Full-width on mobile |
| Hero secondary link | LinkButton | href="/learn", variant="secondary" | Next to primary CTA |
| Feature card | Card | padding="lg", variant="elevated" | Image + heading + excerpt + link |
| Feature card image | Image (from emdash/ui) | image={item.data.featured_image} | Object, not string |
| Feature card link | LinkButton | variant="ghost" | "Read more →" at card bottom |
| Blog post body | PortableText (from emdash/ui) | value={post.data.body} | Renders rich text |
| Sidebar widgets | WidgetArea (from emdash/ui) | name="sidebar" | Widget area from seed |
| Comment section | Comments (from emdash/ui) | contentId={post.data.id} | ULID, not slug |
| Comment form | CommentForm (from emdash/ui) | contentId={post.data.id} | Below comments |
| Loading state | Loader | size="md" | Show while fetching content |
| Empty state | Text + EmDashHead | — | "No posts yet" with SEO tags |

## Spacing & Grid
- Section padding: py-16 on desktop, py-10 on mobile
- Container max-width: max-w-7xl
- Card grid: grid-cols-1 md:grid-cols-2 lg:grid-cols-3
- Card gap: gap-6
- Section gap: gap-12 between major sections

## Responsive Behavior
- sm (< 640px): Single column, hamburger nav, full-width images, stacked CTAs
- md (640-1024px): 2-column grid, horizontal nav (compact), side-by-side CTAs
- lg (> 1024px): 3+ column grid, full nav with links, sidebar appears

## Interactions & States
- Card hover: shadow increase (Card variant="elevated" handles this)
- Button hover: slight darkening (Kumo handles this automatically)
- Link hover: underline or color shift
- Loading: Loader component for async content sections
- Empty: Descriptive text when collections have no items
- Focus: Visible focus rings on all interactive elements (Kumo handles this)

## Accessibility Notes
- All icon-only buttons have aria-label (e.g., `<Button shape="square" icon={SearchIcon} aria-label="Search" />`)
- All form inputs paired with Label component
- Heading hierarchy is logical (h1 → h2 → h3, no skips)
- Color contrast: text-kumo-default on bg-kumo-canvas passes WCAG AA
- Focus order follows visual layout (DOM order matches display order)
- Navigation is keyboard accessible
```

## Validation Loop

1. **Designer produces a Design Brief** from a screenshot
2. **Check every color reference** — is it a Kumo token? No raw Tailwind (except `white`/`black`/`transparent`)? No `dark:` prefix?
3. **Check every component reference** — is it a Kumo component or EmDash UI component? Not a raw HTML element?
4. **Check every layout class** — does it use logical properties (ms-/me-, start-/end-)? No physical classes?
5. **Check the Component Map** — are image fields referenced as objects? Are IDs correctly slug vs ULID?
6. **If any check fails**, the designer must regenerate the brief section with the correct reference
7. **Once all checks pass**, the brief is ready for site-builder handoff

## References

- `references/component-gallery.md` — full Kumo component props reference with visual examples
- `references/color-swatches.md` — Kumo token → color previews
- `references/layout-patterns.md` — expanded layout library with more patterns
- `references/astro-patterns.md` — EmDash content query patterns, caching, image handling
