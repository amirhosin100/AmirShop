from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.cart.models import Cart,CartItem

@receiver(post_save, sender=CartItem)
def change_cart_amount(sender, instance, **kwargs):
    amount = 0
    for item in instance.cart.items.all():
        amount += item.final_price
    print(amount)
    instance.cart.amount = amount
    instance.cart.save()



