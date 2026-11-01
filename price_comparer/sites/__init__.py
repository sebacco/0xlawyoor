from .amazon import AMAZON, make_amazon
from .base import SiteAdapter
from .hktvmall import HKTVMALL
from .pinduoduo import PINDUODUO
from .taobao import TAOBAO

SITES: dict[str, SiteAdapter] = {s.key: s for s in (HKTVMALL, TAOBAO, PINDUODUO, AMAZON)}

__all__ = ["SITES", "SiteAdapter", "make_amazon"]
