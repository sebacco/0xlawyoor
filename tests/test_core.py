import json
from pathlib import Path

import pytest

from price_comparer.models import Comparison, Offer, ShoppingItem
from price_comparer.pricing import parse_price, to_hkd, FALLBACK_HKD_RATES
from price_comparer.reminders import load_from_file, parse_reminders_json
from price_comparer.selection import parse_selection
from price_comparer.sites import SITES, make_amazon


@pytest.mark.parametrize("ans,expected", [
    ("1,3", [0, 2]), ("2-4", [1, 2, 3]), ("all", [0, 1, 2, 3, 4]), ("none", []), ("", []),
    ("5 1", [0, 4]), ("4-2", [1, 2, 3]),
])
def test_parse_selection(ans, expected):
    assert parse_selection(ans, 5) == expected


def test_parse_selection_out_of_range():
    with pytest.raises(ValueError):
        parse_selection("6", 5)


@pytest.mark.parametrize("text,default,expected", [
    ("$ 1,189.50", "HKD", (1189.5, "HKD")),
    ("HK$89.9", "USD", (89.9, "HKD")),
    ("¥ 39.90", "CNY", (39.9, "CNY")),
    ("￥12", "JPY", (12.0, "JPY")),
    ("US$24.99", "HKD", (24.99, "USD")),
    ("no price", "HKD", (None, "HKD")),
])
def test_parse_price(text, default, expected):
    assert parse_price(text, default) == expected


def test_to_hkd():
    assert to_hkd(10, "CNY", {"CNY": 1.09}) == 10.9
    assert to_hkd(None, "CNY", FALLBACK_HKD_RATES) is None
    assert to_hkd(1, "XYZ", FALLBACK_HKD_RATES) is None


def test_reminders_json_and_overrides():
    payload = json.dumps([
        {"id": "x-apple-reminder://1", "name": "Laundry detergent", "notes": "zh: 洗衣液\namazon: tide pods"},
        {"id": "x-apple-reminder://2", "name": "  ", "notes": None},
    ])
    items = parse_reminders_json(payload)
    assert len(items) == 1
    it = items[0]
    assert it.query_for("taobao", chinese_site=True) == "洗衣液"
    assert it.query_for("amazon", chinese_site=False) == "tide pods"
    assert it.query_for("hktvmall", chinese_site=False) == "Laundry detergent"


def test_items_file(tmp_path: Path):
    f = tmp_path / "list.txt"
    f.write_text("# comment\nMilk\nRice | zh: 大米; amazon: jasmine rice\n", encoding="utf-8")
    items = load_from_file(f)
    assert [i.name for i in items] == ["Milk", "Rice"]
    assert items[1].query_overrides == {"zh": "大米", "amazon": "jasmine rice"}


def test_best_offer():
    c = Comparison(item=ShoppingItem("x"))
    c.offers = [Offer("A", "x", "t", "u", 10, "HKD", 10), Offer("B", "x", "t", "u", 5, "CNY", 5.45),
                Offer("C", "x", "t", "u", None, "HKD", None)]
    assert c.best().site == "B"


def test_site_registry():
    assert set(SITES) == {"hktvmall", "taobao", "pinduoduo", "amazon"}
    assert "/en/" in SITES["hktvmall"].search_url
    assert SITES["pinduoduo"].has_cart is False
    jp = make_amazon("amazon.co.jp")
    assert jp.currency == "JPY" and "amazon.co.jp" in jp.build_search_url("tea")
