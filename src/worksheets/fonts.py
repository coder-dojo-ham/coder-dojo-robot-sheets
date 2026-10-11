"""Pinned fonts: download once, bake static instances (weasyprint ignores variable weights)."""
import urllib.parse
import urllib.request

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from .config import FONTS

BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
# family -> (upstream file, [(static name, axis values)])
FAMILIES = {
    "Arimo": ("arimo/Arimo[wght].ttf",
              [("Regular", {"wght": 400}), ("Bold", {"wght": 700})]),
    "Inconsolata": ("inconsolata/Inconsolata[wdth,wght].ttf",
                    [("Regular", {"wdth": 100, "wght": 400}),
                     ("Bold", {"wdth": 100, "wght": 700})]),
}


def _download(rel_path, dest):
    if dest.exists():
        return
    url = BASE + urllib.parse.quote(rel_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)


def ensure_fonts():
    """Return {(family, style): Path}; only fetches/instances what is missing."""
    out = {}
    for family, (upstream, instances) in FAMILIES.items():
        variable = FONTS / "variable" / f"{family}.ttf"
        for style, axes in instances:
            static = FONTS / f"{family}-{style}.ttf"
            if not static.exists():
                _download(upstream, variable)
                font = TTFont(variable)
                instantiateVariableFont(font, axes, inplace=True)
                font.save(static)
            out[(family, style)] = static
    return out


def font_face_css(fonts):
    rules = []
    for (family, style), path in fonts.items():
        weight = "bold" if style == "Bold" else "normal"
        rules.append(f"@font-face {{ font-family: {family}; font-weight: {weight}; "
                     f"src: url('{path.as_uri()}'); }}")
    return "\n".join(rules)
