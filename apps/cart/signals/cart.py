import logging
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from apps.cart.models import CartItem

logger = logging.getLogger(__name__)


def change_cart_amount(instance):
    amount = instance.cart.items.aggregate(amount=Sum('final_price'))['amount']
    instance.cart.amount = amount if amount else 0
    instance.cart.save()

    logger.info(f'cart with {instance.cart.id} is up to date')


@receiver(post_save, sender=CartItem)
def change_cart_amount_post_save(sender, instance, **kwargs):
    change_cart_amount(instance)


@receiver(post_delete, sender=CartItem)
def change_cart_amount_post_delete(sender, instance, **kwargs):
    change_cart_amount(instance)
