# Design System — PDF Redactor

## Product Context
- **What this is:** A client-facing PDF redaction tool. Users upload documents, mark sensitive content for removal via drawing or text search, preview the result, then export to Google Drive or download.
- **Who it's for:** Small teams and external clients handling sensitive documents.
- **Space/industry:** Document processing / regulated workflow tooling.
- **Project type:** Web app — single-page, task-focused, client-facing.

## Aesthetic Direction
- **Direction:** Industrial/Utilitarian — refined, not raw. Precision-instrument energy.
- **Decoration level:** Minimal — typography, spacing, and subtle shadow carry the depth; no decorative flourishes.
- **Mood:** Trustworthy and controlled. Every chrome element recedes so the document content comes forward. The tool should feel like a scalpel: purpose-built, precise, nothing extraneous.
- **Memorable thing:** "This is clean and modern."
- **Reference sites:** Notion (light mode), Linear, Vercel — dark-first tools that also execute a refined light mode.

## Typography
- **UI / Body:** Instrument Sans (400 / 500 / 600) — humanist precision without Inter's clinical coldness. Distinctly contemporary without feeling trendy.
- **Technical labels:** Geist Mono (400 / 500) — session IDs, page counts, file sizes, filename previews. Signals "this is structured data" without visual noise.
- **Loading:** Google Fonts CDN
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
  ```
- **Scale:**

| Token   | Size  | Weight | Usage                        |
|---------|-------|--------|------------------------------|
| display | 32px  | 600    | App name, hero headings      |
| heading | 20px  | 600    | Section headers              |
| subhead | 16px  | 500    | Sub-section labels           |
| body    | 14px  | 400    | Base text, descriptions      |
| body-sm | 13px  | 400    | Secondary body, helper text  |
| label   | 12px  | 500    | UI labels, small elements    |
| caption | 11px  | 500    | Uppercase captions (UC + LS) |
| mono    | 12px  | 400    | Geist Mono — technical data  |

## Color
- **Approach:** Restrained — one distinctive accent plus a zinc-based neutral scale. Color is rare and intentional; when it appears it means something.

| Token          | Value     | Usage                                         |
|----------------|-----------|-----------------------------------------------|
| `--bg`         | `#fafafa` | Page background                               |
| `--surface-1`  | `#ffffff` | Cards, panels, login overlay                  |
| `--surface-2`  | `#f4f4f5` | Inputs, document canvas, secondary bg         |
| `--surface-3`  | `#ececed` | Hover states, pressed states                  |
| `--border`     | `#e4e4e7` | Default borders                               |
| `--border-strong` | `#d4d4d8` | Input borders, interactive elements          |
| `--text-1`     | `#18181b` | Primary text                                  |
| `--text-2`     | `#71717a` | Muted labels, secondary text                  |
| `--text-3`     | `#a1a1aa` | Placeholders, disabled, captions              |
| `--accent`     | `#0d9488` | Primary CTA, active tabs, focus rings         |
| `--accent-hover` | `#0f766e` | Accent hover state                          |
| `--accent-light` | `#f0fdfa` | Accent tinted bg (upload zone hover)        |
| `--accent-dim` | `rgba(13,148,136,.08)` | Subtle accent fill            |
| `--success`    | `#16a34a` | Confirmation messages, Drive badge            |
| `--success-bg` | `#f0fdf4` | Success state background                      |
| `--success-border` | `#bbf7d0` | Success state border                      |
| `--error`      | `#dc2626` | Validation errors, required field states      |
| `--error-bg`   | `#fef2f2` | Error state background                        |
| `--error-border` | `#fecaca` | Error state border                          |
| `--info`       | `#0284c7` | Info banners (preview confirmation strip)     |
| `--info-bg`    | `#f0f9ff` | Info state background                         |
| `--info-border` | `#bae6fd` | Info state border                            |

**Semantic color pattern:** status colors always use the tinted-bg + matching border approach. Never solid-fill backgrounds for status in the light theme.

**Accent rationale:** Teal `#0d9488` is unused by every major PDF tool (all run blue). It reads as clinical precision and measured trust — appropriate for a tool handling sensitive documents.

## Spacing
- **Base unit:** 4px
- **Density:** Comfortable — not cramped, not airy. Each element has room to read; the document canvas should feel like the visual center.

| Token | Value | Usage                               |
|-------|-------|-------------------------------------|
| 2xs   | 2px   | Micro gaps, icon padding            |
| xs    | 4px   | Inline gaps, tight element spacing  |
| sm    | 8px   | Component internal spacing          |
| md    | 12px  | Between related elements            |
| lg    | 16px  | Section padding, toolbar gaps       |
| xl    | 24px  | Between sections                    |
| 2xl   | 32px  | Major layout divisions              |
| 3xl   | 48px  | Page-level vertical rhythm          |
| 4xl   | 64px  | Preview/marketing sections          |

## Layout
- **Approach:** Grid-disciplined — predictable alignment, consistent padding. The app is a focused single-page tool; no sidebar, no complex navigation. The document canvas is the visual center.
- **Max content width:** 1100px (matches existing `--container`)
- **Page padding:** 24px horizontal on mobile, 32px on desktop

## Border Radius
| Token | Value  | Applied to                    |
|-------|--------|-------------------------------|
| r-sm  | 4px    | Tags, badges, small chips     |
| r-md  | 6px    | Buttons, mode tabs            |
| r-input | 8px  | Text inputs, search fields    |
| r-lg  | 10px   | Cards, screen frames, panels  |
| r-full | 9999px | Pills, circular elements     |

## Shadow
| Token      | Value                                              | Applied to              |
|------------|----------------------------------------------------|-------------------------|
| shadow-sm  | `0 1px 2px rgba(0,0,0,.06)`                       | Swatches, subtle lift   |
| shadow-md  | `0 2px 8px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04)` | Cards, login panel, screen frames |

Shadows replace heavy borders as the primary depth signal on the light theme.

## Focus States
- All interactive elements: `box-shadow: 0 0 0 3px rgba(13,148,136,.1)` + `border-color: var(--accent)` on focus.
- Never rely on browser default outlines.

## Motion
- **Approach:** Minimal-functional — only transitions that aid comprehension. Nothing decorative.
- **Easing:** enter → `ease-out`, exit → `ease-in`, move → `ease-in-out`
- **Duration:** hover/focus state changes → `120–150ms`. Status appearance → `200ms`. Nothing longer without user intent.

## Component Notes

**Buttons**
- Primary: `background: var(--accent)` + subtle teal shadow. Hover darkens to `--accent-hover`.
- Secondary: white bg + `border: 1px solid var(--border-strong)` + `shadow-sm`.
- Ghost: transparent bg + `border: 1px solid var(--border)`. Hover fills with `--surface-2`.
- Disabled: `opacity: 0.4`.

**Mode tabs (Draw / Text Search)**
- Container: `border: 1px solid var(--border-strong)` + `border-radius: var(--r-md)` + `shadow-sm`.
- Active tab: `background: var(--accent); color: #fff`.
- Inactive tab: `background: var(--surface-1); color: var(--text-2)`.

**Upload zone**
- Default: `border: 1.5px dashed var(--border-strong)`.
- Hover/dragover: `border-color: var(--accent); background: var(--accent-light)`.

**Document canvas**
- Background: `var(--surface-2)` — light gray so the white PDF page reads distinctly against it.

**Status messages**
- Always: tinted bg + colored border + matching text. Never solid fill.

**Tags/badges**
- Redaction: `background: #fef2f2; color: #991b1b; border: 1px solid #fecaca`.
- Drive connected: `background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0`.
- Drive disconnected: `background: var(--surface-2); color: var(--text-2); border: 1px solid var(--border)`.

## Decisions Log
| Date       | Decision | Rationale |
|------------|----------|-----------|
| 2026-07-08 | Light theme over dark | Product is client-facing; "clean and modern" aligns with light. Existing dark theme was for internal use. |
| 2026-07-08 | Teal accent (#0d9488) over blue | Every PDF tool in the category uses blue. Teal reads as precision/trust and differentiates. |
| 2026-07-08 | Instrument Sans as primary font | Humanist precision without Inter's overuse. Contemporary, legible, not trendy. |
| 2026-07-08 | Geist Mono for technical labels | Treats data (session IDs, page counts, filenames) as typography, not afterthought. |
| 2026-07-08 | Zinc-based neutral scale | Slightly cool grays (zinc) feel more precise than warm grays; matches the tool's precision-instrument aesthetic. |
