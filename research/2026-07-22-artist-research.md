---
date: 2026-07-22
worker: unattributed (backfilled)
type: research
mission: ""
source: "pre-contract record, was analysis/artist-research.md"
---

# Artist research: professional technical documentation in Obsidian

Research date: 2026-07-22  
Scope: inventory only plus recommendations. No vault files or plugin installations were changed.

## Executive recommendation

Do not add a broad visual-plugin stack. This vault already has the right foundation: AnuPpuccin, a scoped 1215 Labs CSS snippet, native Mermaid, and Excalidraw. The highest-value sequence is:

1. Give the Agentic Terminal Stack notes one scoped documentation class and a small Mermaid/callout CSS layer using the existing 1215 dark tokens.
2. Establish one Excalidraw technical-diagram template and a small reusable library of terminal/agent/model primitives.
3. Add Advanced Canvas only if Mike wants a navigable architecture map or presentation surface. Add Callout Manager only if authoring custom callouts by hand becomes friction.
4. Defer banners and chart plugins until a real content need appears. They add surface area without improving these particular notes today.

## Part 1 — current vault inventory

### Plugin folders on disk

| Folder | Manifest name | Version | Enabled in `community-plugins.json` |
|---|---|---:|:---:|
| `copilot` | Copilot | 3.2.7 | No |
| `dataview` | Dataview | 0.5.68 | Yes |
| `obsidian-clipper` | Clipper | 0.2.9 | Yes |
| `obsidian-excalidraw-plugin` | Excalidraw | 2.22.0 | Yes |
| `obsidian-opencode` | OpenCode | 0.1.0 | Yes |
| `perplexity-converter` | Perplexity Converter | 1.0.6 | Yes |
| `table-editor-obsidian` | Advanced Tables | 0.22.1 | Yes |

Interpretation: Copilot is present on disk but not enabled/listed. Excalidraw is installed and enabled. The installed Excalidraw build is 2.22.0; upstream listed 2.25.3 as the latest release on 2026-07-09, so the vault is a few releases behind. Updating is not required for the recommendations below and was not attempted.

### Theme folders on disk

- 1215 Labs
- AnuPpuccin
- LYT Mode
- Obsidianite
- Oxygen
- Wasp

### Active appearance

`appearance.json` says:

- color scheme: `system`
- CSS theme: `AnuPpuccin`
- enabled snippet: `hermes-wiki-1215`
- accent color: unset, so the theme/default decides it

The enabled snippet is already a useful mini design system. It is opt-in via `cssclasses: hermes-wiki`, uses Inter/JetBrains Mono fallbacks, constrains reading width to 980px, styles headings/tables/code/callouts, and supplies dark-mode token overrides. Its dark palette is roughly near-black `#1d1d1f` / tile `#272729`, near-white `#f5f5f7`, blue `#2997ff`, plus green and red semantic colors. Reusing those tokens will produce a more coherent result than introducing a second palette.

## Part 2A — Excalidraw advanced capabilities

The installed plugin is much more than a sketch pad. Its most relevant technical-documentation capabilities are:

### Libraries and reusable primitives

- Excalidraw libraries (`.excalidrawlib`) store reusable groups of elements. For this vault, a small local library could contain terminal panes, agent/model cards, API/service boxes, datastore cylinders, status badges, and standard arrow/edge labels.
- The public [Excalidraw Libraries catalog](https://libraries.excalidraw.com/) can seed generic icons, but a restrained local library will create more visual consistency than mixing illustration styles.
- A default drawing template can preserve stroke color/width, fill, opacity, font, and custom palette. That makes every new architecture drawing start on-brand rather than requiring manual cleanup.

Recommended library rule: keep primitives neutral and semantic. Use one blue for control/orchestration, purple for models, green for success/ready, amber for human gates, red only for destructive/failure paths. Avoid decorative icon packs unless an icon disambiguates a component faster than a label.

### Styling

- Templates can define default drawing properties and palettes. A technical preset should use a solid fill, thin strokes, rounded rectangles, Cascadia/monospace for commands, and the existing 1215 dark colors.
- Per-drawing frontmatter controls transparent backgrounds, dark export, padding, PNG scale, link prefixes, and default view/zen mode.
- Markdown embedded inside a drawing can be styled using `excalidraw-font`, `excalidraw-font-color`, `excalidraw-border-color`, and `excalidraw-css` frontmatter.
- Custom fonts, a fourth font, SVG import, LaTeX, custom pens, and image insertion are available, though most are secondary for architecture documentation.

### Embedding, linking, and export

- Drawings embed in notes with sizing/alignment syntax such as `![[architecture.excalidraw|900]]`, `|900x500`, or alignment values.
- Drawing text can contain Obsidian wikilinks. Links update on file rename (when Obsidian's automatic link updating is enabled) and participate in backlinks.
- Excalidraw can transclude a whole note, a heading, or a block reference into a drawing. It can also link to or embed a selected area/group/element of a larger drawing, which is useful for maintaining one canonical architecture map while showing cropped subsystems in individual notes.
- Auto-export can keep SVG and/or PNG synchronized. Prefer SVG for technical diagrams: it stays sharp, is diff-adjacent and portable, and works where native `.excalidraw` embeds do not. Upstream specifically notes that native drawings do not display in Obsidian Publish, making auto-export the safe publishing path.

Source: [Excalidraw for Obsidian repository and feature guide](https://github.com/zsviczian/obsidian-excalidraw-plugin).

### Script Engine and ExcalidrawAutomate

- The Script Engine runs ExcalidrawAutomate macros from the command palette and allows hotkeys. Scripts can be grouped in folders and shown in the Excalidraw tools panel.
- The built-in script library installs scripts only after an explicit choice. Scripts are code, so review their source and keep the set small.
- ExcalidrawAutomate integrates with QuickAdd, Templater, and Dataview. It can generate diagrams from structured data, apply repeatable styles, create linked elements, and automate exports.
- High-value future automation for this cluster: select a Mermaid block or a list of components, generate a branded Excalidraw scaffold, then leave layout/editing to the author. Do not automate this until the manual visual grammar is stable.

Source: [official Script Engine library](https://github.com/zsviczian/obsidian-excalidraw-plugin/tree/master/ea-scripts).

## Part 2B — worthwhile visual plugins, prioritized

Maintenance signals below are point-in-time observations from the Obsidian community catalog and upstream repositories on 2026-07-22, not guarantees.

| Priority | Plugin/approach | Maintenance signal | Best use here | Recommendation |
|---:|---|---|---|---|
| 1 | Native Mermaid + scoped CSS | Core Obsidian feature; Mermaid actively maintained | Flowcharts, state/sequence diagrams kept as text | Use now; no plugin required. |
| 2 | Excalidraw (already enabled) | Upstream 2.25.3 released 2026-07-09; hundreds of releases | Hero architecture diagrams, annotated workflows, reusable visual primitives | Standardize before adding anything else. |
| 3 | [Advanced Canvas](https://community.obsidian.md/plugins/advanced-canvas) | 6.5.0, updated ~2 weeks ago; 100 releases; 678k downloads | Navigable cluster map, presentations, collapsible groups, styled nodes/edges, SVG/PNG export | Best optional install if a spatial overview is desired. |
| 4 | [Callout Manager](https://community.obsidian.md/plugins/callout-manager) | 1.1.1, updated ~3 months ago; 179k downloads | Visual picker/editor for custom callouts; detects theme/snippet callouts | Optional authoring convenience. CSS alone is enough for a small callout vocabulary. |
| 5 | [Slick Mermaid](https://community.obsidian.md/plugins/slick-mermaid) | 0.1.9, updated ~3 weeks ago; only 2 months old | Automatically maps Obsidian theme variables into Mermaid; pan/zoom dialog | Promising, but too new to outrank a 30-line scoped snippet. Trial later if pan/zoom is needed. |
| 6 | [Charts View](https://community.obsidian.md/plugins/obsidian-chartsview-plugin) | 1.2.8, updated ~8 months ago; 32 releases; 90k downloads | Ant Design plots from CSV/Dataview, many chart types | Only install when notes contain quantitative datasets. Current cluster does not. |
| 7 | [Pixel Banner](https://community.obsidian.md/plugins/pexels-banner) | 3.6.18, updated ~5 months ago; 101 releases; 133k downloads | Per-note local/remote image or video banners, icon/title treatments | Skip for this cluster. A single restrained MOC cover image could work, but banners on every technical note reduce information density and add asset/frontmatter overhead. |

Additional judgment:

- Advanced Canvas adds genuine document capability: metadata-cache/backlink integration, single-node embeds, node templates and shapes, presentation mode, portals, collapsible groups, focus mode, and transparent SVG/PNG export. It is not merely cosmetic.
- For charts, prefer a portable Mermaid `xychart-beta` when the chart is simple and static. Choose Charts View only for richer interactive or Dataview-backed plots.
- Avoid installing a Mermaid theme plugin solely for color. A scoped snippet is more transparent, easier to version, and can reuse the existing 1215 tokens. Slick Mermaid becomes worthwhile when theme switching, override cleanup, or fullscreen pan/zoom becomes painful.
- Banners are appropriate for dashboards, MOCs, and publication landing pages—not routine runbooks or command-heavy notes.

## Part 2C — a consistent professional Mermaid dark theme

### Recommended layering

Use two layers, each for what it does best:

1. Mermaid configuration controls internal SVG colors and layout.
2. A scoped Obsidian CSS snippet controls the diagram container, spacing, border, typography, and minor SVG polish.

Mermaid's official theming docs say `base` is the customizable theme and colors must be hex values. Current Mermaid documentation prefers diagram frontmatter configuration; the legacy `%%{init: ...}%%` directive is still commonly supported in Obsidian builds, but the exact Mermaid version is bundled with Obsidian and can change. Test one diagram in the installed desktop app before converting the cluster.

### Per-diagram init-directive example

This is the compact form most likely to work with existing Obsidian Mermaid blocks:

```text
%%{init: {"theme":"base","themeVariables":{"darkMode":true,"background":"#1d1d1f","primaryColor":"#272729","primaryTextColor":"#f5f5f7","primaryBorderColor":"#2997ff","lineColor":"#7f8c9d","secondaryColor":"#202a36","tertiaryColor":"#252130","fontFamily":"Inter, system-ui, sans-serif","fontSize":"15px"},"flowchart":{"curve":"basis","htmlLabels":true,"nodeSpacing":32,"rankSpacing":42}}}%%
flowchart LR
    CLI["herdr CLI"] -->|prompt / wait / read| SUP["Supervisor"]
    SUP --> GLM["GLM worker"]
    SUP --> KIMI["Kimi worker"]
    SUP --> CLAUDE["Claude reviewer"]
```

For current Mermaid syntax, the equivalent forward-looking configuration is placed at the start of Mermaid source:

```yaml
---
config:
  theme: base
  themeVariables:
    darkMode: true
    background: "#1d1d1f"
    primaryColor: "#272729"
    primaryTextColor: "#f5f5f7"
    primaryBorderColor: "#2997ff"
    lineColor: "#7f8c9d"
    fontFamily: "Inter, system-ui, sans-serif"
  flowchart:
    curve: basis
    nodeSpacing: 32
    rankSpacing: 42
---
flowchart LR
  A["Input"] --> B["Worker"]
```

Source: [Mermaid theme configuration](https://mermaid.js.org/config/theming.html).

### Proposed scoped CSS snippet (do not apply yet)

Add `cssclasses: [hermes-wiki, agentic-doc]` to only these notes, then extend the existing snippet or add one narrowly scoped snippet:

```css
/* Container: stable across Mermaid's generated SVG details. */
.markdown-preview-view.agentic-doc .mermaid {
  background: #1d1d1f;
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 18px;
  margin: 1.5rem 0 2rem;
  padding: 1.25rem;
  overflow-x: auto;
}

.markdown-preview-view.agentic-doc .mermaid svg {
  display: block;
  height: auto;
  margin: 0 auto;
  max-width: 100%;
}

.markdown-preview-view.agentic-doc .mermaid .nodeLabel,
.markdown-preview-view.agentic-doc .mermaid .edgeLabel {
  font-family: Inter, system-ui, sans-serif;
}

.markdown-preview-view.agentic-doc .mermaid .edgeLabel {
  background-color: #1d1d1f !important;
  color: rgba(255, 255, 255, 0.72) !important;
}
```

Do not aggressively target every generated Mermaid class in CSS: the DOM varies across Mermaid versions and inline SVG styles can win the cascade. Put palette variables in Mermaid config; keep CSS focused on the outer presentation. Obsidian itself recommends using its CSS variables for theme-compatible styling; if the goal changes from fixed dark output to system light/dark adaptation, replace literal colors with `var(--background-primary)`, `var(--background-secondary)`, `var(--text-normal)`, `var(--text-muted)`, and `var(--interactive-accent)`.

### Diagram grammar for this cluster

- Direction: `LR` for pipelines/control flow; `TD` only for hierarchy.
- Maximum 7–9 visible nodes in an inline diagram. Split larger systems or use an Excalidraw/Canvas overview.
- Shapes: rounded rectangles for agents/processes, cylinders for stores, diamonds only for decisions, subgraphs for runtime boundaries.
- Lines: solid for commands/data flow; dotted for optional/spawned relationships; labels should be short verbs.
- Color: encode category, not decoration. Blue = orchestration, purple = model/provider, green = ready/success, amber = human decision, red = failure/destructive action.
- Typography: 14–15px labels; sentence case; no emoji inside diagrams unless it is a meaningful status symbol.

## Part 2D — concrete upgrades for `03-Resources/Agentic Terminal Stack/`

Notes reviewed:

- `Agentic Terminal Stack MOC.md`
- `Multi-Agent Orchestration Playbook.md`

Both are structurally sound and readable. The MOC has one large default Mermaid overview plus a status table. The playbook is command-heavy, has a small three-model Mermaid flowchart, and relies on headings/tables without stronger visual signposts.

### Upgrade 1 — make the MOC a genuine visual landing page

Keep the prose, but replace or restyle the “big picture” Mermaid as a clear three-tier architecture:

- control plane: Mike / Claude orchestrator / `herdr CLI`
- execution plane: persistent Herdr workspaces and panes
- model plane: Pi routing to GLM, Kimi, OpenRouter/Ollama

Add a compact legend and a one-line “reading path” callout above the note list. If the architecture stabilizes, promote this one overview to a branded Excalidraw drawing and auto-export SVG; keep detailed behavioral diagrams as Mermaid because text is easier to update. This yields a strong hero visual without turning every note into an illustration project.

### Upgrade 2 — turn playbook recipes into scannable operational cards

Use a tiny callout vocabulary, styled by the existing snippet:

- `[!example] Recipe` for the goal and command block
- `[!info] Prerequisite` for authentication/environment assumptions
- `[!warning] Guardrail` for safety rules
- `[!success] Expected result` for observable completion

Each recipe should follow the same order: intent → command → expected result → failure/cleanup note. The current Recipe 1 prerequisite comes after the code, while Recipe 5 is a dense paragraph; normalizing these will improve scan speed more than adding imagery. Callout Manager can make insertion convenient later, but is unnecessary to render this structure.

### Upgrade 3 — add one decision visual, not more decoration

Convert the “Model routing cheat-sheet” into either:

- a small Mermaid decision flow (“private?” → Ollama; “1M context?” → Kimi; “deep/main?” → Claude; otherwise GLM), or
- keep the table and add semantic row markers through CSS.

Prefer the decision flow if readers choose a route before acting; keep the table if they compare multiple attributes. Do not use both. Add status pills to the MOC status table (`ready`, `installed`, `pending`) through callout/CSS tokens rather than emoji or banners.

## Proposed implementation plan for a later change pass

1. Create one `agentic-doc` scoped snippet using the existing 1215 token palette; validate in Reading View and Live Preview under AnuPpuccin dark mode.
2. Apply the class to only the two reviewed notes, restyle their Mermaid blocks, and add the four-callout vocabulary to one playbook recipe as a pilot.
3. Build one Excalidraw template plus 6–10 reusable technical primitives; redraw only the MOC hero architecture and enable synchronized SVG export for that drawing.
4. After one week of use, decide whether Advanced Canvas solves a real navigation/presentation problem. Install no other visual plugin unless a concrete friction point remains.

This sequence is reversible, keeps the vault simple, and makes the style system prove itself on two notes before it spreads.

## Sources

- [Excalidraw for Obsidian repository and feature guide](https://github.com/zsviczian/obsidian-excalidraw-plugin)
- [Excalidraw Script Engine library](https://github.com/zsviczian/obsidian-excalidraw-plugin/tree/master/ea-scripts)
- [Excalidraw Libraries](https://libraries.excalidraw.com/)
- [Mermaid theme configuration](https://mermaid.js.org/config/theming.html)
- [Obsidian developer documentation: CSS variables and styling](https://docs.obsidian.md/Reference/CSS%20variables/About%20styling)
- [Advanced Canvas community listing](https://community.obsidian.md/plugins/advanced-canvas)
- [Callout Manager community listing](https://community.obsidian.md/plugins/callout-manager)
- [Slick Mermaid community listing](https://community.obsidian.md/plugins/slick-mermaid)
- [Charts View community listing](https://community.obsidian.md/plugins/obsidian-chartsview-plugin)
- [Pixel Banner community listing](https://community.obsidian.md/plugins/pexels-banner)
