# coderdojo robots worksheets (code)

Builds CoderDojo robot worksheet PDFs from markdown sheets and reusable snippets - no Google Docs.

- Sheets and assets (documents): `~/nextcloud/1-Areas/Orionrobots - coderdojo/robots-worksheets/`
  (`assets/<sheet>/` in for a sheet's own images, `assets/` for ones shared between sheets; `sheets/` PDFs out; `examples/` holds the old Google Docs PDF exports to match)
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
```

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
on the line above a heading to keep it flowing.

| Feature | Markdown |
| --- | --- |
| Code, coloured keywords | ` ```python ` fence |
| REPL session (Thonny-style `>>>`) | ` ```pycon ` fence |
| Error text in red | ` ```text {tone="error"} ` |
| Tint changed lines | ` ```python {hl="2,3"} ` |
| Callout label on a token | ` ```python {note="6\|-0.7\|Set to **-0.7**"} ` (`line\|token\|label`, `;`-separated); join tokens with `&` (`Pin&IN`); label prefix `^` grows it upward, `^N`/`_N` moves it N lines up/down with an angled leader |
| Tip / warning box | `::: tip` / `::: warning` ... `:::` |
| Figure beside text | `:::: side` containing `::: fig` and `::: text` (`side-right` puts the figure on the right; used in What is an LED) |
| Robot diagram | ` ```robot ` fence, YAML - see `src/worksheets/robot_diagram.py` |
| Image from `assets/` | `![alt](file.png){style="width:60mm"}` |
| Reusable snippet | `{{> warn-stand}}` includes `snippets/warn-stand.md` (`{{> name key=value}}` fills `{{key}}`) |

Code layout: `config.py` paths, `fonts.py`, `emojis.py`, `code.py` (highlighting), `robot_diagram.py` (SVG
robots), `markup.py` (markdown -> HTML), `page.py` (cover furniture), `worksheet.css` (all styling), `verify.py`, `build.py`.
