---
name: frontend-design
description: "Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults."
license: Apache-2.0
compatibility: opencode
metadata:
  source: https://github.com/anthropics/skills
---
# Frontend Design

Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the user (using OpenCode's native `question` tool when running as primary agent). You can come up with one concrete subject, the design's audience, and the design's primary job, as a proposal. If there's any information in project docs about the user's preferences or context about what they're building, use that as a hint. The subject's industry, subject matter, materials, and vernacular are where distinctive visual choices come from — a design for a consumer app will be very aesthetically different from a dashboard for financial analysts. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is the first thing viewers will see. Open with the most characteristic thing in the subject's world, in the form that is most appropriate: a headline, an image, an animation, a live demo, an interactive moment, or other treatments. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the default treatment, so only use it if that's truly the best option.

Typography carries the personality of the page. You don't need a different typeface for display or headline text and body content: use one family or two, and if two, make them clearly distinct.

Choose your typefaces deliberately, not the default families you would reach for on any other project, and set a clear type scale following *The Elements of Typographic Style* with intentional weights, widths, and spacing. When type is used as a headline or visual element, use the type treatment itself as an active part of the design, not a neutral delivery vehicle for the content.

Default to line lengths of less than 80 characters. Serif typefaces can have slightly longer line lengths; give serif body text slightly more line-height than a sans-serif.

Avoid these default typographic treatments; they are the commonest tells of a generated page:
- Accenting just a single word or phrase in a headline, like putting one word in italic/bold or a different color.
- Using all caps for labels.
- Adding unnecessary typographic labels above content.

Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode useful information about the content rather than decorate it. Many generic designs use numbered markers (`01 / 02 / 03`), but that's only appropriate if the content actually is a sequence — like a stepped process or a timeline. Before adding numbered markers, check the content really is a sequence.

Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment — one page-load sequence or one reveal — lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself.

## Process: plan, review against the brief, build, critique

For calibration, AI-generated design right now clusters around some traits:
- A warm cream background (near `#F4F1EA`) with a high-contrast serif display and a terracotta or warm-clay accent (near `#D97757`).
- A near-black background with a single bright acid-green or vermilion accent.
- A broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns.
- The SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow (`rgba(0,0,0,.1)`) under each, and gradient washes as decoration.
- Template chrome that appears whatever the subject: a tracked-out ALL-CAPS eyebrow label above every heading; meta strings joined with middle dots (`A · B · C`); labels built as `WORD — fragment` with a spaced em dash; tinted near-black (`#0B0B0B`, `#111`) standing in for black; a monospace face for small data labels; a `→` appended to link and button text.

All traits are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly — the brief's own words always win. Where it leaves an axis free, don't spend that freedom on one of these defaults.

**Work in two passes:**
1. **Plan:** Brainstorm a short design plan based on the brief: create a compact token system with:
   - **Color:** core base palette as 4–6 named hex values (with CSS variables).
   - **Type:** typefaces and their roles.
   - **Layout:** layout concept with alignment guidance (left, center, justified).
   - **Principles:** high-level guidance for what makes this page unique.
2. **Critique & Revise before coding:** Review that plan against the brief before building: if any part reads like the generic default you would produce for any similar page rather than a choice made for this specific brief, revise that part and note what changed and why. Only after confirming the uniqueness of the design plan, write the code following the revised plan.

When writing CSS, be careful structuring selector specificities so classes do not cancel each other out (especially between layout/section classes and element-level utility classes).

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected (`prefers-reduced-motion`), visually accessible, harmonious color palettes. Critique your own work as you build — pair with `webapp-testing` to take Playwright screenshots and inspect the rendered UI visually.

## Writing in design

Words appear in a design for one reason: to make it easier to understand and use. Bring the same intentionality and minimalism to copywriting that you bring to spacing and color.
- Write from the end user's perspective ("Notifications", not "Webhook config").
- Use active voice as default: a CTA says exactly what happens ("Save changes", not "Submit"), and keeps the same vocabulary across the flow ("Publish" → toast "Published").
- Treat failure and emptiness as moments for direction, not mood: explain what went wrong and how to fix it clearly without apologizing or being vague.
- Keep the tone conversational: plain verbs, sentence case, no filler, matched to brand and audience.
