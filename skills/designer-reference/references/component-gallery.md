# Component Gallery

Full Kumo component reference from the live docs at [kumo-ui.com](https://kumo-ui.com) and the source code at [github.com/cloudflare/kumo](https://github.com/cloudflare/kumo).

All components are imported from `"@cloudflare/kumo"` and require the Kumo stylesheet: `import "@cloudflare/kumo/styles"`.

## Color Token Mapping

Source: `packages/kumo/src/styles/theme-kumo.css` (auto-generated, edit `scripts/theme-generator/config.ts`).

### Surface Colors

| Tailwind Class     | CSS Variable            | Light Mode                     | Dark Mode                     | Use for                  |
| ------------------ | ----------------------- | ------------------------------ | ----------------------------- | ------------------------ |
| `bg-kumo-canvas`   | `--color-kumo-canvas`   | `oklch(98.75% 0 0)` near-white | `oklch(10% 0 0)` near-black   | Page background          |
| `bg-kumo-elevated` | `--color-kumo-elevated` | `oklch(98% 0 0)`               | `oklch(12% 0 0)`              | Cards, elevated surfaces |
| `bg-kumo-recessed` | `--color-kumo-recessed` | `oklch(96% 0 0)`               | `oklch(15% 0 0)`              | Contextual backgrounds   |
| `bg-kumo-base`     | `--color-kumo-base`     | `#fff` white                   | `oklch(17% 0 0)` dark gray    | Component backgrounds    |
| `bg-kumo-overlay`  | `--color-kumo-overlay`  | `oklch(97.5% 0 0)`             | `oklch(26.9% 0 0)`            | Dialog/modals backdrops  |
| `bg-kumo-contrast` | `--color-kumo-contrast` | `oklch(8.5% 0 0)` near-black   | `oklch(98.5% 0 0)` near-white | High contrast areas      |
| `bg-kumo-tint`     | `--color-kumo-tint`     | `oklch(97% 0 0)`               | `oklch(26.9% 0 0)`            | Subtle background tint   |
| `bg-kumo-control`  | `--color-kumo-control`  | `#fff` white                   | `oklch(21% 0.006 285.885)`    | Form control backgrounds |

### Text Colors

| Tailwind Class          | CSS Variable                    | Light Mode                    | Dark Mode                       | Use for                      |
| ----------------------- | ------------------------------- | ----------------------------- | ------------------------------- | ---------------------------- |
| `text-kumo-default`     | `--text-color-kumo-default`     | `oklch(21% 0.006)` near-black | `oklch(97% 0 0)` near-white     | Body text, headings          |
| `text-kumo-strong`      | `--text-color-kumo-strong`      | `oklch(43.9% 0 0)` dark gray  | `oklch(70.8% 0 0)` light gray   | Emphasized text              |
| `text-kumo-subtle`      | `--text-color-kumo-subtle`      | `oklch(55.6% 0 0)` gray       | `oklch(70.8% 0 0)`              | Secondary text, metadata     |
| `text-kumo-inactive`    | `--text-color-kumo-inactive`    | `oklch(70.8% 0 0)` light gray | `oklch(70.8% 0 0)`              | Disabled text                |
| `text-kumo-placeholder` | `--text-color-kumo-placeholder` | `oklch(70.8% 0 0)`            | `oklch(55.6% 0 0)`              | Input placeholders           |
| `text-kumo-inverse`     | `--text-color-kumo-inverse`     | `oklch(97% 0 0)` near-white   | `oklch(20.5% 0 0)` near-black   | Text on inverted backgrounds |
| `text-kumo-brand`       | `--text-color-kumo-brand`       | `#f6821f` orange              | `#f6821f`                       | Brand-colored text           |
| `text-kumo-link`        | `--text-color-kumo-link`        | `oklch(42.4% 0.199)` blue     | `oklch(70.7% 0.165)` light blue | Links                        |

### Brand & Interactive

| Tailwind Class        | CSS Variable               | Use for                                |
| --------------------- | -------------------------- | -------------------------------------- |
| `bg-kumo-brand`       | `--color-kumo-brand`       | Brand-colored backgrounds (oklch blue) |
| `bg-kumo-brand-hover` | `--color-kumo-brand-hover` | Brand hover state                      |
| `bg-kumo-interact`    | `--color-kumo-interact`    | Interactive elements (hover)           |
| `bg-kumo-fill`        | `--color-kumo-fill`        | Filled backgrounds (rows, items)       |
| `bg-kumo-fill-hover`  | `--color-kumo-fill-hover`  | Filled hover state                     |

### Borders & Shadows

| Tailwind Class         | CSS Variable               | Use for                       |
| ---------------------- | -------------------------- | ----------------------------- |
| `border-kumo-line`     | `--color-kumo-line`        | Divider lines, borders        |
| `border-kumo-hairline` | `--color-kumo-hairline`    | Subtle borders, ring outlines |
| `ring-kumo-focus`      | `--color-kumo-focus`       | Focus rings                   |
| `shadow-kumo-edge`     | `--color-kumo-shadow-edge` | Shadow edge color             |
| `shadow-kumo-drop`     | `--color-kumo-shadow-drop` | Shadow drop color             |

### Status Colors (Background)

| Tailwind Class                            | Use for               |
| ----------------------------------------- | --------------------- |
| `bg-kumo-info-tint`, `bg-kumo-info`       | Info messages         |
| `bg-kumo-success-tint`, `bg-kumo-success` | Success messages      |
| `bg-kumo-warning-tint`, `bg-kumo-warning` | Warning messages      |
| `bg-kumo-danger-tint`, `bg-kumo-danger`   | Error/danger messages |

### Status Colors (Text)

| Tailwind Class      | Use for           |
| ------------------- | ----------------- |
| `text-kumo-info`    | Info text         |
| `text-kumo-success` | Success text      |
| `text-kumo-warning` | Warning text      |
| `text-kumo-danger`  | Error/danger text |

### Badge Colors (Background)

| Tailwind Class                | Color               |
| ----------------------------- | ------------------- |
| `bg-kumo-badge-red`           | Red badge           |
| `bg-kumo-badge-orange`        | Orange badge        |
| `bg-kumo-badge-orange-subtle` | Subtle orange badge |
| `bg-kumo-badge-purple`        | Purple badge        |
| `bg-kumo-badge-green`         | Green badge         |
| `bg-kumo-badge-teal`          | Teal badge          |
| `bg-kumo-badge-teal-subtle`   | Subtle teal badge   |
| `bg-kumo-badge-blue`          | Blue badge          |
| `bg-kumo-badge-neutral`       | Neutral badge       |
| `bg-kumo-badge-inverted`      | Inverted badge      |

### Badge Colors (Text)

| Tailwind Class                   | Use for                       |
| -------------------------------- | ----------------------------- |
| `text-kumo-badge-orange-subtle`  | Text on subtle orange badges  |
| `text-kumo-badge-teal-subtle`    | Text on subtle teal badges    |
| `text-kumo-badge-neutral-subtle` | Text on subtle neutral badges |
| `text-kumo-badge-inverted`       | Text on inverted badges       |

## Typography Scale

Source: `packages/kumo/src/styles/theme-kumo.css` (auto-generated).

| Class       | Size | Line Height | Use for                    |
| ----------- | ---- | ----------- | -------------------------- |
| `text-xs`   | 12px | 1.333       | Captions, fine print       |
| `text-sm`   | 13px | 1.176       | Metadata, labels           |
| `text-base` | 14px | 1.429       | Body text (default)        |
| `text-lg`   | 16px | 1.25        | Large body, small headings |

Note: Kumo defines only 4 text sizes (`xs` through `lg`). For larger headings (h1, h2, h3), use Tailwind's default scale (`text-2xl`, `text-3xl`, `text-4xl`, `text-5xl`) combined with Kumo text color tokens.

### Typography Pairing with Color Tokens

```
h1, h2, h3, h4 → text-kumo-default text-3xl font-bold
body, p, li    → text-kumo-default text-base
.meta, time    → text-kumo-subtle text-sm
.caption       → text-kumo-subtle text-xs
.inactive      → text-kumo-inactive text-sm
```

## Component Inventory (from kumo-ui.com)

42 components listed at [kumo-ui.com](https://kumo-ui.com):

| Component         | Type       | Common Props                                                         |
| ----------------- | ---------- | -------------------------------------------------------------------- |
| Autocomplete      | Input      | items, onSelect, placeholder                                         |
| Badge             | Display    | children, variant                                                    |
| Banner            | Feedback   | variant (info/success/warning/danger), title, description, onDismiss |
| Breadcrumbs       | Navigation | items: { label, href }[]                                             |
| Button            | Action     | variant, size, icon, loading, shape, disabled                        |
| Checkbox          | Input      | label, checked, onChange                                             |
| Clipboard Text    | Utility    | text, onCopy                                                         |
| CodeHighlighted   | Display    | code, language                                                       |
| Collapsible       | Layout     | open, title, children                                                |
| Combobox          | Input      | options, value, onChange                                             |
| Command Palette   | Overlay    | commands, open, onClose                                              |
| Date Picker       | Input      | value, onChange, min, max                                            |
| Dialog            | Overlay    | open, onClose, title, children                                       |
| Dropdown          | Overlay    | trigger, items                                                       |
| Empty             | Feedback   | title, description, action                                           |
| Flow              | Layout     | children (flex layout)                                               |
| Grid              | Layout     | children, cols, gap                                                  |
| Input             | Input      | type, placeholder, value, onChange, error                            |
| InputArea         | Input      | rows, placeholder, value, onChange                                   |
| InputGroup        | Input      | children (groups inputs with labels)                                 |
| Label             | Form       | htmlFor, children                                                    |
| Layer Card        | Layout     | children, padding                                                    |
| Link              | Navigation | href, external                                                       |
| Loader            | Feedback   | size (sm/md/lg)                                                      |
| MenuBar           | Navigation | items                                                                |
| Meter             | Display    | value, max, label                                                    |
| Pagination        | Navigation | page, total, onChange                                                |
| Popover           | Overlay    | trigger, children, open                                              |
| Radio             | Input      | label, value, checked, onChange                                      |
| Select            | Input      | options, value, onChange, placeholder                                |
| Sensitive Input   | Input      | value, onChange (redacted display)                                   |
| Sidebar           | Layout     | children, open, onClose                                              |
| Skeleton Line     | Feedback   | width, height                                                        |
| Switch            | Input      | label, checked, onChange                                             |
| Table             | Display    | columns, data, sortable                                              |
| Table of Contents | Navigation | headings, activeId                                                   |
| Tabs              | Navigation | items, activeTab, onChange                                           |
| Text              | Display    | children, variant, size                                              |
| Toast             | Feedback   | title, description, variant, onDismiss                               |
| Tooltip           | Overlay    | content, children                                                    |

### Blocks

| Block           | Use for                       |
| --------------- | ----------------------------- |
| Page Header     | Page title + actions bar      |
| Resource List   | List views with actions       |
| Delete Resource | Destructive confirmation flow |
