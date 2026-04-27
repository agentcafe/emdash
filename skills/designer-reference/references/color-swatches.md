# Color Swatches

Visual reference for Kumo semantic color tokens. Each token maps to a CSS custom property with `light-dark()` for automatic dark mode.

## Surface Hierarchy

```
Page Background:    bg-kumo-canvas     (light: near-white oklch(98.75%) / dark: near-black oklch(10%))
Cards & Elevated:   bg-kumo-elevated   (light: oklch(98%) / dark: oklch(12%))
Recessed Areas:     bg-kumo-recessed   (light: oklch(96%) / dark: oklch(15%))
Component Base:     bg-kumo-base       (light: #fff / dark: oklch(17%))
Overlay/Backdrop:   bg-kumo-overlay    (light: oklch(97.5%) / dark: oklch(26.9%))
```

## Text Hierarchy (light mode)

```
Primary:   text-kumo-default   → near-black oklch(21%)
Strong:    text-kumo-strong    → dark gray oklch(43.9%)
Subtle:    text-kumo-subtle    → gray oklch(55.6%)
Inactive:  text-kumo-inactive  → light gray oklch(70.8%)
Placeholder: text-kumo-placeholder → light gray oklch(70.8%)
Inverse:   text-kumo-inverse   → near-white oklch(97%)
```

## Text Hierarchy (dark mode)

```
Primary:   text-kumo-default   → near-white oklch(97%)
Strong:    text-kumo-strong    → light gray oklch(70.8%)
Subtle:    text-kumo-subtle    → light gray oklch(70.8%)
Inactive:  text-kumo-inactive  → medium gray oklch(70.8%)
Placeholder: text-kumo-placeholder → medium gray oklch(55.6%)
Inverse:   text-kumo-inverse   → near-black oklch(20.5%)
```

## Brand Colors

```
Brand bg:     bg-kumo-brand       → oklch(0.5772 0.2324 260) [blue]
Brand hover:  bg-kumo-brand-hover → oklch(48.8% 0.243 264.376) [darker blue]
Brand text:   text-kumo-brand     → #f6821f [orange]
```

## Status Colors

```
Success text:  text-kumo-success  → light: emerald-800 / dark: emerald-200
Warning text:  text-kumo-warning  → light: yellow-800 / dark: yellow-400
Danger text:   text-kumo-danger   → light: red-700 / dark: red-400
Info text:     text-kumo-info     → light: blue-800 / dark: blue-400
Link text:     text-kumo-link     → light: blue-800 / dark: blue-400

Success bg (tint): bg-kumo-success-tint → light: emerald-100 / dark: emerald-900
Success bg:        bg-kumo-success      → light: green-300 / dark: green-900
Warning bg (tint): bg-kumo-warning-tint → light: yellow-100 / dark: yellow-700
Warning bg:        bg-kumo-warning      → light: yellow-300 / dark: yellow-900
Danger bg (tint):  bg-kumo-danger-tint  → light: red-100 / dark: red-900
Danger bg:         bg-kumo-danger       → light: red-500 / dark: red-900
Info bg (tint):    bg-kumo-info-tint    → light: blue-100 / dark: blue-900
Info bg:           bg-kumo-info         → light: blue-300 / dark: blue-900
```

## Border Colors

```
Line:     border-kumo-line     → light: oklch(14.5% 0 0 / 0.1) [translucent black] / dark: oklch(32% 0 0)
Hairline: border-kumo-hairline → light: oklch(93.5% 0 0) / dark: oklch(26.9% 0 0)
```

## Common Combinations

```
// Card pattern
<div className="bg-kumo-elevated border border-kumo-line rounded-lg p-6">
  <h3 className="text-kumo-default text-xl font-semibold">Title</h3>
  <p className="text-kumo-subtle text-sm">Metadata</p>
  <p className="text-kumo-default mt-2">Body text goes here.</p>
</div>

// Primary button
<Button className="bg-kumo-brand text-white hover:bg-kumo-brand-hover">
  Click me
</Button>

// Destructive action
<Button className="bg-kumo-danger text-white">
  Delete
</Button>

// Success message
<div className="bg-kumo-success-tint border border-kumo-line rounded p-3">
  <p className="text-kumo-success text-sm">Operation successful</p>
</div>

// Warning message
<div className="bg-kumo-warning-tint border border-kumo-line rounded p-3">
  <p className="text-kumo-warning text-sm">Proceed with caution</p>
</div>

// Error message
<div className="bg-kumo-danger-tint border border-kumo-line rounded p-3">
  <p className="text-kumo-danger text-sm">Something went wrong</p>
</div>
```

## Explicit Allowed Raw Colors

Per Kumo's AGENTS.md, these are the ONLY raw colors allowed:

```
bg-white, bg-black, text-white, text-black, transparent
```

Everything else MUST use Kumo semantic tokens. Never use:

- `bg-blue-500`, `bg-gray-100`, `bg-red-600`
- `text-gray-600`, `text-blue-700`
- `dark:bg-gray-800`, `dark:text-gray-200`
