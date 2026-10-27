"""Compose the two Following lines Step 4 panels from the original Thonny screenshots.

usage: uv run --with playwright python scripts/compose_thonny_panels.py <assets/following-lines dir>

Reads thonny-files-src/{thonny-window,context-menu}.png (the originals, as extracted from the Google Doc
drawing by scripts/gdocs/), writes thonny-files-left.png and thonny-files-right.png beside them, plus the
.svg of each. Crops are in source pixels. Labels, arrows and outlines are drawn as vectors, so they stay
crisp at any size. Idempotent: always rebuilt from the originals.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gdocs"))  # render_svg and its browser helper live there
from render_svg import main as render  # noqa: E402

SCALE = 2  # output pixels per source pixel; the vectors gain from it, the screenshots just upsample
CSS_DPI = 96

WINDOW, WINDOW_SIZE = "thonny-files-src/thonny-window.png", (1256, 1292)
MENU, MENU_SIZE = "thonny-files-src/context-menu.png", (458, 450)

# Thonny window: x range kept (both file panels plus the left of the editor and Shell, for context) and the two
# row bands. The blank part of the left column between the upper list and the lower panel header is dropped
# ("cut and shut") so the lists stay full size. The join is deliberately not marked: both halves are blank at the
# seam, and the reader doesn't need to know the window was shortened.
PANEL_X = (4, 520)
UPPER_ROWS = (152, 492)
LOWER_ROWS = (742, 1258)  # starts above the Shell tab so its first lines stay in view
PANEL_W = PANEL_X[1] - PANEL_X[0]
LABEL_X = PANEL_W + 30  # labels sit right of the window
LABEL_PX = 32
LABELS = (("Files on your computer", 349), ("Files on the robot", 1107))  # source rows the arrows point at
ARROW_TIP_X = 262

MENU_CROP = (0, 0, 447, 438)  # drops the stray scraps of the window at the right and bottom edges

# Context menu: red outlines (x0, y0, x1, y1) round the two items to use, in source pixels.
MENU_OUTLINES = ((196, 164, 302, 193), (196, 337, 276, 366))
RED = "#e00000"
FONT = (Path(__file__).parent.parent / "fonts" / "Arimo-Regular.ttf").as_uri()  # the sheet's own body font


def header(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h}" width="{w / CSS_DPI}in" height="{h / CSS_DPI}in">'
            f'<style>@font-face {{ font-family: Arimo; src: url("{FONT}"); }}</style>'
            '<defs><marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto"><path d="M0 0L10 5L0 10z"/></marker></defs>'
            f'<rect width="{w}" height="{h}" fill="#fff"/>')


def crop(href, size, src, dest):
    """Place the `src` box (x0, y0, x1, y1) of the `size` (w, h) picture at `dest` (x, y) at 1:1."""
    x0, y0, x1, y1 = src
    dx, dy = dest
    return (f'<svg x="{dx}" y="{dy}" width="{x1 - x0}" height="{y1 - y0}" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">'
            f'<image href="{href}" width="{size[0]}" height="{size[1]}"/></svg>')


def row(src_y):
    """Where a source row of the Thonny window lands in the stitched figure."""
    upper_h = UPPER_ROWS[1] - UPPER_ROWS[0]
    return src_y - UPPER_ROWS[0] if src_y < UPPER_ROWS[1] else upper_h + src_y - LOWER_ROWS[0]


def left_panel():
    px0, px1 = PANEL_X
    upper_h = UPPER_ROWS[1] - UPPER_ROWS[0]
    lower_h = LOWER_ROWS[1] - LOWER_ROWS[0]
    width, height = LABEL_X + 350, upper_h + lower_h
    parts = [header(width, height),
             crop(WINDOW, WINDOW_SIZE, (px0, UPPER_ROWS[0], px1, UPPER_ROWS[1]), (0, 0)),
             crop(WINDOW, WINDOW_SIZE, (px0, LOWER_ROWS[0], px1, LOWER_ROWS[1]), (0, upper_h))]
    for text, src_y in LABELS:
        y = row(src_y)
        parts.append(f'<text x="{LABEL_X}" y="{y + LABEL_PX / 3}" font-size="{LABEL_PX}" '
                     f'font-family="Arimo, Arial, sans-serif">{text}</text>')
        parts.append(f'<line x1="{LABEL_X - 10}" y1="{y}" x2="{ARROW_TIP_X}" y2="{y}" stroke="#000" '
                     'stroke-width="3" marker-end="url(#head)"/>')
    parts.append("</svg>")
    return "".join(parts), width, height


def right_panel():
    width, height = MENU_CROP[2], MENU_CROP[3]
    parts = [header(width, height), crop(MENU, MENU_SIZE, MENU_CROP, (0, 0))]
    for x0, y0, x1, y1 in MENU_OUTLINES:
        parts.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="6" fill="none" '
                     f'stroke="{RED}" stroke-width="3"/>')
    parts.append("</svg>")
    return "".join(parts), width, height


def write(folder, name, svg):
    path = folder / f"{name}.svg"
    path.write_text(svg)
    render(path, folder / f"{name}.png", CSS_DPI * SCALE)


def main(folder):
    folder = Path(folder)
    for name, build in (("thonny-files-left", left_panel), ("thonny-files-right", right_panel)):
        svg, _, _ = build()
        write(folder, name, svg)
        print("wrote", folder / f"{name}.png")


if __name__ == "__main__":
    main(sys.argv[1])
