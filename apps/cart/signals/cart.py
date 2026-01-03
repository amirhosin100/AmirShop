from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from apps.cart.models import Cart,CartItem

def change_cart_amount(instance):
    amount = 0
    for item in instance.cart.items.all():
        amount += item.final_price
    instance.cart.amount = amount
    instance.cart.save()

@receiver(post_save, sender=CartItem)
def change_cart_amount_post_save(sender, instance, **kwargs):
    change_cart_amount(instance)

@receiver(post_delete, sender=CartItem)
def change_cart_amount_post_delete(sender, instance, **kwargs):
    change_cart_amount(instance)



