"""Syntax-highlighted code blocks with 'changed line' highlights and callout notes.

Fence attributes (all optional), e.g. ```python {hl="2,3" note="6|-0.7|Set to **-0.7**"}:
  hl    comma separated 1-based lines to tint (the lines the kid should change/add)
  note  ';'-separated "line|token|label": boxes `token` on that line and hangs a label off it;
        the token can be whitespace (e.g. 4 spaces to flag an indent), the label may use <br>;
        join tokens with '&' to box several on one line (e.g. "Pin&IN"); start the label with '^'
        to grow it upwards, so it can sit beside a blank line instead of colliding with the next label.
        '^N' / '_N' also moves the label N lines up / down, angling its leader to reach it
  tone  "error" prints the block in red, like a Thonny traceback
Use ```pycon for a REPL session: the `>>>` prompt is styled like Thonny's.
"""
import html
import math
import re

from pygments.lexers import get_lexer_by_name
from pygments.token import Comment, Generic, Keyword, Name, Number, String

ATTR = re.compile(r'(\w+)="([^"]*)"')
LEADER_GAP_MM = 1.5  # air between the end of the code and the start of its leader line
FONT_PT = 13  # keep in step with .code font-size in page.py
LINE_PT = FONT_PT * 1.12  # code line height; keep in step with .code line-height
LEADER_LEN_MM = 14 - LEADER_GAP_MM  # leader run from the end of the code to the label, before any angle
PT_PER_MM = 72 / 25.4
LABEL_PREFIX = re.compile(r"^([\^_])(\d+(?:\.\d+)?)?")
ADVANCE = 0.5  # Inconsolata glyph advance in em, so line width is known without measuring


def parse_attrs(info):
    return dict(ATTR.findall(info))


def _css_class(ttype):
    # Mirrors the Thonny look the old sheets used: bold keywords, bold def names, orange numbers.
    if ttype in Keyword or ttype in Generic.Prompt:
        return "kw"
    if ttype in Name.Function or ttype in Name.Class:
        return "fn"
    if ttype in Number:
        return "num"
    if ttype in Comment:
        return "cm"
    if ttype in String:
        return "st"
    return ""


def _split_lines(code, lang):
    """-> list of lines, each a list of [css_class, text] runs."""
    lexer = get_lexer_by_name(lang or "text")
    lines = [[]]
    for ttype, value in lexer.get_tokens(code):
        cls = _css_class(ttype)
        parts = value.split("\n")
        for i, part in enumerate(parts):
            if i:
                lines.append([])
            if part:
                lines[-1].append([cls, part])
    if lines and not lines[-1]:
        lines.pop()  # the lexer's trailing newline
    return lines


def _mark(runs, token):
    """Split runs so `token` is its own run flagged for boxing. Returns True if found."""
    text = "".join(t for _, t in runs)
    start = text.find(token)
    if start < 0:
        return False
    end, pos, out = start + len(token), 0, []
    for cls, t in runs:
        a, b = pos, pos + len(t)
        pos = b
        if b <= start or a >= end:
            out.append([cls, t])
            continue
        if a < start:
            out.append([cls, t[:start - a]])
        out.append([cls + " mark", t[max(start, a) - a:min(end, b) - a]])
        if b > end:
            out.append([cls, t[end - a:]])
    runs[:] = out
    return True


def _runs_html(runs):
    return "".join(
        f'<span class="{c}">{html.escape(t)}</span>' if c else html.escape(t) for c, t in runs)


def _split_label(label):
    """-> (text, grows_up, shift_pt); shift_pt is signed, positive = down."""
    m = LABEL_PREFIX.match(label)
    if not m:
        return label, False, 0.0
    lines = float(m.group(2) or 0)
    up = m.group(1) == "^"
    return label[m.end():], up, (-lines if up else lines) * LINE_PT


def render_code(code, lang, info="", inline=lambda s: s):
    """`inline` renders a markdown inline string (for note labels) to HTML."""
    attrs = parse_attrs(info)
    lines = _split_lines(code.rstrip("\n"), lang)
    hl = {int(n) for n in attrs.get("hl", "").split(",") if n.strip()}
    notes = {}
    for spec in filter(None, attrs.get("note", "").split(";")):
        no, token, label = spec.split("|", 2)
        no = int(no)
        for part in token.split("&"):
            if not _mark(lines[no - 1], part):
                raise ValueError(f"note token {part!r} not on line {no}: {lines[no - 1]}")
        notes[no] = label

    widest = max(len("".join(t for _, t in runs)) for runs in lines)
    rows = []
    for n, runs in enumerate(lines, 1):
        cls = "ln hl" if n in hl else "ln"
        note = ""
        if n in notes:
            # leader runs from the end of this line's text to the label, which sits past the block;
            # a shifted label tilts it, so it is rotated about its start and lengthened to match
            text, up, shift = _split_label(notes[n])
            gap_pt = (widest - len("".join(t for _, t in runs))) * FONT_PT * ADVANCE
            run_pt = gap_pt + LEADER_LEN_MM * PT_PER_MM
            angle = math.degrees(math.atan2(shift, run_pt))
            length = math.hypot(run_pt, shift)
            anchor = f"bottom:calc(.6em + {shift:.1f}pt)" if up else f"top:calc(.62em - {shift:.1f}pt)"
            place = f"bottom:calc(1pt - {shift:.1f}pt)" if up else f"top:{shift:.1f}pt"
            note = (f'<span class="note{" up" if up else ""}" style="{place}">'
                    f'<span class="leader" style="left:calc(-{gap_pt:.1f}pt - {3 - LEADER_GAP_MM}mm);'
                    f'{anchor};width:{length:.1f}pt;transform:rotate({angle:.2f}deg)"></span>'
                    f'{inline(text)}</span>')
        rows.append(f'<span class="{cls}">{_runs_html(runs) or "&#8203;"}{note}</span>')
    cls = "code noted" if notes else "code"
    # a label with <br> runs below its line; reserve that room so it can't hit what follows
    spill = max((no + notes[no].count("<br>") + math.ceil(max(_split_label(notes[no])[2], 0) / LINE_PT)
                 - len(lines) for no in notes if not _split_label(notes[no])[1]), default=0)
    style = f' style="margin-bottom:calc(4mm + {spill * FONT_PT * 1.12:.1f}pt)"' if spill > 0 else ""
    if attrs.get("tone") == "error":
        cls += " err"
    return f'<div class="{cls}"{style}>{"".join(rows)}</div>\n'
