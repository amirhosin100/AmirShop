from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from apps.cart.models import CartItem
from django.db.models import Sum


def change_cart_amount(instance):
    amount = instance.cart.items.aggregate(amount=Sum('final_price'))['amount']
    if amount:
        instance.cart.amount = amount
    else:
        instance.cart.amount = 0
    instance.cart.save()

@receiver(post_save, sender=CartItem)
def change_cart_amount_post_save(sender, instance, **kwargs):
    change_cart_amount(instance)

@receiver(post_delete, sender=CartItem)
def change_cart_amount_post_delete(sender, instance, **kwargs):
    change_cart_amount(instance)



