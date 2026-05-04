# Diagram Recipes (Graphviz)

Two Graphviz `dot` recipes consumed by `render_diagram.py`.

## Open-Question bindings (decisions.md 2026-05-04T14:50Z)

- **OQ2 — graceful degrade**: If `dot` is not on PATH, the script
  prints OS-specific install instructions and **exits 0** with a
  `<out>.skipped.json` sentinel rather than failing the deck. The
  `@deck-builder` reads the sentinel, marks the asset as
  `skipped: true` in `qa-report.json`, and proceeds. Diagram-class
  visuals are non-essential in v1 — better to ship a deck without
  the flow diagram than to block on an absent `dot` binary.
- **OQ3 — SVG**: `dot -Tsvg` is native; pass `--svg` to emit
  `<out>.svg` alongside the PNG.

## Install hints (printed on graceful degrade)

| OS | Command |
|----|---------|
| Windows | `winget install Graphviz` (or download from https://graphviz.org/download/) |
| macOS   | `brew install graphviz` |
| Linux (Debian/Ubuntu) | `apt install graphviz` |
| Linux (Fedora/RHEL)   | `dnf install graphviz` |

After install, ensure `dot` is on PATH (Windows: usually
`C:\Program Files\Graphviz\bin`).

## Recipes

### `flow_diagram`

Left-to-right directed flow. Nodes are filled rounded rectangles in
`primary_accent`; the optional focal node is in `secondary_accent`.

Spec:

```json
{
  "nodes": [
    {"id": "draft", "label": "Draft"},
    {"id": "review", "label": "Review"},
    {"id": "approve", "label": "Approve", "focal": true},
    {"id": "deploy", "label": "Deploy"}
  ],
  "edges": [
    ["draft", "review", "1d"],
    ["review", "approve", "2d"],
    ["approve", "deploy", "same day"]
  ]
}
```

Edge tuples are `[from, to]` or `[from, to, label]`. Edges may also
be `{"from": "...", "to": "...", "label": "..."}`.

### `system_diagram`

Top-to-bottom labelled boxes for architecture / system overviews.
Boxes are filled `background_light` with `primary_accent` outline;
focal box is filled `secondary_accent` with `text_on_dark` text.

Spec:

```json
{
  "boxes": [
    {"id": "client", "label": "Client (web)"},
    {"id": "api", "label": "API gateway", "focal": true},
    {"id": "svc-a", "label": "Service A"},
    {"id": "svc-b", "label": "Service B"},
    {"id": "db", "label": "PostgreSQL"}
  ],
  "edges": [
    ["client", "api"],
    ["api", "svc-a"],
    ["api", "svc-b"],
    ["svc-a", "db"],
    ["svc-b", "db"]
  ]
}
```

## Sizing

Graphviz `size` is in inches. `render_diagram.py` divides the
`--size` PX-pair by 96 dpi to get the inch dimensions and passes
them to `dot` with the `!` suffix to force fit.

## Determinism

Graphviz `dot` is deterministic given the same input graph. There
may be cosmetic glyph drift across system fonts; we use
`fontname="Helvetica"` and rely on `dot`'s built-in font resolver.

## Failure modes

| Mode | Symptom | Mitigation |
|------|---------|------------|
| `graphviz` Python binding not installed | `pip install graphviz` fails (rare; permissions) | Sentinel + skip per OQ2 |
| `dot` binary not on PATH | `shutil.which("dot")` returns None | Sentinel + skip per OQ2 + install hint to stderr |
| Bad spec (no `nodes` / no `edges`) | recipe raises | Exit 2 with stderr error (proper failure — bad input is a builder bug, not an environment issue) |
| `dot` produces malformed PNG | `pipe(format="png")` raises | Exit 2 with stderr — environment is broken, escalate |
