"""Post-render checks, so a broken sheet fails loudly instead of looking plausible."""
import sys

import cv2
import numpy as np
import pymupdf
import zxingcpp


def render_previews(pdf_path, out_dir, dpi=100):
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    for n, page in enumerate(doc, 1):
        page.get_pixmap(dpi=dpi).save(out_dir / f"page-{n:02d}.png")
    return doc


def _qr_texts(page):
    pix = page.get_pixmap(dpi=200)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return [b.text for b in zxingcpp.read_barcodes(gray)]


def verify(pdf_path, meta, preview_dir):
    doc = render_previews(pdf_path, preview_dir)
    problems = []
    if meta["link"] not in _qr_texts(doc[0]):
        problems.append(f"QR on page 1 does not decode to {meta['link']}")
    fonts = {f[3].split("+")[-1] for page in doc for f in page.get_fonts()}
    if not any(name.startswith("Arimo") for name in fonts):
        problems.append(f"body font Arimo not embedded (got {sorted(fonts)})")
    if problems:
        sys.exit("VERIFY FAILED:\n  " + "\n  ".join(problems))
    print(f"OK: {len(doc)} pages, QR decodes to the sheet link, fonts {sorted(fonts)}")
