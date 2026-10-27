"""Render a drawing.svg to PNG with headless Chromium (opened directly, so relative picture links load).

usage: uv run --with playwright python scripts/gdocs/render_svg.py <drawing.svg> <out.png> [px-per-inch]
Default 262 px/in is the density of the Thonny screenshots as placed in the Step 4 drawing; raise it
for crisper annotations (pictures just upsample).
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from browser import chromium_path

CSS_DPI = 96


def size_in(svg_text):
    w = re.search(r'width="([\d.]+)in"', svg_text).group(1)
    h = re.search(r'height="([\d.]+)in"', svg_text).group(1)
    return float(w), float(h)


def main(svg, out, ppi=262):
    svg = Path(svg).resolve()
    w_in, h_in = size_in(svg.read_text())
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True)
        page = browser.new_page(
            viewport={"width": round(w_in * CSS_DPI), "height": round(h_in * CSS_DPI)},
            device_scale_factor=float(ppi) / CSS_DPI,
        )
        page.goto(svg.as_uri())
        page.evaluate("document.fonts.ready")  # @font-face fonts load lazily
        page.screenshot(path=out)
        browser.close()


if __name__ == "__main__":
    main(*sys.argv[1:4])
