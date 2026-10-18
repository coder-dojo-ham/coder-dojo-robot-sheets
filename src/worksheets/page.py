"""Page furniture for a worksheet: title, fact bar, hero, QR, footer link. Styles are in worksheet.css."""
import io
from pathlib import Path

import segno

from .config import asset

CSS = (Path(__file__).parent / "worksheet.css").read_text()

LOGO = "coderdojo-ku-logo.png"  # shared asset, top right of every cover
PEPPER = "\U0001F336️"


def qr_svg(url):
    # vector so it prints crisp; high error correction for rough printers
    buf = io.BytesIO()
    segno.make(url, error="h").save(buf, kind="svg", scale=10, border=0, xmldecl=False,
                                    svgns=True, nl=False)
    return buf.getvalue().decode()


def difficulty_html(level, total=5):
    on = f'<span>{PEPPER}</span>' * level
    off = f'<span class="off">{PEPPER}</span>' * (total - level)
    return on + off


def qr_html(meta):
    """The sheet's own QR image if it has one (e.g. the original export), else generated."""
    if meta.get("qr"):
        return f'<img src="{asset(meta["qr"]).as_uri()}">'
    return qr_svg(meta["link"])


def head_html(meta, intro_html, hero_srcs):
    facts = (f'<td>Difficulty: {difficulty_html(int(meta["difficulty"]))}</td>'
             f'<td>Language: {meta["language"]}</td><td>Requires: {meta["requires"]}</td>')
    hero = "".join(f'<img src="{src}">' for src in hero_srcs)
    return f"""<div class="titlebar"><h1>{meta["title"]}</h1>
<div class="logo"><img src="{asset(LOGO).as_uri()}"></div></div>
<table class="facts"><tr>{facts}</tr></table>
<div class="hero">{hero}</div>
<div class="intro"><div class="qr">{qr_html(meta)}</div>
<div class="text"><p><strong>Version: {meta["version"]}</strong></p>{intro_html}</div></div>"""


def link_html(meta):
    return f'<p class="link">Sheet link: <a href="{meta["link"]}">{meta["link"]}</a></p>'
