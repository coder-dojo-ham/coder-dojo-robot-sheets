"""The one-page landscape overview that lists every sheet with its QR code (the old "All robot sheets" slide).

Driven entirely by front matter: `link` is the overview's own QR, `tiles` is a list of
{title, link, difficulty, images}. Tiles are laid out two to a row, in order.
"""
from pathlib import Path

from .config import asset
from .page import LOGO, difficulty_html, qr_svg

CSS = (Path(__file__).parent / "overview.css").read_text()
TILES_PER_ROW = 2


def display_link(url):
    return url.removeprefix("https://")


def tile_html(tile):
    images = "".join(f'<img src="{asset(name).as_uri()}">' for name in tile["images"])
    return f"""<td class="tile"><div class="card"><div class="tile-head"><span class="tile-title">{tile["title"]}</span>
<span class="peppers">{difficulty_html(int(tile["difficulty"]))}</span></div>
<a href="{tile["link"]}">{display_link(tile["link"])}</a>
<table class="tile-body"><tr><td class="qr">{qr_svg(tile["link"])}</td>
<td class="pics">{images}</td></tr></table></div></td>"""


def rows_html(tiles):
    cells = [tile_html(tile) for tile in tiles]
    rows = [cells[i:i + TILES_PER_ROW] for i in range(0, len(cells), TILES_PER_ROW)]
    return "".join(f"<tr>{''.join(row)}</tr>" for row in rows)


def overview_html(meta):
    return f"""<table class="head"><tr>
<td class="logo"><img src="{asset(LOGO).as_uri()}"></td>
<td class="title"><h1>{meta["title"]}</h1><a href="{meta["link"]}">{display_link(meta["link"])}</a></td>
<td class="master-qr">{qr_svg(meta["link"])}</td></tr></table>
<table class="grid">{rows_html(meta["tiles"])}</table>"""


def expected_links(meta):
    return [meta["link"]] + [tile["link"] for tile in meta["tiles"]]
