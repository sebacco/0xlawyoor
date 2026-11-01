"""Site adapter base class.

Each marketplace changes its markup often, so extraction is heuristic rather
than tied to brittle CSS classes: find product links by URL pattern, climb to
the enclosing card, read the first price-like text in it. Adapters only
declare URL patterns, currency and add-to-cart buttons.
"""
from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass

from ..models import CartResult, Offer, ShoppingItem
from ..pricing import parse_price

EXTRACT_JS = r"""
([linkPattern, priceHint, limit]) => {
  const linkRe = new RegExp(linkPattern);
  const priceRe = new RegExp(priceHint);
  const seen = new Set();
  const out = [];
  for (const a of document.querySelectorAll('a[href]')) {
    const href = a.href;
    if (!linkRe.test(href)) continue;
    const key = href.split('#')[0].split('?')[0] + (href.match(/[?&](id|goods_id)=\d+/)||[''])[0];
    if (seen.has(key)) continue;
    let card = a, price = '';
    for (let i = 0; i < 7 && card; i++, card = card.parentElement) {
      const txt = card.innerText || '';
      const m = txt.match(priceRe);
      if (m) { price = m[0]; break; }
    }
    if (!price || !card) continue;
    const img = card.querySelector('img[alt]');
    const lines = (card.innerText || '').split('\n').map(s => s.trim())
      .filter(s => s.length > 3 && !priceRe.test(s));
    const title = (a.getAttribute('title') || (img && img.alt) || lines.sort((x, y) => y.length - x.length)[0] || '').trim();
    if (!title) continue;
    seen.add(key);
    out.push({title: title.slice(0, 160), url: href, price: price});
    if (out.length >= limit) break;
  }
  return out;
}
"""


@dataclass
class SiteAdapter:
    key: str = ""
    label: str = ""
    search_url: str = ""          # contains {q}
    product_link: str = ""        # regex for product page URLs
    price_hint: str = r"(HK\$|US\$|\$|¥|￥)\s?\d[\d,]*(\.\d{1,2})?"
    currency: str = "HKD"
    chinese_site: bool = False
    has_cart: bool = True
    cart_buttons: tuple[str, ...] = ()   # CSS/text selectors, tried in order
    mobile: bool = False                 # emulate a phone (Pinduoduo)
    login_hint: str = ""

    # -- search -----------------------------------------------------------
    def build_search_url(self, query: str) -> str:
        return self.search_url.format(q=urllib.parse.quote(query))

    def search(self, page, item: ShoppingItem, limit: int = 5) -> list[Offer]:
        query = item.query_for(self.key, self.chinese_site)
        page.goto(self.build_search_url(query), wait_until="domcontentloaded", timeout=45_000)
        self.after_search_load(page)
        rows = page.evaluate(EXTRACT_JS, [self.product_link, self.price_hint, limit])
        return [self._to_offer(item, r) for r in rows]

    def after_search_load(self, page) -> None:
        """Give client-rendered result grids time to paint."""
        try:
            page.wait_for_load_state("networkidle", timeout=12_000)
        except Exception:
            pass
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(1500)

    def _to_offer(self, item: ShoppingItem, row: dict) -> Offer:
        value, cur = parse_price(row.get("price", ""), self.currency)
        return Offer(site=self.label, item=item.name, title=row["title"], url=row["url"],
                     price=value, currency=cur, raw_price=row.get("price", ""))

    # -- cart -------------------------------------------------------------
    def add_to_cart(self, page, offer: Offer) -> CartResult:
        if not self.has_cart:
            return CartResult(offer, "saved", f"{self.label} has no cart; link saved to local cart file.")
        page.goto(offer.url, wait_until="domcontentloaded", timeout=45_000)
        page.wait_for_timeout(2500)
        for sel in self.cart_buttons:
            loc = page.locator(sel).first
            try:
                if loc.is_visible(timeout=2500):
                    loc.click(timeout=5000)
                    page.wait_for_timeout(2500)
                    return CartResult(offer, "added", f"clicked {sel}")
            except Exception:
                continue
        return CartResult(offer, "manual", "Add-to-cart button not found (variant/size picker or login needed).")


def compile_check(adapter: SiteAdapter) -> None:
    re.compile(adapter.product_link)
    re.compile(adapter.price_hint)
