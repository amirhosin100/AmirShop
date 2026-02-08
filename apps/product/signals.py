from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from apps.product.models import Product
from core.cache.invalidation import invalidate_product_list,invalidate_product_detail


@receiver([post_save,pre_delete], sender=Product)
def invalidate_cache_product(sender, instance, **kwargs):
    invalidate_product_list()
    invalidate_product_detail(instance.id)