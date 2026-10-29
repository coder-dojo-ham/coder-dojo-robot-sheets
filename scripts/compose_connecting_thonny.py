"""Build the figures for the Connecting Thonny sheet from its Google Doc's drawings.

usage:
  uv run --with playwright --with potracer python scripts/compose_connecting_thonny.py            # render from the committed sources
  uv run --with playwright --with potracer python scripts/compose_connecting_thonny.py stage <odt-dir> <drawings-dir>
                                                                                      # refresh sources from scripts/gdocs/ output

The sources are assets/connecting-thonny/src/: one drawing-NN.svg per Docs drawing (labels, arrows, dashed outlines as
vectors) plus the original pictures in src/pictures/, shared between drawings. Rendering rewrites each svg's
picture links, optionally crops its canvas, and writes the figure PNG beside src/. The robot stand line drawing is a
raster in the doc, so it is traced to a vector first. Idempotent: always rebuilt from src/.
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent / "gdocs"))  # render_svg and its browser helper live there
from render_svg import main as render  # noqa: E402

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "connecting-thonny"
SRC, PICTURES = ASSETS / "src", ASSETS / "src" / "pictures"
FONT = Path(__file__).resolve().parent.parent / "fonts" / "Arimo-Regular.ttf"
PPI = 192  # 2x CSS pixels; the labels and outlines gain from it, the screenshots just upsample
U = 1000  # drawing units per inch (see odt_drawings.py)

# figure -> (drawing number, crop viewBox (x, y, w, h) in drawing units or None for the whole canvas)
FIGURES = {
    "thonny-window-labelled": (1, None),
    "robot-stand": (2, None),
    "robot-on-stand": (3, None),
    "usb-power": (4, None),
    "thonny-click-here": (5, None),
    "thonny-pick-interpreter": (6, (0, 6250, 5930.3, 3489)),  # drops the blank canvas above the label
    "thonny-connected": (7, (0, 0, 2922.4, 3009.8)),  # the window only; its output snippets are code blocks in the sheet
}
# figures shown larger than the doc had them: shrink their label text by the same factor so captions keep their size
LABEL_SHRINK = {"thonny-connected": 64 / 84}  # printed 64mm in the doc's layout, 84mm in the sheet
# picture that is a plain-black line drawing, traced to a vector (picture name -> trace threshold)
TRACED = {"100002010000058F000004790E84FCF353565544.png": 140}
# pictures outside any drawing, copied as-is: ODT picture -> asset name (hero images are downsized)
FLAT = {"1000020100000112": "thonny-view-menu.png"}
# the simple-mode toolbar picture, kept as a source; the figure adds a red outline round its "Switch to regular mode" link
BANNER = "10000201000004390000006A1E411A1F9538F4DB.png"
BANNER_SIZE, BANNER_LINK = (1081, 106), (1004, 16, 1088, 88)  # picture px; outline box x0, y0, x1, y1 (runs past the edge)
BANNER_MARGIN = 14  # canvas added at the right so the outline is not cut off; the picture's last pixel column is stretched into it
# the doc crops some plain pictures (fo:clip); keep the same box (left, top, right, bottom) in source pixels
CROPS = {"thonny-view-menu.png": (0, 0, 274, 322)}  # View menu: the doc hides everything below Shell
HEROES = {"10000201000006790000": "hero-thonny.png", "100000000000070300000800": "hero-robot.jpg"}
HERO_MAX = 1200


def stage(odt_dir, drawings_dir):
    """Copy the converter's output into src/: pictures once, drawing svgs pointing at them."""
    odt_dir, drawings_dir = Path(odt_dir), Path(drawings_dir)
    PICTURES.mkdir(parents=True, exist_ok=True)
    shutil.copy(odt_dir / "Pictures" / BANNER, PICTURES / BANNER)
    for pic in (odt_dir / "Pictures").iterdir():
        for prefix, name in {**FLAT, **HEROES}.items():
            if pic.name.startswith(prefix):
                save_flat(pic, name)
    for number in {n for n, _ in FIGURES.values()}:
        svg = (drawings_dir / f"drawing-{number:02d}" / "drawing.svg").read_text()
        for pic in re.findall(r'href="([^"#]+\.(?:png|jpg))"', svg):  # keep only what a drawing places
            shutil.copy(odt_dir / "Pictures" / pic, PICTURES / pic)
        svg = re.sub(r"<style>.*?</style>", "", svg)  # the font link is machine-specific; render adds it back
        svg = re.sub(r'href="([^"#]+\.(?:png|jpg))"', r'href="pictures/\1"', svg)
        (SRC / f"drawing-{number:02d}.svg").write_text(svg)
        print("staged", f"drawing-{number:02d}.svg")


def save_flat(pic, name):
    """Copy a plain picture to its asset name; hero images are shrunk to a sensible print size."""
    if name in CROPS:
        with Image.open(pic) as im:
            im.crop(CROPS[name]).save(ASSETS / name)
        return
    if not pic.name.startswith(tuple(HEROES)):
        shutil.copy(pic, ASSETS / name)
        return
    with Image.open(pic) as im:
        im.thumbnail((HERO_MAX, HERO_MAX))
        if name.endswith(".jpg"):
            im = im.convert("RGB")
        im.save(ASSETS / name, quality=90)


def trace(png, dest, threshold):
    """Trace a black-on-white raster into a single-path svg beside `dest`."""
    import numpy as np
    import potrace

    with Image.open(png) as im:
        rgba = im.convert("RGBA")
    flat = Image.new("RGBA", rgba.size, "white")
    flat.alpha_composite(rgba)
    curves = potrace.Bitmap(np.array(flat.convert("L")) >= threshold).trace(turdsize=20, alphamax=1.0, opttolerance=0.4)
    paths = []
    for curve in curves:
        d = [f"M{curve.start_point.x:.1f},{curve.start_point.y:.1f}"]
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f},{seg.c.y:.1f}L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        paths.append("".join(d) + "Z")
    w, h = rgba.size
    dest.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
                    f'<path fill="#000" fill-rule="evenodd" d="{" ".join(paths)}"/></svg>')


def crop(svg, box):
    """Narrow the canvas to `box` (x, y, w, h) in drawing units."""
    x, y, w, h = box
    svg = re.sub(r'viewBox="[^"]*"', f'viewBox="{x} {y} {w} {h}"', svg, count=1)
    svg = re.sub(r'width="[\d.]+in" height="[\d.]+in"', f'width="{w / U:.4f}in" height="{h / U:.4f}in"', svg, count=1)
    return svg


def banner_svg():
    """The simple-mode toolbar with a dashed red outline round the link to click (picture px, 96 per inch)."""
    w, h = BANNER_SIZE
    x0, y0, x1, y1 = BANNER_LINK
    total = w + BANNER_MARGIN
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total} {h}" width="{total / 96}in" height="{h / 96}in">'
            f'<svg x="{w}" width="{BANNER_MARGIN}" height="{h}" viewBox="{w - 1} 0 1 {h}" preserveAspectRatio="none">'
            f'<image href="pictures/{BANNER}" width="{w}" height="{h}"/></svg>'
            f'<image href="pictures/{BANNER}" width="{w}" height="{h}"/>'
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="6" fill="none" stroke="#ff0000" '
            'stroke-width="4" stroke-dasharray="14 10"/></svg>')


def shrink_labels(svg, factor):
    """Scale every label's font size and line step (the leaders and pictures stay put)."""
    return re.sub(r'(font-size|dy)="([\d.]+)"', lambda m: f'{m.group(1)}="{float(m.group(2)) * factor:.1f}"', svg)


def figure(name, svg, box, work):
    for pic, threshold in TRACED.items():
        if pic in svg:
            traced = work / (Path(pic).stem + ".svg")
            trace(PICTURES / pic, traced, threshold)
            svg = svg.replace(f"pictures/{pic}", traced.as_uri())
    svg = svg.replace('href="pictures/', f'href="{PICTURES.as_uri()}/')
    svg = svg.replace("<defs>", f'<style>@font-face {{ font-family: Arimo; src: url("{FONT.as_uri()}"); }}</style><defs>', 1)
    if name in LABEL_SHRINK:
        svg = shrink_labels(svg, LABEL_SHRINK[name])
    if box:
        svg = crop(svg, box)
    page = work / f"{name}.svg"
    page.write_text(svg)
    render(page, ASSETS / f"{name}.png", PPI)
    print("wrote", ASSETS / f"{name}.png")


def main(*args):
    if args and args[0] == "stage":
        stage(*args[1:3])
    with tempfile.TemporaryDirectory() as tmp:
        figure("thonny-regular-mode", banner_svg(), None, Path(tmp))
        for name, (number, box) in FIGURES.items():
            figure(name, (SRC / f"drawing-{number:02d}.svg").read_text(), box, Path(tmp))


if __name__ == "__main__":
    main(*sys.argv[1:])
