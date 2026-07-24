# MathWizard Brand Guidelines

> Stage A deliverable for the full visual redesign. This is the single source of
> truth for the new visual language. Token values here are copied verbatim into
> `frontend/src/index.css` during implementation (Stage B).

## Brand essence

MathWizard turns exam maths into something a student *wants* to open. The mark is
a bold-outlined geometric gem (a wizard-hat abstraction) in flat pastel fills.
The redesign takes that mark literally: **flat geometric shapes, confident ink
outlines, pastel fills, and generous light space.**

**Personality:** clear, confident, a little playful. Not a corporate SaaS
dashboard, not a childish edu-app. Think "well-made study tool with taste."

**Retired from the old design (full replace):**
- Graph-paper / notebook ambient background
- Instrument Serif display face
- Cool blue-grey backgrounds (`#fafbfd`) and glassmorphism
- Scattered, untokenised hex values

## Logo

- Primary asset: `data/copy/logo.jpeg` (horizontal lockup: gem mark + "Math Wizard" wordmark).
- **Action items for implementation:** export a clean **SVG** (and PNG @1x/@2x)
  from this artwork; produce an **icon-only** variant (just the gem) for the
  favicon and compact header; generate a matching favicon to replace the leftover
  purple Vite icon at `frontend/public/favicon.svg`.
- Clear space: keep at least the height of the peach band around the mark.
- Do not recolor the mark's outline to anything but ink; do not add gradients.

## Color palette

Sampled from the logo, then extended into usable ramps. Format: hex.

### Primitives

**Ink (outlines, text) — the signature of the whole system**
| Token | Hex | Use |
|-------|-----|-----|
| `--ink-950` | `#111318` | Outlines, headings, primary text |
| `--ink-800` | `#282B33` | Body text |
| `--ink-600` | `#4C515C` | Secondary text |
| `--ink-400` | `#878C98` | Muted / placeholder |
| `--ink-200` | `#CBCFD8` | Hairlines, disabled |

**Sky (primary blue family — from the gem)**
| Token | Hex | Use |
|-------|-----|-----|
| `--sky-100` | `#EAF3FC` | Tint backgrounds |
| `--sky-200` | `#D2E5F7` | Soft fills |
| `--sky-300` | `#BAD6F0` | Top-triangle blue (logo) |
| `--sky-400` | `#9BBEE6` | Lower-gem blue (logo) |
| `--sky-500` | `#6F9FD8` | Hover fills |
| `--sky-600` | `#3F79BF` | Interactive / links / focus |
| `--sky-700` | `#2A5A93` | Pressed / strong accents |

**Peach (accent family — from the band)**
| Token | Hex | Use |
|-------|-----|-----|
| `--peach-100` | `#FDF4E8` | Tint backgrounds |
| `--peach-200` | `#FBE3C6` | Band peach (logo) |
| `--peach-300` | `#F6CE9E` | Accent fills, highlights |
| `--peach-400` | `#EAB170` | Strong accent / badges |

**Neutrals**
| Token | Hex | Use |
|-------|-----|-----|
| `--paper` | `#FCFBF7` | App background (warm, not cool) |
| `--surface` | `#FFFFFF` | Cards, sheets |

**Functional (kept flat + pastel to match the system)**
| Token | Hex | Use |
|-------|-----|-----|
| `--success-fill` `--success-ink` | `#D9F0E1` / `#1F6B45` | Easy / correct |
| `--warning-fill` `--warning-ink` | `#FBE8C4` / `#8A5A17` | Medium |
| `--danger-fill` `--danger-ink` | `#F7D6D2` / `#A62F26` | Hard / errors |

### Semantic layer (what components actually reference)

```
--color-bg:            var(--paper)
--color-surface:       var(--surface)
--color-text:          var(--ink-800)
--color-heading:       var(--ink-950)
--color-text-muted:    var(--ink-600)
--color-text-faint:    var(--ink-400)
--color-outline:       var(--ink-950)   /* the bold border */
--color-hairline:      var(--ink-200)   /* subtle dividers */
--color-primary:       var(--sky-600)
--color-primary-fill:  var(--sky-300)
--color-primary-hover: var(--sky-700)
--color-accent:        var(--peach-300)
--color-accent-fill:   var(--peach-200)
--color-focus:         var(--sky-600)
```

## Typography

The logo wordmark is a clean geometric sans. For a distinctive full replace:

- **Display / headings:** `Space Grotesk` — geometric, slightly characterful,
  pairs naturally with bold outlines and the gem. Weights 500/700.
- **Body / UI:** `DM Sans` — already loaded, highly readable, neutral. Weights 400/500/600.
- **Math:** unchanged — MathJax handles rendering.

```
--font-display: 'Space Grotesk', 'DM Sans', system-ui, sans-serif;
--font-body:    'DM Sans', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
```

Type scale (rem): `0.75 / 0.875 / 1 / 1.125 / 1.375 / 1.75 / 2.25 / 3`.
Headings use `--font-display` at 700; body at 400–500; line-height 1.5 body / 1.15 display.

## Shape, outline & elevation — the signature

This is what makes the redesign read as "the logo, everywhere."

- **Bold ink outline:** primary surfaces (cards, buttons, inputs, badges) carry a
  `1.5px` (controls) to `2px` (cards) `--color-outline` border. This is the
  defining move — flat fills bounded by confident ink lines, exactly like the mark.
- **Hard offset shadow (signature accent, used sparingly):** primary CTAs and hero
  cards get a solid offset shadow `4px 4px 0 var(--ink-950)` instead of a soft blur.
  Everything else stays flat or uses a very soft shadow.
- **Radius scale:** crisp, geometric.
  ```
  --radius-sm: 6px;  --radius-md: 10px;  --radius-lg: 16px;  --radius-pill: 999px;
  ```
- **Spacing scale (px):** `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64`.
- **Layout:** `--container-max: 1040px`, `--header-height: 68px`.

## Motion

Restrained and snappy. Ease `cubic-bezier(0.2, 0.8, 0.2, 1)`, durations 120–220ms.
- Buttons: press translates `2px 2px` into their offset shadow (tactile "click").
- Cards: hover lifts 2px + outline darkens.
- Page enter: 8px rise + fade, 180ms. No decorative looping animation.

## Component intent (defined fully in Stage B)

- **Button** — variants: `primary` (sky-300 fill, ink outline, hard shadow),
  `secondary` (surface fill, ink outline), `ghost` (no fill/outline, ink text).
- **Card** — surface fill, 2px ink outline, radius-lg, optional peach top-band.
- **Input** — surface fill, 1.5px ink outline, sky-600 focus ring.
- **Badge** — pill, flat functional fill + matching ink text, 1px outline.

## Voice

UI copy stays **Dutch**, consistent with the current app. Tone: direct,
encouraging, jargon-free.

## Anti-patterns (do not reintroduce)

- Purple/violet anything (the old favicon).
- Soft blurry drop shadows everywhere, glassmorphism, gradients on the mark.
- Generic SaaS card layouts or "pill soup."
- Untokenised hex values in component CSS — everything references the semantic layer.
