"""Runs the in-page extractor against a fixture in headless Chromium."""
import os
from pathlib import Path

import pytest

from price_comparer.models import ShoppingItem
from price_comparer.sites import SITES

pw = pytest.importorskip("playwright.sync_api")
FIXTURE = Path(__file__).parent / "fixtures" / "search.html"
CHROMIUM = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")


@pytest.fixture(scope="module")
def page():
    with pw.sync_playwright() as p:
        kw = {"executable_path": CHROMIUM} if Path(CHROMIUM).exists() else {}
        try:
            browser = p.chromium.launch(**kw)
        except Exception as e:
            pytest.skip(f"no chromium: {e}")
        yield browser.new_page()
        browser.close()


def test_hktvmall_extraction(page):
    site = SITES["hktvmall"]
    site_local = type(site)(**{**site.__dict__, "search_url": FIXTURE.as_uri() + "?q={q}"})
    site_local.after_search_load = lambda page: None
    offers = site_local.search(page, ShoppingItem("detergent"), limit=5)
    assert [(o.title, o.price, o.currency) for o in offers] == [
        ("Tide Pods Laundry Detergent 81ct", 1189.5, "HKD"),
        ("Ariel Liquid 2L", 89.9, "HKD"),
    ]
