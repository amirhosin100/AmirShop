from core.cache.backend import CacheBackend
from core.cache.keys import product_list_key, product_detail_key
from core.cache.ttl import CacheTTL


class ProductService:
    @staticmethod
    def load_product_list(page=1,query=""):
        key = product_list_key(page,query)
        cached = CacheBackend.get(key)
        if cached:
            return cached

        return False

    @staticmethod
    def save_product_list(data, page,query=""):
        key = product_list_key(page,query)
        CacheBackend.set(key, data, CacheTTL.PRODUCT_LIST)

        return True

    @staticmethod
    def load_product_detail(product_id: str):
        key = product_detail_key(product_id)
        cached = CacheBackend.get(key)
        if cached:
            return cached

        return False

    @staticmethod
    def save_product_detail(data, product_id):
        key = product_detail_key(product_id)
        CacheBackend.set(key, data, CacheTTL.PRODUCT_DETAIL)

        return True
