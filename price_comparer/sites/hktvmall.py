from .base import SiteAdapter

HKTVMALL = SiteAdapter(
    key="hktvmall",
    label="HKTVmall",
    search_url="https://www.hktvmall.com/hktv/en/search_a?keyword={q}",
    product_link=r"hktvmall\.com/hktv/en/.*/p/[A-Z0-9_]+",
    price_hint=r"\$\s?\d[\d,]*(\.\d{1,2})?",
    currency="HKD",
    cart_buttons=(
        "button:has-text('Add to Cart')",
        "a:has-text('Add to Cart')",
        "[class*='addToCart']",
    ),
    login_hint="Sign in at hktvmall.com (English) once in the opened browser.",
)
