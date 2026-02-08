from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from apps.market.models import Market
from core.cache.invalidation import invalidate_market_list,invalidate_market_detail


@receiver([post_save,pre_delete], sender=Market)
def invalidate_cache_market(sender, instance, **kwargs):
    invalidate_market_list()
    invalidate_market_detail(instance.id)