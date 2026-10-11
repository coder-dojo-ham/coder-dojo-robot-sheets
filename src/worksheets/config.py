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
