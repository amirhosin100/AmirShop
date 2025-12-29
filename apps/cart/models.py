from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from base.base_models import BaseModel


class CartManager(models.Manager):

    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @transaction.atomic
    def set(self, user, product, quantity=1):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        cart = self.get_cart(user)

        item, _ = cart.items.get_or_create(product=product)
        item.quantity = quantity
        item.save()

        return item

    @transaction.atomic
    def add(self, user, product):
        cart = self.get_cart(user)
        item, is_created = cart.items.get_or_create(product=product)

        if not is_created:
            item.quantity += 1

        item.save()

        return item

    @transaction.atomic
    def decrease(self, user, product):
        cart = self.get_cart(user)

        if cart.items.filter(product=product).exists():
            item = cart.items.get(product=product)
            if item.quantity > 1:
                item.quantity -= 1
                item.save()

        else:
            raise ValueError("Product not in cart")

        return item

    @transaction.atomic
    def remove(self, user, product):
        cart = self.get_cart(user)

        if cart.items.filter(product=product).exists():
            item = cart.items.get(product=product)
            item.delete()
        else:
            raise ValueError("Product not in cart")

        return True

    @transaction.atomic
    def clear(self, user):
        cart = self.get_cart(user)
        for item in cart.items.all():
            item.delete()

        return cart


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

    manage_items = CartManager()

    objects = models.Manager()

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

    class Meta(BaseModel.Meta):
        unique_together = (("cart", "product"),)

    def __str__(self):
        return f"{str(self.product)} : {self.final_price}"

    def save(self, *args, **kwargs):
        self.final_price = self.quantity * self.product.discount_price
        super().save(*args, **kwargs)
