from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ShoppingItem:
    """One line from the Reminders list."""

    name: str
    reminder_id: str | None = None
    notes: str = ""

    @property
    def query_overrides(self) -> dict[str, str]:
        """Per-site search terms parsed from reminder notes.

        Notes lines such as ``zh: 洗衣液`` or ``amazon: tide pods 81ct`` let the
        family tune searches without renaming the reminder. ``zh`` applies to
        the Chinese-language sites (Taobao, Pinduoduo).
        """
        out: dict[str, str] = {}
        for line in (self.notes or "").splitlines():
            key, sep, value = line.partition(":")
            if sep and value.strip():
                out[key.strip().lower()] = value.strip()
        return out

    def query_for(self, site_key: str, chinese_site: bool) -> str:
        o = self.query_overrides
        if site_key in o:
            return o[site_key]
        if chinese_site and "zh" in o:
            return o["zh"]
        return self.name


@dataclass
class Offer:
    site: str
    item: str
    title: str
    url: str
    price: float | None
    currency: str
    price_hkd: float | None = None
    raw_price: str = ""


@dataclass
class CartResult:
    offer: Offer
    status: str  # "added" | "manual" | "saved" | "failed"
    detail: str = ""


@dataclass
class Comparison:
    item: ShoppingItem
    offers: list[Offer] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)

    def best(self) -> Offer | None:
        priced = [o for o in self.offers if o.price_hkd is not None]
        return min(priced, key=lambda o: o.price_hkd) if priced else None
