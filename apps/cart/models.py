from django.db import models
from django.utils.translation import gettext_lazy as _

from base.base_models import BaseModel


# Create your models here.

class Cart(BaseModel):
    user = models.OneToOneField(
        "user.User",
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("User"),
    )

    amount = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Amount")
    )

    def __str__(self):
        return f"{str(self.user)} : {self.amount}"



class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Cart"),
    )

    product = models.ForeignKey(
        "product.Product",
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("quantity")
    )

    final_price = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Final price")
    )

    def __str__(self):
        return f"{str(self.product)} : {self.final_price}"

    def save(self, *args, **kwargs):
        self.final_price = self.quantity * self.product.discount_price
        super().save(*args, **kwargs)