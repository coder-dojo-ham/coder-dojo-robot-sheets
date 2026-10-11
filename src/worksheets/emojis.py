"""Swap emoji characters for Google-style PNG images.

weasyprint can't draw colour-emoji fonts, and PNGs also match the look of the old
Google Docs sheets. Images are fetched once and cached.
"""
import re
import urllib.request

from .config import CACHE

SOURCE = "https://cdn.jsdelivr.net/npm/emoji-datasource-google@15.1.2/img/google/64/{}.png"
# Symbols/pictographs, plus arrows/dingbats only when forced to emoji style by U+FE0F.
EMOJI = re.compile(
    r"(?:[\U0001F300-\U0001FAFF]|[⌀-⏿☀-➿⤀-⥿⬀-⯿←-⇿]️?)"
    r"(?:️|‍[\U0001F300-\U0001FAFF]️?)*")
TEXT_NODE = re.compile(r">([^<]+)<")


def _png(chars):
    """Cached PNG path for an emoji sequence, or None if the source lacks it."""
    codes = [f"{ord(c):x}" for c in chars if c != "️"]
    # source names include fe0f for some emoji and not others; try both
    for name in ("-".join(codes), "-".join(codes) + "-fe0f"):
        dest = CACHE / "emoji" / f"{name}.png"
        if dest.exists():
            return dest
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(SOURCE.format(name), dest)
            return dest
        except OSError:
            dest.unlink(missing_ok=True)
    return None


def _swap(match):
    chars = match.group(0)
    path = _png(chars)
    return f'<img class="emoji" src="{path.as_uri()}" alt="">' if path else chars


def emojify(html):
    """Only touch text between tags, never attribute values."""
    return TEXT_NODE.sub(lambda m: ">" + EMOJI.sub(_swap, m.group(1)) + "<", html)
