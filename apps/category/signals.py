from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from apps.category.models import Category, SubCategory
from core.cache.invalidation import invalidate_category_list, invalidate_category_detail

def invalid(category_id):
    invalidate_category_list()
    invalidate_category_detail(category_id)

@receiver([post_save,pre_delete], sender=Category)
def invalidate_cache(sender, instance, **kwargs):
    invalid(instance.pk)


@receiver([post_save,pre_delete], sender=SubCategory)
def invalidate_cache(sender, instance, **kwargs):
    invalidate_category_detail(instance.category.id)


