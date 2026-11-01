from .base import SiteAdapter

# Pinduoduo has no English version and no shopping cart (it is buy-now /
# group-buy only). The adapter compares prices via the mobile web site and
# saves chosen items to the local cart file for manual purchase in the app.
PINDUODUO = SiteAdapter(
    key="pinduoduo",
    label="Pinduoduo",
    search_url="https://mobile.yangkeduo.com/search_result.html?search_key={q}",
    product_link=r"yangkeduo\.com/goods\d?\.html\?.*goods_id=\d+",
    price_hint=r"(¥|￥)\s?\d[\d,]*(\.\d{1,2})?",
    currency="CNY",
    chinese_site=True,
    has_cart=False,
    mobile=True,
    login_hint="Log in to mobile.yangkeduo.com with your phone number (SMS code).",
)
