from core.cache.backend import CacheBackend
from core.cache.keys import product_detail_key, market_detail_key, category_detail_key


def invalidate_product_list():
    CacheBackend.delete_prefix("product:list")


def invalidate_market_list():
    CacheBackend.delete("market:list")


def invalidate_category_list():
    CacheBackend.delete("category:list")


def invalidate_product_detail(product_id: str):
    CacheBackend.delete(product_detail_key(product_id))


def invalidate_market_detail(market_id: str):
    CacheBackend.delete(market_detail_key(market_id))


def invalidate_category_detail(category_id: str):
    CacheBackend.delete(category_detail_key(category_id))
