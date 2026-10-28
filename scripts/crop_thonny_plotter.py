"""Split the Obstacle avoiding Thonny drawing (Step 1) into two panels: the View menu, and the plot.

Rebuilt from the original Docs drawing in assets/avoiding-obstacles/thonny-plotter-src/ (SVG + native
screenshot, from scripts/gdocs/), so it can be re-run if a better source turns up. Each panel is the same
SVG with its viewBox narrowed, then rendered with scripts/gdocs/render_svg.py. Idempotent.

usage: uv run --with playwright python scripts/crop_thonny_plotter.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gdocs"))
from render_svg import main as render  # noqa: E402

from worksheets.config import ASSETS  # noqa: E402

SRC = ASSETS / "avoiding-obstacles"
UNITS_PER_INCH = 1000  # the ODT-derived SVGs are in 1/1000 inch

# (output name, x, y, width, height) in the drawing's units
PANELS = [
    ("thonny-plotter-menu", 0, 0, 3640, 2335),      # View menu + the editor, callouts 1 and 2
    ("thonny-plotter-plot", 3380, 1950, 3313, 1703),  # plot only (the shell numbers are cut by the menu edge), callout 3
]


# Arrows match the Following lines figures (compose_thonny_panels.py): a thin black line and a small head, not the
# Docs drawing's thick pink highlighter stroke. Widths are in drawing units, where one source pixel is ~3.5 units.
ARROW_WIDTH = 11
ARROW_COLOUR = "#000"
ARROW_HEAD = 7  # head size, in stroke widths (as in compose_thonny_panels.py)


def restyle_arrows(svg_text):
    svg_text = re.sub(r'(<line [^>]*?)stroke="#[0-9a-f]+" stroke-width="[\d.]+"',
                      rf'\1stroke="{ARROW_COLOUR}" stroke-width="{ARROW_WIDTH}"', svg_text)
    head = (f'<marker id="head42" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{ARROW_HEAD}" '
            f'markerHeight="{ARROW_HEAD}" orient="auto"><path d="M0 0L10 5L0 10z"/></marker>')
    return re.sub(r'<marker id="head42".*?</marker>', head, svg_text, flags=re.S)


CENTRE_OF_TEXT = 0.36  # x-height centre above the baseline, in font sizes
ABOVE_TAIL_GAP = 70  # for a label above its arrow: baseline-to-tail distance, in drawing units

LABEL_AND_ARROW = re.compile(
    r'<text x="(?P<tx>[\d.]+)" y="(?P<ty>[\d.]+)" font-size="(?P<fs>[\d.]+)"(?P<text_rest>[^>]*>[^<]*</text>\s*)'
    r'<line x1="(?P<x1>[\d.]+)" y1="(?P<y1>[\d.]+)"(?P<line_rest>[^>]*>)')


def align_labels(svg_text):
    """Seat each arrow's tail on its label. A label to the right of the tail is centred on it vertically (the tail
    moves to the text's centre); a label above the tail comes down to just above it. The tip is not touched."""
    def fix(m):
        tx, ty, fs, x1, y1 = (float(m[k]) for k in ("tx", "ty", "fs", "x1", "y1"))
        if x1 < tx:
            y1 = ty - CENTRE_OF_TEXT * fs
        else:
            ty = y1 - ABOVE_TAIL_GAP
        return (f'<text x="{m["tx"]}" y="{ty:.1f}" font-size="{m["fs"]}"{m["text_rest"]}'
                f'<line x1="{m["x1"]}" y1="{y1:.1f}"{m["line_rest"]}')
    return LABEL_AND_ARROW.sub(fix, svg_text)


def crop(svg_text, x, y, w, h):
    svg_text = re.sub(r'viewBox="[^"]*"', f'viewBox="{x} {y} {w} {h}"', svg_text, count=1)
    svg_text = re.sub(r'width="[\d.]+in"', f'width="{w / UNITS_PER_INCH:.4f}in"', svg_text, count=1)
    return re.sub(r'height="[\d.]+in"', f'height="{h / UNITS_PER_INCH:.4f}in"', svg_text, count=1)


def main():
    src_dir = SRC / "thonny-plotter-src"
    svg_text = align_labels(restyle_arrows((src_dir / "drawing.svg").read_text()))
    for name, x, y, w, h in PANELS:
        cropped = src_dir / f"{name}.svg"  # beside the picture so its relative link resolves
        cropped.write_text(crop(svg_text, x, y, w, h))
        render(cropped, SRC / f"{name}.png")
        cropped.unlink()


if __name__ == "__main__":
    main()
