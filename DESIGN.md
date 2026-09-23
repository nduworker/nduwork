# Design System — nduwork

## Product Context
- **What this is:** Niu Du's personal homepage at www.nduwork.com. It presents Niu as an AI builder, shows two open-source projects as selected work, links the portfolio, and shows a daily starred-repo pick with a blurb written by a local LLM.
- **Who it's for:** Engineers and hiring managers arriving from GitHub or Proreerfolio.
- **Space/industry:** Developer personal sites, open-source AI agent tooling.
- **Project type:** A single static page (GitHub Pages, no build step).
- **Memorable thing:** "This person builds things with AI": products, agents and the tools around them.

## Aesthetic Direction
- **Direction:** Field notebook. Warm paper, sharp ink, one vermilion signal, laid out like a technical poster.
- **Decoration level:** Intentional. Only 1px rules, the torn edge on the pick note, and a faint dot-grid "notebook paper" behind the project demos. Both demos use the same paper/ink/mono style as the rest of the page instead of each project's own branding.
- **Mood:** A working engineer's notebook, not a marketing page. Calm and confident, with evidence that real systems are running.

## Typography
- **Display/Hero:** Newsreader 600, with one italic phrase for emphasis. An editorial serif makes the headline feel authored rather than templated.
- **Body:** Instrument Sans 400/500. Clean and slightly humanist, and not the default Inter.
- **UI/Labels, data, code:** JetBrains Mono 400/500 with `tabular-nums`, used for the masthead, metadata, star counts, dates and the pick log.
- **Loading:** Google Fonts `family=Newsreader:ital,opsz,wght@0,6..72,600;1,6..72,600&family=Instrument+Sans:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap`
- **Scale:** hero `clamp(44px, 9vw, 96px)`/1.02, h2 32px/1.15, h3 22px/1.25, body 17px/1.6, small 14px/1.5, mono label 12px/1.4 uppercase +0.08em tracking.

## Color
- **Approach:** Restrained. Neutrals plus one signal color and one secondary.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#F3F0E7` | `#101717` | page paper |
| `--surface` | `#FFFCF4` | `#1B2424` | cards, pick note |
| `--ink` | `#172522` | `#F3F0E7` | primary text |
| `--muted` | `#53635C` | `#A7B2AC` | secondary text, meta |
| `--rule` | `#D9D3C4` | `#2A3535` | 1px hairlines |
| `--signal` | `#D4472F` | `#FF7857` | links, emphasis, stamp; use sparingly |
| `--teal` | `#2F6F6A` | `#5FA8A0` | PenguPool preview, secondary accents |

- **Dark mode:** Use `prefers-color-scheme` with tokens on `:root`. Surfaces are redesigned for dark, not inverted.

## Spacing
- **Base unit:** 8px. **Density:** Spacious.
- **Scale:** 2xs(2) xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48) 3xl(64) 4xl(96)

## Layout
- **Approach:** Creative-editorial. Left-aligned throughout.
- **First viewport:** Mono masthead (`NIU DU / BIOINFORMATICS ENGINEER` on the left, Proreerfolio and GitHub links on the right), then the big three-line headline, then two project destinations side by side (stacked below 720px).
- **Below the fold:** The Pick of the day as a field note, followed by a one-line footer.
- **Max content width:** 1120px, with a 24px gutter (16px on phones).
- **Border radius:** sm 2px, md 4px, lg 6px. No pills and no bubbles.

## Motion
- **Approach:** Minimal-functional. A 200ms fade-up on load, and project cards lift 2px on hover.
- **Easing:** enter ease-out, exit ease-in. **Duration:** micro 100ms, short 200ms.
- Respect `prefers-reduced-motion` by turning all motion off.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-23 | Initial design system created | Created by /design-consultation. The Codex "field notebook" direction was chosen over the "switchboard" direction because it costs less to maintain. |
| 2026-09-23 | Demos restyled to the page system; portfolio promoted | User feedback: the demos should match the landing style, and the portfolio should be more prominent. It now has a primary vermilion CTA in the hero and a full-width card with a signal-colored left rule. |
| 2026-09-23 | Reframed from "agent tooling" to "AI builder" | User feedback: they build more than coding-agent tools. The headline is now "I build things *with* AI.", the projects are labelled "Selected work", and the portfolio carries the breadth. |
| 2026-09-23 | Removed the portfolio card | User feedback: the hero "View my portfolio" CTA is enough, and the card below the projects was redundant. |
