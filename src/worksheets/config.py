"""Where things live. Code is in git; documents (assets, PDFs) are in Nextcloud."""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SHEETS_SRC = REPO / "sheets"
SNIPPETS = REPO / "snippets"
FONTS = REPO / "fonts"
CACHE = REPO / ".cache"

NEXTCLOUD = Path(os.environ.get(
    "WORKSHEETS_NEXTCLOUD",
    Path.home() / "nextcloud/1-Areas/Orionrobots - coderdojo/robots-worksheets"))
ASSETS = NEXTCLOUD / "assets"
OUTPUT = NEXTCLOUD / "sheets"

# assets/<sheet>/ holds a sheet's own images; assets/ itself holds ones shared between sheets.
_asset_dirs = [ASSETS]


def select_sheet(stem):
    """Make `asset()` look in assets/<stem>/ first, then in the shared assets/."""
    _asset_dirs[:] = [ASSETS / stem, ASSETS]


def asset(name):
    for folder in _asset_dirs:
        if (folder / name).exists():
            return folder / name
    raise FileNotFoundError(f"asset {name!r} not in {[str(d) for d in _asset_dirs]}")
