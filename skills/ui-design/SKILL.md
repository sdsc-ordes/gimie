---
name: sdsc-ui-design
description: >-
  Applies the Swiss Data Science Center (SDSC) visual identity to framework-agnostic web UI (
  design, typography, spacing, components, and layouts). Use when building, editing, or reviewing
  any visual component that should follow the SDSC look; when  defining or editing design tokens,
  colors, fonts, radius, or spacing; or when the user says "design", "restyle", "SDSC branding" or
  "match the design system". Skip for non-visual work, and for non-SDSC visual identities.
---

# UI design — SDSC visual system

Build and review web UIs that follow the **Swiss Data Science Center (SDSC)**
visual identity. 

The system is derived from the SDSC UI Kit (Figma Make file
`xFRPysbb2ni4RXyuT7dVqq`, UI Kit v2.1, based on
[datascience.ch](https://datascience.ch)).

## When to use this skill

Use it for any web UI work that should carry the SDSC look:

- Creating, styling, or restyling a page, component, or layout.
- Defining or editing design tokens, colors, fonts, radius, or spacing.
- Building or extending a design system or token set.
- Reviewing a UI change or pull request for brand consistency.

Skip it for backend, infrastructure, CI, devcontainer, or shell-script work, and
for surfaces that intentionally use a different (non-SDSC) visual identity.

## How to use this skill

1. **Read `references/design.md` first** the moment you touch a UI surface in a
   session. It is the design language; this file only summarizes it.
2. **Reach for an existing token before inventing a value.** Tokens are CSS
   custom properties (`--op-*`) in the stylesheet (for example, `app.css`).
3. **If a value doesn't exist, add it to `references/design.md` first**, then to
   the stylesheet (both `:root` and `.dark`), and only then use it in code.
   Never write an ad-hoc hex, radius, or spacing value in component markup.
4. **Reference tokens by name, never a mode-specific hex.** Components adapt to
   light or dark automatically because they read token names.
5. **Verify every visible change in both modes** before considering it done.

## Non-negotiable principles

The SDSC look is **Swiss, structured, and sharp-edged**:

- **Minimal and academic** — no glow, no neon, no decorative gradients beyond
  the one approved brand gradient (`linear-gradient(135deg, #5461a6, #26245c)`).
- **Two blues carry the brand** — dark blue `#26245c` and interactive blue
  `#5461a6` are the only chrome colors. Status colors appear only on badges,
  alerts, toasts, and progress states.
- **Sharp corners** — cards, panels, and banners are square (`0`). Buttons and
  small controls carry a `4px` radius. Only avatars and floating buttons are
  fully round. Never use `8px`+ radii on chrome.
- **Three fonts only** — **Space Grotesk** for headings, **Switzer** for body
  and all UI chrome, **JetBrains Mono** for code and IDs.
- **The `〇 LABEL` pattern** — every titled section opens with a circle-prefixed,
  uppercase, muted label. It is the kit's signature (full markup in the
  reference).
- **One token set, two modes** — light mode on `:root`, dark mode overriding the
  same names under `.dark`. Define every new token for both modes.
- **Uppercase buttons** — button labels are always uppercase, Switzer Regular,
  with wide tracking. Never Title Case or lowercase.
- **Accessibility is required** — meet WCAG AA contrast (4.5:1 body) in both
  modes, give every interactive element a visible `2px --op-blue` focus state,
  keep tap targets ≥ 44×44px, and never use color as the only signal.

## What's in `references/design.md`

Load the reference and jump to the relevant section:

| You need… | Section |
|---|---|
| Full token tables (brand, surface, text, links, status, neutrals, footer) and the `:root`/`.dark` CSS | **Color**, **Implementation reference** |
| Adding a new color/token the right way | **Color → Add a new color** |
| Font families, type scale, line-height, dark-mode weight rules | **Typography** |
| Border radius, padding/gap, page widths (8px unit) | **Spacing, layout, and shape** |
| The `〇 LABEL` block markup | **Content label pattern** |
| Buttons, links, badges, cards, inputs, checkboxes/toggles, progress, tables, icon box | **Components** |
| The ten page templates (header, footer, hero, feature grid, banners, key numbers, lists, sidebar, event index, article grid) | **Page layouts** |
| Logo usage and the four partner logos | **Logos** |
| Backgrounds, dot patterns, the approved gradient | **Backgrounds and patterns** |
| Contrast, focus, keyboard, tap-target rules | **Accessibility** |
| A one-glance cheat sheet | **Quick reference** |

## Building a UI surface

1. Read `references/design.md` (whole file the first time).
2. Confirm the active mode(s) the surface must support; ensure tokens exist for
   both `:root` and `.dark`.
3. Compose from the **Components** and **Page layouts** sections — copy the
   reference markup and swap in token names, not raw hex.
4. Open every titled section with the `〇 LABEL` pattern.
5. Add hover and focus states to every interactive element.
6. Verify contrast and behavior in both light and dark mode.

## Reviewing a UI change

Flag anything that violates the principles above: raw hex in markup (drawing
code like D3/SVG is the only exception), medium/large radii on chrome, fonts
beyond the approved three, glow/neon/drop-shadow chrome, non-uppercase button
labels, a token defined for only one mode, missing focus states, or status
colors used as chrome. For each, point to the correct token or pattern in
`references/design.md`.
