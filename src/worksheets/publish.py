"""Copy the built sheet PDFs to the shared Google Drive worksheets folder.

Destination comes from GDRIVE_WORKSHEETS_DIR (environment or the git-ignored .env, see
.env.example). It may be a path on this machine (a mount) or, on WSL where the drive is only
mounted on the Windows side, a Windows path such as G:\\My Drive\\...: those go via powershell.exe.
Copying is idempotent: existing files are overwritten with the same content.
With sheet names as arguments (`publish-sheets connecting-thonny`) only those PDFs are copied, so a sheet
can go out without re-publishing others that have local changes nobody has reviewed yet.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .config import OUTPUT, REPO

ENV_VAR = "GDRIVE_WORKSHEETS_DIR"
WINDOWS_PATH = re.compile(r"^[A-Za-z]:[\\/]")


def read_dotenv(path):
    """KEY=value lines; blanks and # comments ignored; surrounding quotes stripped."""
    values = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip().strip("'\"")
    return values


def destination():
    dest = os.environ.get(ENV_VAR) or read_dotenv(REPO / ".env").get(ENV_VAR)
    if not dest:
        sys.exit(f"{ENV_VAR} is not set: copy .env.example to .env and fill it in")
    return dest


def copy_local(pdfs, dest):
    dest = Path(dest)
    if not dest.is_dir():
        sys.exit(f"{dest} is not a directory (is the drive mounted?)")
    for pdf in pdfs:
        shutil.copy2(pdf, dest / pdf.name)


def _ps_quote(text):
    return "'" + text.replace("'", "''") + "'"


def copy_via_powershell(pdfs, dest):
    """For a Windows-side destination that WSL has not mounted."""
    sources = ",".join(_ps_quote(subprocess.check_output(["wslpath", "-w", str(p)], text=True).strip())
                       for p in pdfs)
    script = (f"$d = {_ps_quote(dest)}; if (-not (Test-Path -LiteralPath $d)) {{ throw \"no such folder: $d\" }}; "
              f"Copy-Item -LiteralPath {sources} -Destination $d -Force")
    # cwd on C: because powershell warns about (and can break on) a UNC working directory
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], check=True, cwd="/mnt/c")


def main():
    names = sys.argv[1:]
    pdfs = [OUTPUT / f"{name}.pdf" for name in names] if names else sorted(OUTPUT.glob("*.pdf"))
    missing = [p for p in pdfs if not p.exists()]
    if missing or not pdfs:
        sys.exit(f"no PDF for {', '.join(p.name for p in missing) or 'anything'} in {OUTPUT}; run build-sheet first")
    dest = destination()
    # a mounted/local path wins; otherwise a Windows-style path is handed to powershell
    if Path(dest).is_dir() or not WINDOWS_PATH.match(dest):
        copy_local(pdfs, dest)
    else:
        copy_via_powershell(pdfs, dest)
    print(f"copied {len(pdfs)} sheet(s) to {dest}: " + ", ".join(p.name for p in pdfs))


if __name__ == "__main__":
    main()
