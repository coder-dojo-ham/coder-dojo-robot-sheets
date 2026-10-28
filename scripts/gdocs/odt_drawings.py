"""Turn each Google Docs drawing (an ODT draw:g group) into an SVG plus its original pictures.

usage: uv run python scripts/gdocs/odt_drawings.py <unpacked-odt-dir> <out-dir>

Per drawing, out-dir/drawing-NN/ gets drawing.svg (pictures linked relatively, shapes and text as
vectors) and the picture files at their native resolution. Units in the SVG are 1/1000 inch.
Shapes understood: text boxes (ooxml-rect), arrows (mso-spt32), outlines (ooxml-roundRect/rect).
Unknown shapes are reported, not guessed. Idempotent: out-dir is rebuilt each run.
"""
import re
import shutil
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

NS = {
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}
U = 1000  # SVG user units per inch
DPI = 96  # ODF measures fo:clip against the picture's natural size at this density


def q(tag):
    prefix, name = tag.split(":")
    return f"{{{NS[prefix]}}}{name}"


def inches(value):
    return float(value.removesuffix("in")) * U if value else 0.0


def points(value):
    return float(value.removesuffix("pt")) / 72 * U


def load_styles(root):
    """name -> merged graphic/text properties from the automatic styles."""
    styles = {}
    for st in root.iter(q("style:style")):
        props = {}
        for kind in ("style:graphic-properties", "style:text-properties"):
            for el in st.iter(q(kind)):
                props.update({k.split("}")[1]: v for k, v in el.attrib.items()})
        styles[st.get(q("style:name"))] = props
    return styles


class Box:
    def __init__(self, el):
        self.x = inches(el.get(q("svg:x")))
        self.y = inches(el.get(q("svg:y")))
        self.w = inches(el.get(q("svg:width")))
        self.h = inches(el.get(q("svg:height")))


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def clip_of(props):
    """fo:clip="rect(top, right, bottom, left)" in inches -> (top, right, bottom, left) in user units."""
    m = re.match(r"rect\((.*)\)", props.get("clip", ""))
    return tuple(inches(v.strip()) for v in m.group(1).split(",")) if m else (0, 0, 0, 0)


def picture(frame, box, props, odt_dir, out_dir, n):
    """Place the picture so its un-cropped part fills the frame; a clipPath hides the rest."""
    href = frame.find(q("draw:image")).get(q("xlink:href"))
    name = Path(href).name
    shutil.copy(odt_dir / href, out_dir / name)
    with Image.open(odt_dir / href) as im:
        nat_w, nat_h = im.width / DPI * U, im.height / DPI * U
    top, right, bottom, left = clip_of(props)
    scale = box.w / (nat_w - left - right)
    x, y = box.x - left * scale, box.y - top * scale
    return (f'<clipPath id="clip{n}"><rect x="{num(box.x)}" y="{num(box.y)}" width="{num(box.w)}" height="{num(box.h)}"/></clipPath>'
            f'<image href="{name}" x="{num(x)}" y="{num(y)}" width="{num(nat_w * scale)}" height="{num(nat_h * scale)}" '
            f'clip-path="url(#clip{n})"/>')


HEADS = {}  # arrowhead marker id -> size in user units, one per stroke width


def arrowhead(sw):
    """Marker id for an arrowhead on a stroke `sw` wide. Thin strokes keep the classic 8x width; thick ones
    are capped, because 8x a fat highlighter-style line is comically large."""
    size = min(8 * sw, max(3 * sw, 80))
    marker_id = f"head{round(sw)}"
    HEADS[marker_id] = size
    return marker_id


def arrow(shape, box, props):
    geom = shape.find(q("draw:enhanced-geometry"))
    flip = geom.get(q("draw:mirror-horizontal")) == "true"
    x1, x2 = (box.x + box.w, box.x) if flip else (box.x, box.x + box.w)
    stroke = props.get("stroke-color", "#000000")
    sw = inches(props.get("stroke-width", "0.01in"))
    return (f'<line x1="{num(x1)}" y1="{num(box.y)}" x2="{num(x2)}" y2="{num(box.y + box.h)}" stroke="{stroke}" '
            f'stroke-width="{num(sw)}" marker-end="url(#{arrowhead(sw)})"/>')


def outline(box, props):
    stroke = props.get("stroke-color", "#000000")
    sw = inches(props.get("stroke-width", "0.01in"))
    return (f'<rect x="{num(box.x)}" y="{num(box.y)}" width="{num(box.w)}" height="{num(box.h)}" rx="{num(min(box.w, box.h) / 6)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{num(sw)}"/>')


def label_text(shape):
    return "".join(shape.find(q("text:p")).itertext())


def label_size(shape, styles):
    span = next(shape.iter(q("text:span")), None)
    tprops = styles.get(span.get(q("text:style-name")), {}) if span is not None else {}
    return points(tprops.get("font-size", "11pt")), tprops.get("color", "#000000")


def label_fit(group, styles):
    """The ODT keeps the drawing's un-scaled text size but the box is already scaled down, so 14pt text
    overflows its own box. Shrink every label in a drawing by one common factor until each fits.
    Heuristic: an average Arial glyph is ~0.45 em wide."""
    fit = 1.0
    for shape in group.iter(q("draw:custom-shape")):
        text = label_text(shape) if shape.find(q("text:p")) is not None else ""
        if not text.strip():
            continue
        props = styles.get(shape.get(q("draw:style-name")), {})
        inner = Box(shape).w - 2 * inches(props.get("padding-left", "0.1in"))
        fit = min(fit, inner / (len(text) * 0.45) / label_size(shape, styles)[0])
    return fit


def label(shape, box, props, styles, fit):
    size, color = label_size(shape, styles)
    size *= fit
    pad = inches(props.get("padding-top", "0.1in"))
    return (f'<text x="{num(box.x + pad)}" y="{num(box.y + pad + size)}" font-size="{num(size)}" '
            f'font-family="Arial, sans-serif" fill="{color}">{label_text(shape)}</text>')


def shape_svg(shape, box, styles, fit):
    props = styles.get(shape.get(q("draw:style-name")), {})
    kind = shape.find(q("draw:enhanced-geometry")).get(q("draw:type"))
    if kind == "mso-spt32":
        return arrow(shape, box, props)
    if kind in ("ooxml-roundRect", "ooxml-rect") and props.get("stroke") == "solid":
        return outline(box, props)
    if kind == "ooxml-rect" and "".join(shape.itertext()).strip():
        return label(shape, box, props, styles, fit)
    print("skipped unknown shape:", kind, shape.get(q("draw:name")), file=sys.stderr)
    return ""


def drawing_svg(group, styles, odt_dir, out_dir):
    HEADS.clear()  # markers are per drawing
    parts, right, bottom = [], 0.0, 0.0
    fit = label_fit(group, styles)
    for el in group:
        box = Box(el)
        right, bottom = max(right, box.x + box.w), max(bottom, box.y + box.h)
        if el.tag == q("draw:frame"):
            props = styles.get(el.get(q("draw:style-name")), {})
            parts.append(picture(el, box, props, odt_dir, out_dir, len(parts)))
        elif el.tag == q("draw:custom-shape"):
            parts.append(shape_svg(el, box, styles, fit))
    marker = "<defs>" + "".join(
        f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{num(size)}" markerHeight="{num(size)}" '
        'markerUnits="userSpaceOnUse" orient="auto"><path d="M0 0L10 5L0 10z"/></marker>'
        for mid, size in HEADS.items()) + "</defs>"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(right)} {num(bottom)}" '
            f'width="{right / U:.4f}in" height="{bottom / U:.4f}in">\n{marker}\n' + "\n".join(p for p in parts if p) + "\n</svg>\n")


def main(odt_dir, out_root):
    odt_dir, out_root = Path(odt_dir), Path(out_root)
    shutil.rmtree(out_root, ignore_errors=True)
    root = ET.parse(odt_dir / "content.xml").getroot()
    styles = load_styles(root)
    for n, group in enumerate(root.iter(q("draw:g")), 1):
        out = out_root / f"drawing-{n:02d}"
        out.mkdir(parents=True)
        (out / "drawing.svg").write_text(drawing_svg(group, styles, odt_dir, out))
        print("wrote", out / "drawing.svg")


if __name__ == "__main__":
    main(*sys.argv[1:3])
