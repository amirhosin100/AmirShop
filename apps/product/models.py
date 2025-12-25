from django.db import models
from apps.market.models import Market
from base.base_models import BaseModel
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

def get_product_path(instance, filename):
    return f"{instance.market.name}/{instance.name}/{filename}"

class Product(BaseModel):
    market = models.ForeignKey(
        Market,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Market'),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=pgettext_lazy("Product name", "name"),
    )
    description = models.TextField(
        max_length=2000,
        blank=True,
        null=True,
        verbose_name=_("Description"),
    )
    price = models.PositiveIntegerField(
        verbose_name=_("Price"),
    )
    percentage_off = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Percentage off"),
    )
    discount_price = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Discount price"),
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Stock"),
    )

    def __str__(self):
        return self.name

    class Meta(BaseModel.Meta):
        ordering = BaseModel.Meta.ordering + [
            'name'
        ]
        indexes = BaseModel.Meta.indexes + [
            models.Index(fields=['name'])
        ]
    
    def save(self, *args, **kwargs):
        self.discount_price = self.price - (self.price * self.percentage_off/100)
        super().save(*args,**kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Product'),
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Title"),
    )

    image = models.ImageField(
        upload_to=get_product_path,
        verbose_name=_("Image"),
    )

    def __str__(self):
        return self.title

class ProductFeature(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='features'
    )
    key = models.CharField(
        max_length=255,
    )
    value = models.CharField(
        max_length=255,
    )

    class Meta:
        unique_together = ['product', 'key']

    def __str__(self):
        return f"{self.key} : {self.value}"

