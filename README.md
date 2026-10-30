# coderdojo robots worksheets (code)

Builds CoderDojo robot worksheet PDFs from markdown sheets and reusable snippets - no Google Docs.

- Sheet sources: `sheets/`. Images are in `assets/` (`assets/<sheet>/` for a sheet's own, `assets/` for ones shared between sheets).
- Built PDFs go to `sheets/` under `WORKSHEETS_NEXTCLOUD` (default `~/nextcloud/1-Areas/Orionrobots - coderdojo/robots-worksheets`;
  set the env var to put them elsewhere)
- Notes / area router: `orionrobots_memories/20-areas/coderdojo/`; project log:
  `orionrobots_memories/10-projects/2026-10-11-coderdojo-worksheet-framework/`
- Older work to gather in: `coder_dojo_robots`, `coder-dojo-worksheets`, `coder-dojo-worksheets2` (inside the Nextcloud coderdojo area; embedded git repos, see the memories migration project)

## Build

```bash
uv run build-sheet sheets/make-it-drive.md            # PDF -> Nextcloud sheets/
uv run build-sheet sheets/make-it-drive.md /some/dir  # PDF -> elsewhere
```

Copy the built PDFs to the shared CoderDojo KU Google Drive `Worksheets/` folder:

```bash
cp .env.example .env        # once per machine; set GDRIVE_WORKSHEETS_DIR (git-ignored)
uv run publish-sheets       # mounted path, or a Windows G:\... path via powershell.exe on WSL
uv run publish-sheets connecting-thonny   # only the named sheets (others may hold unreviewed local changes)
```

In VS Code (Ctrl+Shift+P > Tasks: Run Task; the default build task is Ctrl+Shift+B), `.vscode/tasks.json` has:
**Build current sheet (preview)**, **Build and publish current sheet**, **Build all sheets (no publish)** and
**Republish all sheets** (`scripts/republish-all.sh [--build-only]`: builds every sheet, then publishes all PDFs, retrying the occasional empty-glob failure).

Fonts (Arimo, Inconsolata) and emoji PNGs are fetched on first run into `fonts/` and `.cache/`
(both git-ignored). Page PNG previews land in `.cache/previews/<sheet>/` and the build fails if the QR
doesn't decode to the sheet link or the pinned fonts aren't embedded.

## Overview sheet

`sheets/all-robot-sheets.md` has `layout: overview`: one landscape page, no markdown body. Front matter `link` is the
master QR and `tiles` (title, link, difficulty, images) are the per-sheet tiles; every QR is generated and
checked by the build. Change a tile's `link` when its `/dojo/...` short link goes live. See `src/worksheets/overview.py`.

## Writing a sheet

`sheets/<name>.md`: YAML front matter (title, difficulty 1-5, language, requires, version, link, hero
images from `assets/`, `pdf_link` = the PDF's Drive share link, pasted once; it stays valid when `publish-sheets` overwrites the file), intro text up to `<!-- /intro -->` (sits beside the QR), the rest of the cover
page up to the first `## `, then steps. `## Step N` / `## Checkpoint` start a new page; put `{.nobreak}`
on the line above a heading to keep it flowing, or `{.newpage}` to start any other heading on a new page.

| Feature | Markdown |
| --- | --- |
| Code, coloured keywords | ` ```python ` fence |
| REPL session (Thonny-style `>>>`) | ` ```pycon ` fence |
| Error text in red | ` ```text {tone="error"} ` |
| Tint changed lines | ` ```python {hl="2,3"} ` |
| Callout label on a token | ` ```python {note="6\|-0.7\|Set to **-0.7**"} ` (`line\|token\|label`, `;`-separated; a line may have several); join tokens with `&` (`Pin&IN`); label prefix `^` grows it upward, `^N`/`_N` moves it N lines up/down with an angled leader |
| Tip / warning box | `::: tip` / `::: warning` ... `:::` |
| Figure beside text | `:::: side` containing `::: fig` and `::: text` (`side-right` puts the figure on the right; used in What is an LED) |
| Two figures, left and right margin | `:::: split` containing two `::: fig` (the second sits flush right); used for the Thonny panels in Following lines |
| Robot diagram | ` ```robot ` fence, YAML - see `src/worksheets/robot_diagram.py` |
| Image from `assets/` | `![alt](file.png){style="width:60mm"}` |
| Short list after a heading stays on one page | automatic (`h2 + ul` is `break-inside: avoid`) |
| A paragraph before a code block or lone image stays on its page with it | automatic (`p.lead`); add `{.lead}` on the line above to force it |
| Generated QR code in the text | `![alt](qr:https://orionrobots.co.uk/dojo/led){style="width:36mm"}` |
| Reusable snippet | `{{> warn-stand}}` includes `snippets/warn-stand.md` (`{{> name key=value}}` fills `{{key}}`) |

Code layout: `config.py` paths, `fonts.py`, `emojis.py`, `code.py` (highlighting), `robot_diagram.py` (SVG
robots), `markup.py` (markdown -> HTML), `page.py` (cover furniture), `worksheet.css` (all styling), `verify.py`, `build.py`.

Asset prep that is more than a crop is a script in `scripts/` (e.g. `compose_thonny_panels.py`: crops the original screenshots, cut-and-shut, vector labels/arrows/outlines), always rebuilt from the original so it can be re-run when a better source turns up. Originals extracted from Google Docs drawings come from `scripts/gdocs/` (see its README). `compose_connecting_thonny.py` renders a whole sheet's figures from the committed drawing SVGs and pictures in `assets/connecting-thonny/src/` (vector labels, arrows and dashed outlines over the original screenshots; the robot stand line drawing is traced to a vector); `stage` mode refreshes those sources from `scripts/gdocs/` output.

## Generated assets

Most images are committed. A few are drawn or rendered by scripts from committed sources, so they are git-ignored; run
these once after a fresh clone (each is idempotent; they need `playwright`, then `playwright install chromium`):

```bash
uv run python scripts/draw_ping_pong.py assets/avoiding-obstacles/ping-pong.svg   # then render it to ping-pong.png with scripts/gdocs/render_svg.py
uv run --with playwright python scripts/crop_thonny_plotter.py
uv run --with playwright python scripts/compose_thonny_panels.py assets/following-lines
uv run --with playwright --with potracer --with numpy python scripts/compose_connecting_thonny.py   # assets/connecting-thonny/*.png
```

## Licence

MIT - see [LICENSE](LICENSE). Covers the code, the worksheets and the images in `assets/` (my own screenshots,
drawings and SVGs, and the CoderDojo KU logo).
