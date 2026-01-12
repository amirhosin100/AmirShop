from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg

from apps.comment.models import Comment


def change_product_score(instance):
    query = Comment.published.filter(product=instance.product)
    final_score = query.aggregate(avg=Avg('score'))['avg']
    instance.product.score = final_score

    instance.product.save()


@receiver(post_save, sender=Comment)
def update_score_to_product(sender, instance, **kwargs):
    change_product_score(instance)


@receiver(post_delete, sender=Comment)
def update_score_to_product(sender, instance, **kwargs):
    change_product_score(instance)
