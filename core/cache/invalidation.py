from core.cache.backend import CacheBackend
from core.cache.keys import product_detail_key, market_detail_key


def invalidate_product_list():
    CacheBackend.delete_prefix("product:list")


def invalidate_market_list():
    CacheBackend.delete_prefix("market:list")


def invalidate_market_detail(market_id: str):
    CacheBackend.delete_prefix(market_detail_key(market_id))


def invalidate_product_detail(product_id: str):
    CacheBackend.delete_prefix(product_detail_key(product_id))
