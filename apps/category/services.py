from core.cache.keys import category_detail_key, category_list_key
from core.cache.backend import CacheBackend
from core.cache.ttl import CacheTTL


class CategoryService:
    @staticmethod
    def load_list_category():
        key = category_list_key()
        cached = CacheBackend.get(key)
        if cached:
            return cached
        return False

    @staticmethod
    def load_detail_category(category_id: str):
        key = category_detail_key(category_id)
        cached = CacheBackend.get(key)
        if cached:
            return cached
        return False

    @staticmethod
    def save_list_category(data):
        key = category_list_key()
        result = CacheBackend.set(key, data, CacheTTL.CATEGORY_LIST)

        return result

    @staticmethod
    def save_detail_category(data, category_id: str):
        key = category_detail_key(category_id)
        result = CacheBackend.set(key, data, CacheTTL.CATEGORY_DETAIL)

        return result
