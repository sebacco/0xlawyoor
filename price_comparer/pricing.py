"""Price text parsing and HKD normalisation."""
from __future__ import annotations

import json
import re
import urllib.request

# Fallback rates (HKD per 1 unit). Refreshed live when --live-fx is used.
FALLBACK_HKD_RATES = {"HKD": 1.0, "CNY": 1.09, "USD": 7.78, "JPY": 0.052, "GBP": 10.0, "EUR": 8.6}

_CURRENCY_MARKERS = [
    ("HK$", "HKD"), ("HKD", "HKD"),
    ("US$", "USD"), ("USD", "USD"),
    ("RMB", "CNY"), ("CNY", "CNY"), ("CN¥", "CNY"),
    ("JP¥", "JPY"), ("JPY", "JPY"),
    ("£", "GBP"), ("€", "EUR"),
]
_NUMBER = re.compile(r"(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?")


def parse_price(text: str, default_currency: str) -> tuple[float | None, str]:
    """Extract the first price from ``text``.

    Bare ``$``/``¥``/``￥`` symbols resolve to the site's default currency, so
    ``¥`` means CNY on Taobao but JPY on amazon.co.jp.
    """
    if not text:
        return None, default_currency
    t = text.replace("\xa0", " ")
    currency = default_currency
    upper = t.upper()
    for marker, code in _CURRENCY_MARKERS:
        if marker.upper() in upper:
            currency = code
            break
    m = _NUMBER.search(t)
    if not m:
        return None, currency
    whole = m.group(1).replace(",", "")
    value = float(f"{whole}.{m.group(2)}" if m.group(2) else whole)
    return value, currency


def to_hkd(amount: float | None, currency: str, rates: dict[str, float]) -> float | None:
    if amount is None or currency not in rates:
        return None
    return round(amount * rates[currency], 2)


def fetch_live_rates(timeout: float = 8.0) -> dict[str, float]:
    """HKD-per-unit rates from open.er-api.com (free, no key)."""
    with urllib.request.urlopen("https://open.er-api.com/v6/latest/HKD", timeout=timeout) as r:
        data = json.load(r)
    per_hkd = data["rates"]  # units of X per 1 HKD
    return {code: round(1 / per_hkd[code], 6) for code in FALLBACK_HKD_RATES if per_hkd.get(code)}
