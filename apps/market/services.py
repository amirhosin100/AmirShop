from django.core.paginator import Paginator
from core.cache.ttl import CacheTTL
from core.cache.backend import CacheBackend
from core.cache.keys import market_list_key, market_detail_key
from apps.market.models import Market
from apps.market.serializer.market_serializer import MarketUserSerializer


class MarketService:
    @staticmethod
    def load_market_list(page=1):
        key = market_list_key(page)
        cached = CacheBackend.get(key)

        if cached:
            return cached

        return False

    @staticmethod
    def save_market_list(data,page=1):
        key = market_list_key(page)
        CacheBackend.set(key, data, CacheTTL.MARKET_DETAIL)

        return True

    @staticmethod
    def load_market_detail(market_id: str):
        key = market_detail_key(market_id)
        cached = CacheBackend.get(key)
        if cached:
            return cached

        return False

    @staticmethod
    def save_market_detail(data,market_id: str):
        key = market_detail_key(market_id)
        CacheBackend.set(key, data, CacheTTL.MARKET_DETAIL)

        return True
