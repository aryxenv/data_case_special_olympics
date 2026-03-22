---
name: visuals
description: Enforces Excalidraw as the sole diagramming tool. Defines the folder structure, dark-mode export workflow, naming conventions, and README embedding rules for all project diagrams.
---

# Visuals — Excalidraw Diagrams

## Golden Rule

**All diagrams in this project MUST be created with Excalidraw.** No other diagramming tools (draw.io, Mermaid, Lucidchart, etc.) are permitted.

## Folder Structure

```
excalidraw/
  diagrams/
    excalidraw/          ← Source .excalidraw JSON files (editable)
      etl-pipeline.excalidraw
      star-schema.excalidraw
    export/              ← Exported dark-mode PNGs (generated from sources)
      etl-pipeline.png
      star-schema.png
  scripts/
    export-excalidraw.js ← Export script (Kroki + resvg)
  node_modules/          ← npm dependencies
  package.json
```

- **`excalidraw/diagrams/excalidraw/`** — Stores the raw `.excalidraw` JSON files. These are the source of truth.
- **`excalidraw/diagrams/export/`** — Stores the rendered PNG images. These are **generated artifacts** — always re-export from the `.excalidraw` source, never edit PNGs directly.

## Naming Conventions

- Use **flat, descriptive kebab-case** names — no subfolders.
- The `.excalidraw` and `.png` filenames must match exactly (minus extension).
- Names should clearly describe the diagram content.

### Examples

```
etl-pipeline.excalidraw    → etl-pipeline.png
star-schema.excalidraw     → star-schema.png
data-flow.excalidraw       → data-flow.png
architecture.excalidraw    → architecture.png
```

## Creating a Diagram

### Step 1 — Design with `excalidraw-create_view`

Use the Excalidraw MCP tool to design the diagram interactively:

```
excalidraw-create_view  →  renders the diagram inline
```

- Use the **dark-friendly color palette** (light-colored fills on dark backgrounds).
- Use light stroke colors (`#e0e0e0` or similar) — never use `#1e1e1e` strokes on a dark background.
- Recommended fill colors: `#a5d8ff` (blue), `#b2f2bb` (green), `#d0bfff` (purple), `#ffd8a8` (orange), `#ffc9c9` (red), `#fff3bf` (yellow).

### Step 2 — Save the `.excalidraw` source file

Save the Excalidraw JSON to `excalidraw/diagrams/excalidraw/<name>.excalidraw`.

The file must include dark theme settings in `appState`:

```json
{
  "type": "excalidraw",
  "version": 2,
  "elements": [ ... ],
  "appState": {
    "theme": "dark",
    "viewBackgroundColor": "#000000"
  }
}
```

**Important:** Always save the `.excalidraw` file **before** exporting. The source file is the single source of truth.

### Step 3 — Export to dark-mode PNG

Run the export script from the project root:

```bash
node excalidraw/scripts/export-excalidraw.js excalidraw/diagrams/excalidraw/<name>.excalidraw
```

This automatically:
1. Reads the `.excalidraw` JSON
2. Forces dark theme + `#000000` background
3. **Auto-fixes dark standalone text** — any title/annotation text (not inside a shape) with a dark `strokeColor` is rewritten to `#e0e0e0` so it remains visible. Container text stays black (readable on colored fills).
4. Sends it to Kroki.io to render SVG
5. Converts SVG → PNG at 1600px width using `@resvg/resvg-js`
6. Saves the PNG to `excalidraw/diagrams/export/<name>.png`

> **Note:** The auto-fix only applies to standalone text during export — container text and the source `.excalidraw` file are not modified.

You can also specify a custom output path:

```bash
node excalidraw/scripts/export-excalidraw.js excalidraw/diagrams/excalidraw/etl-pipeline.excalidraw excalidraw/diagrams/export/etl-pipeline.png
```

### Step 4 — Upload to Excalidraw.com

Use `excalidraw-export_to_excalidraw` to get a shareable link:

```
excalidraw-export_to_excalidraw  →  returns https://excalidraw.com/#json=...
```

Save this link — it is used in the README alongside the inline image.

## Embedding in the README

Every diagram in the README must have **both** an inline image and an Excalidraw.com link:

```markdown
### ETL Pipeline

![ETL Pipeline](excalidraw/diagrams/export/etl-pipeline.png)

[📝 Edit on Excalidraw](https://excalidraw.com/#json=XXXXX)
```

- The inline image uses a relative path to the PNG in `excalidraw/diagrams/export/`.
- The Excalidraw link lets anyone open and edit the diagram in their browser.
- Always include a descriptive alt-text for the image.

## Updating an Existing Diagram

1. Edit the `.excalidraw` source in `excalidraw/diagrams/excalidraw/`.
2. Re-run the export script to regenerate the PNG.
3. Re-upload to Excalidraw.com to get a fresh link.
4. Update the Excalidraw.com link in the README if it changed.

**Never** edit the PNG directly — always go through the `.excalidraw` source.

## Dark Mode Design Guidelines

All diagrams must look good on a pitch-black background (`#000000`):

- **Text inside shapes:** Use black/dark text (`#1e1e1e`, `#000000`). It reads well on the pastel fills.
- **Standalone text** (titles, annotations not inside a shape): Use light colors (`#e0e0e0`). The export script auto-fixes dark standalone text.
- **Strokes:** Use light colors (`#e0e0e0`, `#c0c0c0`) for shape borders and arrows so they're visible.
- **Fills:** Use the pastel Excalidraw palette — they contrast well on black backgrounds.
- **Arrows:** Use light strokes (`#e0e0e0`) with visible arrowheads.

## Export Dependencies

The export pipeline requires Node.js and the `@resvg/resvg-js` package:

```bash
cd excalidraw && npm install    # installs @resvg/resvg-js from package.json
```

The export script also calls **Kroki.io** (free, public API) to render Excalidraw → SVG. Internet access is required during export.

## What NOT to Do

- ❌ Use Mermaid, draw.io, or any other diagramming tool
- ❌ Edit PNG files directly
- ❌ Save `.excalidraw` files outside of `excalidraw/diagrams/excalidraw/`
- ❌ Use dark strokes on a dark background
- ❌ Export without dark theme enabled
- ❌ Embed diagrams in the README without both the image and the Excalidraw.com link
- ❌ Forget to re-export the PNG after editing the `.excalidraw` source
