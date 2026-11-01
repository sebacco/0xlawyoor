from .base import SiteAdapter

# Taobao's English UI is an account/app language setting; the web search page
# accepts English queries but Chinese terms (``zh:`` in reminder notes) match
# far more listings. Search requires a logged-in session.
TAOBAO = SiteAdapter(
    key="taobao",
    label="Taobao",
    search_url="https://s.taobao.com/search?q={q}",
    product_link=r"(item\.taobao\.com/item\.htm|detail\.tmall\.com/item\.htm).*[?&]id=\d+",
    price_hint=r"(¥|￥)\s?\d[\d,]*(\.\d{1,2})?|\d[\d,]*\.\d{1,2}",
    currency="CNY",
    chinese_site=True,
    cart_buttons=(
        "button:has-text('Add to cart')",
        "a:has-text('Add to cart')",
        "text=加入购物车",
        "#J_LinkBasket",
    ),
    login_hint="Log in to Taobao (QR code via the Taobao app is easiest).",
)
