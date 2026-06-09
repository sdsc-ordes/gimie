# SDSC design system


The system is derived from the SDSC UI Kit (Figma Make file
`xFRPysbb2ni4RXyuT7dVqq`, UI Kit v2.1), which is itself based on
[datascience.ch](https://datascience.ch). The kit ships in light mode; this
document adds the corresponding dark theme so that a single token set drives both
appearances.

- **Tech stack:** React or SvelteKit with Tailwind CSS v4.
- **Fonts:** Space Grotesk (headings), Switzer (body and UI), and JetBrains Mono
  (code and IDs).
- **Status:** active. Update this file when the Figma kit changes.

## How to use this document

Read this document before you create or change any UI surface. It is the design
language; the rest of the codebase implements it.

1. Reach for an existing token before you introduce a new value. Tokens live in
   your stylesheet (for example, `app.css`) as CSS custom properties.
2. If you need a value that doesn't exist yet, add it to the relevant section of
   this document first, then add it to the stylesheet, and only then use it in
   code. Don't invent ad hoc colors, radii, or spacing in component markup.
3. Define each token for both modes. Never hard-code a hex value that only works
   in one theme.

**Note:** Throughout this document, "light" values are the canonical SDSC kit
values from datascience.ch. "Dark" values are the ink-blue-on-near-black
adaptation. Both are first-class; pick per the active mode, not per preference.

## Design principles

The SDSC look is **Swiss, structured, and sharp-edged**:

- **Minimal and academic.** No glow, no neon, no decorative gradients beyond the
  one approved brand gradient.
- **Two blues carry the brand.** Dark blue (`#26245c`) and light blue (`#5461a6`)
  are the only chrome colors. Status colors appear only on badges, alerts, and
  toasts.
- **Sharp corners.** Cards, panels, and banners have square corners. Only buttons
  and small controls carry a subtle 4px radius; only avatars and floating buttons
  are fully round.
- **The `〇 LABEL` pattern.** Every titled section opens with a circle-prefixed,
  uppercase label. This is the kit's signature.

Apply these principles consistently:

- **Consistency.** Use the defined palette and type scale everywhere. Apply the
  8px spacing unit uniformly.
- **Clarity.** Prioritize readability with generous line spacing and white space.
  Keep a clear hierarchy of size and weight.
- **Accessibility.** Meet WCAG AA contrast (4.5:1 for body text) in both modes.
  Support keyboard navigation, provide visible focus states, and never use color
  as the only way to convey meaning.
- **Responsiveness.** Design mobile-first. Use the breakpoints 640px (`sm`), 768px
  (`md`), 1024px (`lg`), and 1280px (`xl`). Keep tap targets at least 44×44px.

## Theming and modes

The system uses a single set of named tokens. Light mode is the default, defined
on `:root`. Dark mode overrides the same tokens under a `.dark` class on a
root element (typically `<html>` or `<body>`).

```css
:root {
  /* light-mode token values (default) */
}

.dark {
  /* dark-mode token values override the same names */
}
```

To switch modes, toggle the `.dark` class on the root element. Because components
reference token names rather than raw hex values, they adapt automatically.

When you write a component:

- Reference tokens by name (`var(--op-surface)`, `bg-op-surface`,
  `text-op-text`). Don't reference a mode-specific hex value.
- Test every visible change in both modes before you consider it done.

**Note:** Drawing code that can't read CSS variables — for example, D3 or raw
SVG — must read the resolved token value at runtime or branch on the active mode.
It's the one place a literal hex is acceptable, and even then, source it from a
single shared constant.

## Color

All colors are exposed as CSS custom properties (`--op-*`) and, where you use
Tailwind, as theme colors that generate `bg-op-*`, `text-op-*`, and `border-op-*`
utilities.

### Brand colors

The two SDSC blues are the same in both modes. Only the hover step changes,
because a darker hover reads well on light surfaces but a lighter hover reads
better on dark ones.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--op-blue-darker` | `#161438` | `#161438` | Pressed state for dark-blue banners and footer accents. |
| `--op-blue-dark` | `#26245c` | `#26245c` | **Primary brand.** Loud banners, key-numbers band, hero overlay. |
| `--op-blue-mid` | `#3a4585` | `#3a4585` | Hover step on dark surfaces (dark mode only). |
| `--op-blue` | `#5461a6` | `#5461a6` | **Interactive blue.** Primary buttons, icon fills, focus ring. |
| `--op-blue-light` | `#8a94c9` | `#8a94c9` | Lighter accents; link and hover text on dark. |
| `--op-blue-pale` | `#dddeec` | `#1a1834` | Soft banner background. Pale blue on light, deep blue on dark. |

Full brand scales (source of truth — don't invent intermediate steps):

| Scale | Lighter | Light | Base | Dark | Darker |
|---|---|---|---|---|---|
| Dark Blue | `#4a4889` | `#383673` | `#26245c` | `#1e1c4a` | `#161438` |
| Light Blue | `#8a94c9` | `#6f7ab8` | `#5461a6` | `#434e85` | `#323b64` |

#### Secondary accent (green)

The kit defines a secondary green, `#90ca42`, for highlights and progress
completion. It is **not** a chrome color: don't use it for primary actions,
navigation, or backgrounds. Reserve it for the complete (100%) state of progress
indicators and occasional accent highlights.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--op-green` | `#90ca42` | `#a4d564` | Secondary accent. Progress-complete (100%) state and occasional highlights. Dark mode steps to the Light scale value so it reads on near-black. |

Full green scale (source of truth — don't invent intermediate steps):

| Scale | Lighter | Light | Base | Dark | Darker |
|---|---|---|---|---|---|
| Green | `#b8e186` | `#a4d564` | `#90ca42` | `#73a235` | `#567928` |

### Surface and background colors

| Token | Light | Dark | Role |
|---|---|---|---|
| `--op-bg` | `#fafafa` | `#0c0c12` | Page background. The base of every page. |
| `--op-surface` | `#ffffff` | `#141420` | Default card or panel. |
| `--op-surface-2` | `#f5f5f5` | `#1c1c2c` | Elevated surface: table heads, second-level cards, hover targets. |
| `--op-surface-active` | `#e9ebef` | `#1a1834` | Selected or active row; current sidebar item. |
| `--op-border` | `#e5e5e5` | `#242438` | Default border for cards, dividers, table cells. |
| `--op-border-subtle` | `#f0f0f2` | `#1a1a28` | Dim or inset border under headings and badges. |

### Text colors

| Token | Light | Dark | Role |
|---|---|---|---|
| `--op-text` | `#000000` | `#f4f4fc` | Primary text. Headings and body. |
| `--op-text-2` | `#525252` | `#c0c0dc` | Secondary text. Long-form paragraphs, table cells. |
| `--op-text-muted` | `#848484` | `#9898b8` | Captions, labels, `〇 LABEL` text, table heads. |
| `--op-text-faint` | `#a3a3a3` | `#6a6a88` | Fine print, timestamps, disabled labels. |
| `--op-text-on-blue` | `#ffffff` | `#ffffff` | Text on `--op-blue` or `--op-blue-dark` surfaces. |

### Links

| Token | Light | Dark | Role |
|---|---|---|---|
| `--op-link` | `#5461a6` | `#8a94c9` | Default hyperlink color. |
| `--op-link-hover` | `#26245c` | `#5461a6` | Hover and focus color for links. |

Append a trailing arrow (`→`) to navigational and call-to-action links inside body
text. This is the SDSC convention.

### Semantic and status colors

Status colors appear only on badges, alerts, toasts, and progress states — never
as chrome. Light mode uses the kit's base values; dark mode steps each color
lighter so it reads against near-black.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--op-success` | `#10b981` | `#4ade80` | Success badges and confirmations. |
| `--op-warning` | `#f59e0b` | `#fbbf24` | Warning and degraded states. |
| `--op-error` | `#ef4444` | `#f87171` | Error badges, destructive actions. |
| `--op-info` | `#3b82f6` | `#5461a6` | Informational messages. Dark mode aliases the brand blue. |

Full semantic scales (for badge backgrounds and per-mode tuning):

| Scale | Lighter | Light | Base | Dark | Darker |
|---|---|---|---|---|---|
| Success | `#6ee7b7` | `#34d399` | `#10b981` | `#059669` | `#047857` |
| Warning | `#fcd34d` | `#fbbf24` | `#f59e0b` | `#d97706` | `#b45309` |
| Error | `#fca5a5` | `#f87171` | `#ef4444` | `#dc2626` | `#b91c1c` |
| Info | `#93c5fd` | `#60a5fa` | `#3b82f6` | `#2563eb` | `#1d4ed8` |

Render a badge with the status color on a low-alpha fill of the same color:

```css
color: var(--op-success);
background: color-mix(in srgb, var(--op-success) 12%, transparent);
```

### Neutral grayscale reference

The kit defines a 10-step neutral scale. Use it to derive new surface or border
values when the named tokens above don't cover a case.

| Step | Hex | Typical use |
|---|---|---|
| 50 | `#fafafa` | Light page background |
| 100 | `#f5f5f5` | Subtle section tint |
| 200 | `#e5e5e5` | Card border, divider |
| 300 | `#d4d4d4` | Medium border, disabled |
| 400 | `#a3a3a3` | Placeholder text |
| 500 | `#737373` | Secondary text |
| 600 | `#525252` | Strong border, captions |
| 700 | `#404040` | Overlay background |
| 800 | `#262626` | Dark section background |
| 900 | `#171717` | Near-black text |

### Footer colors

The footer is true black in both modes for partner-logo contrast.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--op-footer-bg` | `#000000` | `#000000` | Footer surface. |
| `--op-footer-border` | `rgba(255,255,255,0.10)` | `rgba(255,255,255,0.10)` | Dividers within the footer. |

### Add a new color

1. Add `--op-<name>` to both the `:root` and `.dark` blocks in your stylesheet,
   each with the correct per-mode value.
2. If you use Tailwind, add `--color-op-<name>` to the `@theme` block.
3. Document it in the relevant table above, with both light and dark values.
4. Don't write a raw hex in component markup. Drawing code (D3, SVG) is the only
   exception.

## Typography

### Fonts

| Family | Where to use it | Weight |
|---|---|---|
| **Space Grotesk** | All headings (`h1`–`h6`), display numbers, wordmarks. | 600–700 |
| **Switzer** | Body, paragraphs, buttons, inputs, navigation, labels — all UI chrome. | 400–600 |
| **JetBrains Mono** | Code, IDs, commit SHAs, query snippets — anything monospaced. | 400–500 |

Set `'Switzer', system-ui, sans-serif` on `body` and
`'Space Grotesk', system-ui, sans-serif` on `h1`–`h6`. Apply a `.mono` utility for
monospaced content. D3 and SVG text elements need an explicit `font-family`
attribute, because they don't inherit it from CSS.

### Type scale

| Role | Size | Weight |
|---|---|---|
| H1 — display | 48px | Bold (700) |
| H2 — section | 32px | Bold (700) |
| H3 — subsection | 24px | Semibold (600) |
| H4 — component title | 18px | Semibold (600) |
| Body large (lead) | 18px | Regular (400) |
| Body | 16px | Regular (400) |
| Body small | 14px | Regular (400) |
| Button | 14px | Regular (400), uppercase, wide tracking |
| Caption | 12px | Regular (400) |

Use a line height of 1.5–1.6 for body text and 1.2–1.3 for headings. Apply
letter spacing of −0.02em on large headings (H1 and H2). Keep line length to
65–75 characters for readability.

**Note:** In dark mode, prefer Regular (400) for body text. Weights below 400
hairline out against near-black. Headings stay Bold or Semibold in both modes.

## Spacing, layout, and shape

### Border radius

| Use | Radius |
|---|---|
| Cards, panels, tables, banners, hero sections, sidebar nav links | `0` (square) |
| Buttons, status badges, icon buttons, inputs, checkboxes, progress bars | `4px` |
| Avatars and floating icon buttons | fully round |

**Caution:** Don't use medium or large radii (`8px`+) on chrome. If you find one in
existing code, it's legacy — replace it with a square corner or the 4px control
radius.

### Padding and gap

The base spacing unit is 8px. Common applications:

| Use | Value |
|---|---|
| Card or panel padding | 24px (small), 32px (standard), 48px (hero) |
| Button padding | 16px × 8px (small), 24px × 12px (medium), 32px × 16px (large) |
| Vertical section gap | 48px–64px |
| Inside a content block | 12px–16px |
| Label to title | 12px |
| Title to body | 16px |

### Page width

| Surface | Max width |
|---|---|
| Page | 1280px, centered |
| Content or article column | 768px–896px |
| Page horizontal padding | 24px |

## Content label pattern

This three-line block is the kit's signature. Every titled section uses it.

```
〇 LABEL          ← muted text, 14px Switzer Medium, uppercase, wide tracking
Section title     ← primary text, Space Grotesk Bold
Body text…        ← secondary text, 16px Switzer Regular
```

Reference markup:

```html
<div class="space-y-3">
  <div class="flex items-center gap-2">
    <span style="color: var(--op-text-muted)">〇</span>
    <p class="text-sm font-medium uppercase tracking-wide"
       style="color: var(--op-text-muted)">
      LABEL
    </p>
  </div>
  <h2 style="color: var(--op-text)">Section title</h2>
  <p class="leading-relaxed" style="color: var(--op-text-2)">Body content…</p>
</div>
```

Use 12px from label to title and 16px from title to body.

## Components

Each component below references tokens, so it adapts to the active mode without
change. Patterns use Tailwind utilities and inline `var(--op-*)` references; adapt
the syntax to your framework.

### Buttons

All buttons share these traits: uppercase text, Switzer Regular, a 4px radius,
a minimum 44px touch target, and a 2px `--op-blue` focus ring.

| Variant | When to use it | Pattern |
|---|---|---|
| **Primary** | The single most important action on a screen. | Blue fill, white text; hover to `--op-blue-mid`, active to `--op-blue-dark`. |
| **Secondary** | A supporting action beside a primary. | Transparent fill, blue border and text; hover fills the elevated surface. |
| **Outline** | A subtle or tertiary action. | Transparent fill, border in `--op-border`, text in `--op-text`; hover to blue. |
| **Text** | A minimal, in-flow action. | Link-colored text, no border; hover fills the elevated surface. |
| **Icon (round)** | A floating action button only. | Fully round, blue fill, white icon. |

Reference primary button:

```html
<button
  class="rounded px-6 py-3 text-sm font-normal uppercase tracking-wide
         transition-all focus-visible:outline-2"
  style="background: var(--op-blue); color: var(--op-text-on-blue);
         outline-color: var(--op-blue)">
  Action
</button>
```

Hover to `--op-blue-mid`, active to `--op-blue-dark`. For the disabled state, use
the elevated surface with faint text and `cursor: not-allowed`. Give text buttons
a minimum width of 120px.

**Caution:** Don't dim buttons with `opacity: 0.5` in dark mode — it makes them
look smudged. Use the disabled surface and text tokens instead. Don't use Title
Case or lowercase button labels; button text is always uppercase.

### Links

```html
<a href="…" class="inline-flex items-center gap-1 transition-colors"
   style="color: var(--op-link)">
  Learn more <span aria-hidden="true">→</span>
</a>
```

Hover and focus shift the color to `--op-link-hover`.

### Status badges

Badges use a semantic color on a low-alpha fill of the same color, with square or
4px corners — never fully rounded pills.

```html
<span class="rounded px-2.5 py-0.5 text-sm font-medium uppercase tracking-wide"
      style="color: var(--op-success);
             background: color-mix(in srgb, var(--op-success) 12%, transparent)">
  succeeded
</span>
```

| State | Foreground token |
|---|---|
| succeeded | `--op-success` |
| running | `--op-blue-light` |
| failed | `--op-error` |
| pending | `--op-text-muted` |
| warning | `--op-warning` |

### Cards

```html
<div class="border p-8"
     style="background: var(--op-surface); border-color: var(--op-border)">
  …
</div>
```

Card hierarchy:

- **Default card.** `--op-surface` background, `--op-border` border, square
  corners, 24px–32px padding.
- **Elevated card.** `--op-surface-2` background, for table heads or a card that
  sits above another card.
- **Soft banner.** `--op-blue-pale` background, no border, 32px–48px padding. Pale
  blue in light mode, deep blue in dark mode.
- **Loud banner or hero.** `--op-blue-dark` background, white text, 32px–48px
  padding.

### Form inputs

```html
<input
  class="w-full rounded border px-4 py-3"
  style="background: var(--op-surface); border-color: var(--op-border);
         color: var(--op-text)" />
```

Inputs carry a 4px radius. Use placeholder text in `--op-text-muted`, consistent
padding (8px vertical, 16px horizontal), and a `--op-blue` border on focus. Place
labels above inputs in Switzer Medium, 14px, with an 8px gap.

### Checkboxes and toggles

- **Checkbox.** 20px square, 4px radius, 2px border. Unchecked: surface fill with a
  border. Checked: `--op-blue` fill and border with a white checkmark. Focus adds
  a 2px blue ring.
- **Toggle switch.** 48px × 24px track with a fully round 16px thumb. Off: border
  color track, thumb left. On: `--op-blue` track, thumb right. Animate the thumb
  with a 200ms transition.

### Progress indicators

- **Progress bar.** Full-width, 8px tall, 4px radius. The track uses the border
  color; the fill uses `--op-blue`. Use `--op-green` (the secondary accent) for the
  complete (100%) state. Animate width changes over 300ms.
- **Spinner.** A 32px circle with a 4px border; the top border uses `--op-blue`.
  Sizes are 24px (small), 32px (default), and 48px (large).

### Tables

```html
<div class="overflow-hidden border" style="border-color: var(--op-border)">
  <table class="w-full">
    <thead style="background: var(--op-surface-2)">
      <tr>
        <th class="px-4 py-3 text-left text-sm font-semibold uppercase tracking-wide"
            style="color: var(--op-text-muted)">Column</th>
      </tr>
    </thead>
    <tbody style="background: var(--op-surface)">
      <tr class="border-t" style="border-color: var(--op-border)">
        <td class="px-4 py-3" style="color: var(--op-text-2)">…</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Icon box

For feature grids, use a square icon container with a translucent blue fill and a
light-blue icon.

```html
<div class="flex h-12 w-12 items-center justify-center"
     style="background: color-mix(in srgb, var(--op-blue) 15%, transparent)">
  <YourIcon style="color: var(--op-blue-light)" />
</div>
```

Use 40px for compact layouts and 48px as standard.

## Page layouts

The kit defines ten page templates. Build them from the components above.

1. **App header.** Sticky, surface background, bottom border. Show the SDSC logo
   on the left and navigation links on the right. Use the color logo on the light
   header and the white logo on the dark header.
2. **Footer.** True-black background with all four partner logos, a links section,
   and a copyright row. See [Logos](#logos).
3. **Hero (split).** A two-column grid: a patterned blue panel beside a content
   panel that uses the content label pattern and a primary button.
4. **Feature grid.** Two, three, or four columns of cards, each with an icon box, a
   title, and one or two lines of body. Place on the page background or on a soft
   banner band for emphasis.
5. **Full-width banner.** Soft variant (`--op-blue-pale`) for low-emphasis CTAs;
   loud variant (`--op-blue-dark`, white text) for high-emphasis CTAs.
6. **Key numbers.** A deep-blue band with large stats: 48px Space Grotesk Bold
   numbers above body-size labels.
7. **List layout.** Use the `〇` prefix for primary lists and a check icon for
   confirmation lists. Don't use disc bullets.
8. **Content + sidebar.** An asymmetric layout (for example, a 280px sidebar beside
   the main column). Style the sidebar with the surface background and a right
   border. Mark the active nav item with link-colored text and a 2px left border in
   `--op-blue`.
9. **Event index.** A card grid where each card has a date chip, a title, a meta
   line, and a CTA link. The date chip uses a blue fill with white text.
10. **Article grid.** A grid of cards, each with a top gradient strip
    (`linear-gradient(135deg, #5461a6, #26245c)`), a category label, a date, a
    title, a summary, and a read-more link.

## Logos

### Primary logo

Use the official logo files. Use the color logo on light backgrounds and the white
logo on dark backgrounds. Maintain the aspect ratio, keep clear space around the
logo equal to its height, and use a minimum height of 32px for digital.

Don't stretch, recolor, or add effects to the logo, and don't place it on busy
backgrounds.

### Partner logos

Always display all four partner logos in the footer, alongside the SDSC logo: ETH
Zürich, EPFL, PSI, and Biopôle Lausanne.

- Maintain a consistent height across partner logos and a 48px gap between them.
- On light backgrounds, use the original colored versions.
- On dark backgrounds, apply the CSS filter `brightness(0) invert(1)` so all logos
  render white.
- Add an opacity transition on hover (70% → 100%).

## Backgrounds and patterns

- **Page background.** Flat `--op-bg`.
- **Dot pattern.** Use the kit's dot-pattern SVGs for hero sections and featured
  content only. Anchor the background at `left center` or `right center`, never
  `center` — the asymmetric placement is intentional. Layer it over
  `--op-blue-dark` with `background-blend-mode: overlay` so it stays dim.
- **Content over a pattern.** Place content on a semi-transparent surface card with
  a backdrop blur to maintain contrast. Verify WCAG AA contrast (4.5:1) over the
  pattern.
- **Gradients.** Use only `linear-gradient(135deg, #5461a6, #26245c)`, for hero
  surrogates and article-card tops. Don't use multi-color gradients anywhere.

## Accessibility

- Meet WCAG AA contrast in both modes: 4.5:1 for body text, 3:1 for large text and
  UI components. In dark mode, prefer `--op-text` or `--op-text-2` for body; avoid
  `--op-text-faint` on `--op-surface`.
- Give every interactive element a visible focus state — a 2px `--op-blue` outline.
- Support full keyboard navigation.
- Don't rely on color alone to convey state. Pair status colors with text, icons,
  or both.
- Keep tap targets at least 44×44px.

## Implementation reference

Define both modes in one stylesheet. Light mode is the default on `:root`; dark
mode overrides the same names under `.dark`.

```css
:root {
  /* Surfaces */
  --op-bg: #fafafa;
  --op-surface: #ffffff;
  --op-surface-2: #f5f5f5;
  --op-surface-active: #e9ebef;
  --op-border: #e5e5e5;
  --op-border-subtle: #f0f0f2;

  /* Brand */
  --op-blue-darker: #161438;
  --op-blue-dark: #26245c;
  --op-blue-mid: #3a4585;
  --op-blue: #5461a6;
  --op-blue-light: #8a94c9;
  --op-blue-pale: #dddeec;

  /* Secondary accent */
  --op-green: #90ca42;

  /* Text */
  --op-text: #000000;
  --op-text-2: #525252;
  --op-text-muted: #848484;
  --op-text-faint: #a3a3a3;
  --op-text-on-blue: #ffffff;

  /* Links */
  --op-link: #5461a6;
  --op-link-hover: #26245c;

  /* Status */
  --op-success: #10b981;
  --op-warning: #f59e0b;
  --op-error: #ef4444;
  --op-info: #3b82f6;

  /* Footer */
  --op-footer-bg: #000000;
  --op-footer-border: rgba(255, 255, 255, 0.1);
}

.dark {
  /* Surfaces */
  --op-bg: #0c0c12;
  --op-surface: #141420;
  --op-surface-2: #1c1c2c;
  --op-surface-active: #1a1834;
  --op-border: #242438;
  --op-border-subtle: #1a1a28;

  /* Brand (unchanged; pale steps to a deep blue) */
  --op-blue-darker: #161438;
  --op-blue-dark: #26245c;
  --op-blue-mid: #3a4585;
  --op-blue: #5461a6;
  --op-blue-light: #8a94c9;
  --op-blue-pale: #1a1834;

  /* Secondary accent (stepped lighter to read on near-black) */
  --op-green: #a4d564;

  /* Text */
  --op-text: #f4f4fc;
  --op-text-2: #c0c0dc;
  --op-text-muted: #9898b8;
  --op-text-faint: #6a6a88;
  --op-text-on-blue: #ffffff;

  /* Links (lighter steps for legibility on dark) */
  --op-link: #8a94c9;
  --op-link-hover: #5461a6;

  /* Status (stepped lighter to read on near-black) */
  --op-success: #4ade80;
  --op-warning: #fbbf24;
  --op-error: #f87171;
  --op-info: #5461a6;

  /* Footer */
  --op-footer-bg: #000000;
  --op-footer-border: rgba(255, 255, 255, 0.1);
}
```

If you use Tailwind v4, mirror these into an `@theme` block so utilities such as
`bg-op-surface` and `text-op-text` resolve to the variables above.

## Quick reference

| Need | Token or value |
|---|---|
| Page background | `--op-bg` |
| Card | `--op-surface` + `--op-border`, square corners, 32px padding |
| Elevated card | `--op-surface-2` + `--op-border` |
| Primary action | `--op-blue` fill, white text, uppercase, 4px radius |
| Secondary action | Transparent fill, `--op-blue` border and text |
| Heading | Space Grotesk, `--op-text` |
| Body | Switzer 16px, `--op-text-2` |
| Link | `--op-link`, hover `--op-link-hover`, trailing `→` |
| Section label | `〇 LABEL`, `--op-text-muted`, uppercase, 14px |
| Soft banner | `--op-blue-pale` |
| Loud banner | `--op-blue-dark`, white text |
| Footer | `--op-footer-bg`, partner logos with `brightness(0) invert(1)` on dark |
| Code or IDs | `.mono` (JetBrains Mono) |

## Do and don't

**Do:**

- Use Space Grotesk for headings and Switzer for everything else.
- Open every titled section with the `〇 LABEL` pattern.
- Group related content into cards with square corners and an `--op-border` outline.
- Use the brand blues for every interactive element. Reserve status colors for
  badges, alerts, and toasts.
- Give every interactive element a clear hover and focus state.
- Define every token for both light and dark mode, and test both.

**Don't:**

- Don't mix in fonts beyond the three approved families.
- Don't introduce ad hoc colors. Add a token to this document first.
- Don't use medium or large radii on chrome.
- Don't add glow, neon, or drop-shadow chrome.
- Don't use Title Case or lowercase button labels — uppercase only.
- Don't write raw hex in component markup. Use tokens. Drawing code (D3, SVG) is
  the only exception.

---

**Maintained by:** SDSC. Update this document when the Figma kit changes or the
light-to-dark mapping needs to flex.
**Source:** Figma Make file `xFRPysbb2ni4RXyuT7dVqq` (SDSC UI Kit v2.1, based on
datascience.ch).
