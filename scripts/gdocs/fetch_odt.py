"""Download a Google Doc you own as ODT and unzip it.

usage: uv run --with playwright python scripts/gdocs/fetch_odt.py <doc-id-or-url> <out-dir>

ODT is the one export that keeps a Docs drawing as layers (native-resolution pictures plus vector
shapes); HTML/docx flatten it to a single PNG. Needs the profile from login.py.
Idempotent: out-dir is rebuilt from scratch on each run.
"""
import re
import shutil
import sys
import zipfile
from io import BytesIO
from pathlib import Path

from browser import open_context, session


def doc_id(arg):
    m = re.search(r"/d/([A-Za-z0-9_-]+)", arg)
    return m.group(1) if m else arg


def fetch(ctx, did):
    r = ctx.request.get(f"https://docs.google.com/document/d/{did}/export?format=odt")
    if not r.ok:
        sys.exit(f"export failed: HTTP {r.status} (signed in? run login.py)")
    return r.body()


def main(arg, out):
    out = Path(out)
    shutil.rmtree(out, ignore_errors=True)
    with session() as pw:
        ctx = open_context(pw)
        body = fetch(ctx, doc_id(arg))
        ctx.close()
    zipfile.ZipFile(BytesIO(body)).extractall(out)
    print("unpacked ODT to", out)


if __name__ == "__main__":
    main(*sys.argv[1:3])
