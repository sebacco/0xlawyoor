"""Persistent browser profile so you log in to each marketplace yourself, once.

No passwords are stored by this tool; cookies live in the Chromium profile
directory (default ``~/.price-comparer/profile``) on your own machine.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

DEFAULT_PROFILE = Path.home() / ".price-comparer" / "profile"


@contextmanager
def open_browser(profile_dir: Path = DEFAULT_PROFILE, headless: bool = False,
                 channel: str | None = "chrome", executable_path: str | None = None):
    from playwright.sync_api import sync_playwright

    profile_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        kwargs = dict(headless=headless, locale="en-HK", viewport={"width": 1366, "height": 900})
        if executable_path:
            kwargs["executable_path"] = executable_path
        elif channel:
            kwargs["channel"] = channel
        try:
            ctx = p.chromium.launch_persistent_context(str(profile_dir), **kwargs)
        except Exception:
            kwargs.pop("channel", None)  # Chrome not installed -> bundled Chromium
            ctx = p.chromium.launch_persistent_context(str(profile_dir), **kwargs)
        try:
            yield p, ctx
        finally:
            ctx.close()


def page_for(p, ctx, adapter):
    """Desktop tab, or an iPhone-emulated tab for mobile-only sites."""
    if not adapter.mobile:
        return ctx.new_page()
    page = ctx.new_page()
    device = p.devices["iPhone 13"]
    page.set_viewport_size(device["viewport"])
    page.set_extra_http_headers({"User-Agent": device["user_agent"]})
    return page
