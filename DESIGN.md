# Design System — PDF Redactor

## Product Context
- **What this is:** A client-facing PDF redaction tool. Users upload documents, mark sensitive content for removal via drawing or text search, preview the result, then export to Google Drive or download.
- **Who it's for:** Small teams and external clients handling sensitive documents.
- **Space/industry:** Document processing / regulated workflow tooling.
- **Project type:** Web app — single-page, task-focused, client-facing.

## Aesthetic Direction
- **Direction:** Bold-utilitarian — precision instrument energy with an editorial layout. Clean and direct.
- **Decoration level:** Minimal — typography weight, spacing, and card structure carry the depth. No decorative flourishes.
- **Mood:** Controlled and trustworthy. Strong typographic hierarchy pulls focus to the task. The document canvas is always the visual center.
- **Memorable thing:** "This is clean, modern, and means business."
- **Reference:** UX Pilot pricing page (warm beige bg, bold uppercase headings, navy/yellow-green pairing).

## Typography
- **UI / Body:** Inter (400 / 500 / 600 / 700 / 800 / 900) — industry-standard legibility with wide weight range for strong hierarchy.
- **Technical labels:** Geist Mono (400 / 500) — page counts, file sizes, session IDs, filename previews. Signals structured data.
- **Loading:** Google Fonts CDN
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
  ```
- **Scale:**

| Token   | Size  | Weight | Usage                              |
|---------|-------|--------|------------------------------------|
| hero    | clamp(2.6rem, 6vw, 4.5rem) | 900 | Upload state hero heading (uppercase) |
| heading | 1.05rem | 800  | Card/section headings              |
| subhead | 0.88rem | 700  | Logo text, sub-headings            |
| body    | 0.82–0.85rem | 400/500 | Base text, inputs           |
| body-sm | 0.78rem | 500/600 | Secondary body, button labels    |
| label   | 0.68–0.72rem | 600/700 | UI labels (uppercase + LS)  |
| caption | 0.63rem | 700  | Panel titles (uppercase + LS)      |
| mono    | 0.68–0.72rem | 400/500 | Geist Mono — technical data   |

## Color
- **Approach:** Warm beige base + deep navy primary + yellow-green CTA. Color is intentional and rare on the neutral scale; the CTA pops sharply against navy.

| Token              | Value                        | Usage                                         |
|--------------------|------------------------------|-----------------------------------------------|
| `--bg`             | `#e8e5dc`                    | Page background (warm beige)                  |
| `--surface-1`      | `#ffffff`                    | Cards, panels, inputs, login overlay          |
| `--surface-2`      | `#f0ede5`                    | Input backgrounds, canvas topbar, hover tints |
| `--surface-3`      | `#e5e2d9`                    | Pressed states                                |
| `--border`         | `#d8d4c8`                    | Default borders                               |
| `--border-strong`  | `#bbb7ab`                    | Input borders, interactive elements           |
| `--text-1`         | `#0c0c24`                    | Primary text (same as navy)                   |
| `--text-2`         | `#5a5770`                    | Muted labels, secondary text                  |
| `--text-3`         | `#9490a8`                    | Placeholders, disabled, captions              |
| `--navy`           | `#0c0c24`                    | Primary UI color — dark bg for buttons, header marks |
| `--cta`            | `#d4f34a`                    | CTA text on navy, match chips, primary button bg |
| `--cta-hover`      | `#c2e040`                    | CTA hover state                               |
| `--success`        | `#16a34a`                    | Confirmation messages                         |
| `--success-bg`     | `#f0fdf4`                    | Success background                            |
| `--success-border` | `#bbf7d0`                    | Success border                                |
| `--error`          | `#dc2626`                    | Validation errors                             |
| `--error-bg`       | `#fef2f2`                    | Error background                              |
| `--error-border`   | `#fecaca`                    | Error border                                  |
| `--info`           | `#92400e`                    | Preview mode banners (amber)                  |
| `--info-bg`        | `#fffbeb`                    | Info background                               |
| `--info-border`    | `#fde68a`                    | Info border                                   |

**Semantic color pattern:** status colors always use tinted bg + matching border. Never solid-fill backgrounds for status in the light theme.

**CTA rationale:** Yellow-green `#d4f34a` on navy `#0c0c24` gives maximum contrast and visual pop. Used exclusively as text/icon color on dark surfaces, or as the background for the one primary action per screen.

**Canvas drawing colors:** Selection rectangles use `rgba(12,12,36,.08)` fill + navy `#0c0c24` dashed stroke. This reads clearly against white PDF pages without misrepresenting the final solid black redaction output.

## Spacing
- **Base unit:** 4px
- **Density:** Comfortable — each element has room to read.

| Token | Value | Usage                                  |
|-------|-------|----------------------------------------|
| 2xs   | 2px   | Micro gaps, icon padding               |
| xs    | 4px   | Inline gaps                            |
| sm    | 8px   | Component internal spacing             |
| md    | 12px  | Between related elements               |
| lg    | 16px  | Section padding, toolbar gaps          |
| xl    | 24px  | Between sections                       |
| 2xl   | 32px  | Major layout divisions                 |
| 3xl   | 48px  | Page-level vertical rhythm             |

## Layout
- **Upload state:** Centered hero with large uppercase heading + centered upload card (max-width 520px). Feature chips below a dashed divider.
- **App state (editor/preview):** Two-column grid — 272px sidebar + 1fr canvas panel. Preview banner spans full width above the grid when in preview mode.
- **Max content width:** 1100px
- **Page padding:** 2rem horizontal

## Border Radius
| Token   | Value  | Applied to                              |
|---------|--------|-----------------------------------------|
| r-sm    | 4px    | Tags, file icon, close buttons          |
| r-md    | 8px    | Inputs, mode tabs, buttons, small cards |
| r-lg    | 12px   | Toasts, larger chips                    |
| r-xl    | 16px   | Panels, canvas wrap, preview banner     |

## Shadow
| Token     | Value                                              | Applied to                         |
|-----------|----------------------------------------------------|------------------------------------|
| shadow-sm | `0 1px 3px rgba(12,12,36,.06)`                    | Panels, upload zone default        |
| shadow-md | `0 4px 16px rgba(12,12,36,.08), 0 1px 4px rgba(12,12,36,.04)` | Canvas wrap, login card, toasts |

## Focus States
- All interactive elements: `box-shadow: 0 0 0 3px rgba(12,12,36,.08)` + `border-color: var(--navy)` on focus.
- Never rely on browser default outlines.

## Motion
- **Approach:** Minimal-functional — only transitions that aid comprehension.
- **Easing:** enter → `ease-out`, exit → `ease-in`, move → `ease-in-out`
- **Duration:** hover/focus → `120ms`. Status appearance → `200ms`. Upload button lift → `100ms ease-out`.

## Component Notes

**Buttons**
- Primary (CTA bg): `background: var(--cta); color: var(--navy)`. Bold 800 weight. Used for the single primary action per screen.
- Primary (navy bg): `background: var(--navy); color: var(--cta)`. Used for upload CTA, Drive action, Find button.
- Secondary: white/transparent bg + `border: 1.5px solid var(--border-strong)`. Hover fills surface-2 + darkens border to navy.
- Ghost: transparent bg, no border. Hover fills surface-2. Used for low-emphasis cancel actions.
- Disabled: `opacity: 0.35`.

**Mode tabs (Draw / Text Search)**
- Container: `background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--r-md)`.
- Active: `background: var(--navy); color: var(--cta)`.
- Inactive: transparent + `color: var(--text-2)`. Hover fills `var(--surface-3)`.

**Upload zone**
- Default: `border: 2px dashed var(--border-strong); background: var(--surface-1)`.
- Hover/dragover: `border-color: var(--navy); background: var(--surface-2)`.

**Canvas area**
- Background: `#cbc8bf` — warm gray so the white PDF page reads distinctly against it.
- Wrapped in a card panel (border + border-radius + shadow-md).
- Topbar: mode label + match chip + page nav. Bottombar: status message area.

**Sidebar panels**
- All panels: `background: var(--surface-1)` + `border: 1px solid var(--border)` + `border-radius: var(--r-xl)` + `shadow-sm`.
- Panel titles: 0.63rem, 700, uppercase, wide letter-spacing, `var(--text-3)`.

**Preview banner**
- Spans full width above the app grid when active (`.visible` class).
- Amber/info color scheme: `--info-bg` + `--info-border` + `--info` text.
- Actions: navy Drive button + CTA download button + ghost cancel.

**Logo mark**
- 28×28px navy square (r=6px) with "PR" in CTA color. Used in header and login overlay.

**Match chip**
- `background: var(--cta); color: var(--navy)`. Pill-shaped. Shown in canvas topbar when selections/matches exist.

**Tags/badges**
- True Redaction: `background: var(--error-bg); color: #991b1b; border: 1px solid var(--error-border)`.
- Drive connected: `background: var(--success-bg); color: #15803d; border: 1px solid var(--success-border)`.
- Drive disconnected: `background: var(--surface-2); color: var(--text-2); border: 1px solid var(--border)`.

## Decisions Log
| Date       | Decision | Rationale |
|------------|----------|-----------|
| 2026-07-08 | Light theme over dark | Product is client-facing; "clean and modern" aligns with light. |
| 2026-07-08 | Switched accent from teal to navy+CTA pairing | UX Pilot-inspired redesign. Navy+yellow-green gives stronger visual pop and editorial feel. |
| 2026-07-08 | Switched from Instrument Sans to Inter | Inter's wider weight range (up to 900) is required for the bold uppercase hero heading and strong typographic hierarchy. |
| 2026-07-08 | Warm beige background (#e8e5dc) | Replaces zinc white. Adds warmth and distinctiveness; less sterile, more considered. |
| 2026-07-08 | Two-state layout (upload hero / sidebar+canvas) | Clear mode separation: the hero communicates the product before any file is loaded; the sidebar+canvas is a focused work environment. |
| 2026-07-08 | Geist Mono kept for technical labels | Treats data (page counts, filenames, session IDs) as structured typography. Consistent with original design intent. |
