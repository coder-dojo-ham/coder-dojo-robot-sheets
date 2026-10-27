"""Markdown -> HTML for a sheet: snippet includes, callouts, side-by-side layout, code, diagrams."""
import re

from markdown_it import MarkdownIt
from mdit_py_plugins.attrs import attrs_block_plugin, attrs_plugin
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

from .code import render_code
from .config import SNIPPETS, asset
from .robot_diagram import render_robot

INCLUDE = re.compile(r"^\{\{>\s*([\w-]+)((?:\s+\w+=\S+)*)\s*\}\}\s*$", re.MULTILINE)
ARG = re.compile(r"(\w+)=(\S+)")
# ::: names and the CSS class each renders to. fig/text only make sense inside side/side-right/split.
CONTAINERS = ("tip", "warning", "side", "side-right", "split", "fig", "text")


def expand_snippets(source, _depth=0):
    """Replace `{{> name key=value}}` with snippets/name.md, filling `{{key}}` placeholders."""
    if _depth > 5:
        raise RecursionError("snippet includes nested too deeply")

    def sub(match):
        path = SNIPPETS / f"{match.group(1)}.md"
        text = path.read_text().strip("\n")
        for key, value in ARG.findall(match.group(2)):
            text = text.replace("{{" + key + "}}", value)
        return expand_snippets(text, _depth + 1)

    return INCLUDE.sub(sub, source)


def _fence_renderer(md):
    def render(self, tokens, idx, options, env):
        token = tokens[idx]
        lang, _, info = token.info.strip().partition(" ")
        if lang == "robot":
            return render_robot(token.content)
        return render_code(token.content, lang, info, inline=md.renderInline)
    return render


def _render_image(self, tokens, idx, options, env):
    token = tokens[idx]
    src = token.attrGet("src")
    if not src.startswith(("http", "file:", "/")):
        src = asset(src).as_uri()
    token.attrSet("src", src)
    token.attrSet("alt", token.content)
    return self.renderToken(tokens, idx, options, env)


def _mark_lead_ins(state):
    """Class `lead` on any paragraph directly followed by a code fence (see .lead in page.py)."""
    tokens = state.tokens
    for i in range(len(tokens) - 3):
        if (tokens[i].type == "paragraph_open" and tokens[i + 2].type == "paragraph_close"
                and tokens[i + 3].type == "fence"):
            tokens[i].attrJoin("class", "lead")


def build_parser():
    md = (MarkdownIt("commonmark", {"typographer": True, "html": True})
          .enable(["replacements", "smartquotes", "table"])
          .use(front_matter_plugin)
          .use(attrs_plugin)
          .use(attrs_block_plugin))
    for name in CONTAINERS:
        md.use(container_plugin, name=name,
               render=lambda self, tokens, idx, options, env, name=name:
               f'<div class="{name}">\n' if tokens[idx].nesting == 1 else "</div>\n")
    md.core.ruler.push("lead_ins", _mark_lead_ins)
    md.add_render_rule("fence", _fence_renderer(md))
    md.add_render_rule("image", _render_image)
    return md


def to_html(source):
    md = build_parser()
    return md.render(expand_snippets(source))
