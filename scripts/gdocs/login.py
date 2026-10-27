"""One-off: open Google Docs in the persistent profile so you can sign in by hand.

usage: uv run --with playwright python scripts/gdocs/login.py <doc-url>
Returns once the doc editor has loaded (i.e. you are signed in) or after 10 minutes.
"""
import sys

from browser import open_context, session


def main(url):
    with session() as pw:
        ctx = open_context(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(url)
        page.wait_for_selector(".kix-appview-editor", timeout=600_000)
        print("signed in; doc loaded:", page.title())
        ctx.close()


if __name__ == "__main__":
    main(sys.argv[1])
