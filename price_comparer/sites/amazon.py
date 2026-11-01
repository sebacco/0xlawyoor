from dataclasses import replace

from .base import SiteAdapter

_CURRENCY_BY_DOMAIN = {"amazon.com": "USD", "amazon.co.jp": "JPY", "amazon.co.uk": "GBP", "amazon.de": "EUR"}


def make_amazon(domain: str = "amazon.com") -> SiteAdapter:
    """Amazon adapter. Set ship-to = Hong Kong in the browser so prices and
    'ships to HK' filtering reflect your delivery address."""
    base = SiteAdapter(
        key="amazon",
        label=f"Amazon ({domain})",
        search_url=f"https://www.{domain}/s?k={{q}}&language=en_US",
        product_link=r"/(dp|gp/product)/[A-Z0-9]{10}",
        price_hint=r"(HK\$|US\$|\$|¥|￥|£|€)\s?\d[\d,]*(\.\d{1,2})?",
        currency=_CURRENCY_BY_DOMAIN.get(domain, "USD"),
        cart_buttons=("#add-to-cart-button", "input[name='submit.add-to-cart']",
                      "button:has-text('Add to Cart')"),
        login_hint=f"Sign in to {domain} and set the delivery location to Hong Kong.",
    )
    return replace(base)


AMAZON = make_amazon()
