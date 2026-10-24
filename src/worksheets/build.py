"""Build a worksheet PDF from a markdown sheet.

Usage: build-sheet sheets/make-it-drive.md [output-dir]
An overview sheet (`layout: overview`, see overview.py) is one landscape page of tiles.
Sheet layout: YAML front matter, intro text (beside the QR) up to `<!-- /intro -->`,
the rest of the cover page up to the first `## ` heading, then the steps.
"""
import re
import sys
from pathlib import Path

import weasyprint
import yaml
from weasyprint.text.fonts import FontConfiguration

from .config import CACHE, OUTPUT, asset, select_sheet
from .emojis import emojify
from .fonts import ensure_fonts, font_face_css
from .markup import to_html
from .overview import CSS as OVERVIEW_CSS, expected_links, overview_html
from .page import CSS, head_html, link_html
from .verify import verify

FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
INTRO_END = "<!-- /intro -->"
STEP_HEADING = re.compile(r"<h2>(Step |Checkpoint)")


def split_sheet(text):
    match = FRONT_MATTER.match(text)
    meta = yaml.safe_load(match.group(1))
    body = text[match.end():]
    intro, _, rest = body.partition(INTRO_END)
    cover, sep, steps = rest.partition("\n## ")
    return meta, intro, cover, ("## " + steps) if sep else ""


def mark_step_headings(html):
    return STEP_HEADING.sub(
        lambda m: f'<h2 class="{"checkpoint" if m.group(1) == "Checkpoint" else "step"}">{m.group(1)}',
        html)


def is_overview(meta):
    return meta.get("layout") == "overview"


def build_html(meta, intro, cover, steps):
    if is_overview(meta):
        return f"<html><body>{emojify(overview_html(meta))}</body></html>"
    hero = [asset(name).as_uri() for name in meta.get("hero", [])]
    page = (head_html(meta, to_html(intro), hero) + to_html(cover) + link_html(meta)
            + mark_step_headings(to_html(steps)))
    return f"<html><body>{emojify(page)}</body></html>"


def render_pdf(html, out_pdf, sheet_css=CSS):
    fonts = ensure_fonts()
    config = FontConfiguration()  # @font-face only applies when CSS and render share one
    css = weasyprint.CSS(string=font_face_css(fonts) + sheet_css,
                         font_config=config)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    weasyprint.HTML(string=html, base_url=str(Path.cwd())).write_pdf(
        out_pdf, stylesheets=[css], font_config=config)


def main():
    sheet = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    select_sheet(sheet.stem)
    meta, intro, cover, steps = split_sheet(sheet.read_text())
    out_pdf = out_dir / f"{sheet.stem}.pdf"
    render_pdf(build_html(meta, intro, cover, steps), out_pdf,
               OVERVIEW_CSS if is_overview(meta) else CSS)
    verify(out_pdf, expected_links(meta) if is_overview(meta) else [meta["link"]],
           CACHE / "previews" / sheet.stem)
    print(out_pdf)


if __name__ == "__main__":
    main()
