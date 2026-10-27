"""Shared Chromium launcher for the Google Docs drawing-export scripts.

Uses a persistent profile outside the repo so you sign in to Google once, by hand, and later runs reuse it.
Headed because you sign in interactively; WSLg shows the window. No attempt is made to hide automation.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE = Path.home() / ".cache" / "gdocs-export-profile"  # holds cookies: keep out of git


def chromium_path():
    """Playwright's own Chromium build (no system Chrome on this box)."""
    builds = sorted((Path.home() / ".cache/ms-playwright").glob("chromium-*/chrome-linux64/chrome"))
    return str(builds[-1])


def open_context(pw, **kwargs):
    return pw.chromium.launch_persistent_context(
        PROFILE, executable_path=chromium_path(), headless=False, **kwargs
    )


def session():
    return sync_playwright()
