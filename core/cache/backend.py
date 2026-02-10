from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class CacheBackend:

    @staticmethod
    def get(key: str):
        value = cache.get(key)
        logger.info("CACHE GET %s -> %s", key, "HIT" if value else "MISS")
        return value

    @staticmethod
    def set(key, value, ttl):
        cache.set(key, value, ttl)
        logger.info("CACHE SET %s (ttl=%s)", key, ttl)
        return True

    @staticmethod
    def delete(key):
        cache.delete(key)
        logger.info("CACHE DELETE %s ", key)
        return True

    @staticmethod
    def delete_prefix(key):
        logger.info("CACHE DELETE_PREFIX %s", key)
        cache.delete_pattern(f"*{key}*")
