"""Split the Thonny files-panels screenshot into two crisp, tight panels for the Following lines sheet.

usage: uv run python scripts/prepare_thonny_panels.py <assets/following-lines dir>

Reads thonny-files-panels.png, writes thonny-files-left.png and thonny-files-right.png beside it.
Left: the two file lists with their labels; the blank band between the upper file list and the Shell
tab is cut out ("cut and shut") so the rest keeps its size. Right: the right-click menu.
Rows/columns are in source pixels; re-measure them if the original is replaced by a higher-res one
(scale them by the width ratio). Idempotent: always rebuilt from the original.
"""
import sys
from pathlib import Path

from PIL import Image

LEFT_COLS = (0, 312)       # panel plus the "Files on ..." labels beside it
LEFT_ROWS = (12, 416)      # drop the tab strip above and the frame below
LEFT_CUT = (142, 224)      # empty band: below the upper file list, above the Shell tab
RIGHT_BOX = (337, 8, 633, 298)  # left, top, right, bottom of the context-menu panel


def on_white(img):
    """The labels sit on transparency; flatten onto white so every tool shows the same thing."""
    flat = Image.new("RGBA", img.size, (255, 255, 255, 255))
    flat.alpha_composite(img.convert("RGBA"))
    return flat.convert("RGB")


def cut_and_shut(img, rows, cut):
    """Keep `rows`, with the `cut` band removed and the halves joined."""
    top = img.crop((0, rows[0], img.width, cut[0]))
    bottom = img.crop((0, cut[1], img.width, rows[1]))
    joined = Image.new("RGB", (img.width, top.height + bottom.height), (255, 255, 255))
    joined.paste(top, (0, 0))
    joined.paste(bottom, (0, top.height))
    return joined


def main(folder):
    folder = Path(folder)
    src = on_white(Image.open(folder / "thonny-files-panels.png"))
    left = cut_and_shut(src.crop((LEFT_COLS[0], 0, LEFT_COLS[1], src.height)), LEFT_ROWS, LEFT_CUT)
    left.save(folder / "thonny-files-left.png")
    src.crop(RIGHT_BOX).save(folder / "thonny-files-right.png")
    print(f"left {left.size}, right {(RIGHT_BOX[2] - RIGHT_BOX[0], RIGHT_BOX[3] - RIGHT_BOX[1])}")


if __name__ == "__main__":
    main(sys.argv[1])
