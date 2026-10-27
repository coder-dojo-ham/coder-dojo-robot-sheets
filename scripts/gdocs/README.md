# Google Docs drawings -> SVG + original pictures

Docs drawings are not exportable as layers from the doc itself (the editor renders on a canvas, the Docs API
exposes no drawing content, and HTML/docx exports flatten them to one PNG). The **ODT export** keeps them as
layers: native-resolution pictures + vector shapes + text. These scripts turn that into SVG.

```bash
# once: sign in by hand in the window that opens (profile lives in ~/.cache/gdocs-export-profile, outside git)
uv run --with playwright python scripts/gdocs/login.py <doc-url>

# per doc
uv run --with playwright python scripts/gdocs/fetch_odt.py <doc-url> /tmp/doc-odt
uv run python scripts/gdocs/odt_drawings.py /tmp/doc-odt /tmp/doc-drawings      # drawing-NN/drawing.svg + pictures
uv run --with playwright python scripts/gdocs/render_svg.py /tmp/doc-drawings/drawing-01/drawing.svg out.png [ppi]
```

Each `draw:g` group in the ODT is one drawing. Known limits:

- Shapes handled: text boxes, straight arrows, rectangle/rounded-rectangle outlines. Anything else is reported on stderr.
- Label font size is a heuristic (see `label_fit`): the ODT keeps the unscaled size, so labels are shrunk to fit their boxes.
- Picture crops (`fo:clip`) are read as inches at 96 dpi against the picture's natural size (verified on the Step 4 drawing).
- Pictures that are *not* inside a drawing group are plain images; take them straight from the ODT `Pictures/`.

## Surveyed 2026-10-27 (all five other sheet docs)

| Doc | Drawings | Notes |
|---|---|---|
| Robots - line follow (`1h-EPddi...`) | 1 | Step 4 Thonny panels -> `scripts/compose_thonny_panels.py` |
| Getting started (`1W--JNVv...`) | 7 | Thonny screenshots at 1256x1292 / 1650x1668 (best source of crisp panels); shapes: freeform ("non-primitive") + rounded rects not yet converted |
| Make it drive (`1Cuq-YQTU...`) | 9 | mostly vector-only diagrams (square path, arrows, flowchart shapes) - many unconverted shapes |
| Button (`131hjjhB...`) | 6 | small pictures + labels + one curved connector (unconverted) |
| LED (`1tN4cISq...`) | 2 | one right-arrow shape unconverted |
| Obstacle avoiding (`1PLxNShtf...`) | 7 | arcs, cans, curved connectors unconverted; one 1920x1044 picture |

Unconverted shape types are listed on stderr by `odt_drawings.py` (`ooxml-upArrow`, `-bentArrow`, `-uturnArrow`,
`-rightArrow`, `-arc`, `-can`, `-flowChartDisplay`, `-curvedConnector3`, `-non-primitive`, plus filled rects/roundRects).
Add a handler in `shape_svg` when a drawing needs one.
