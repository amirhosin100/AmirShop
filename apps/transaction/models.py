from django.db import models
from base.base_models import BaseModel
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Transaction(BaseModel):
    user = models.ForeignKey(
        "user.User",
        on_delete=models.SET_DEFAULT,
        related_name="transactions",
        default=None,
        null=True,
        blank=True,
        verbose_name=_("User"),
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name=_("First Name")
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name=_("Last Name")
    )

    mobile_number = models.CharField(
        max_length=11,
        verbose_name=_("Mobile Number"),
    )

    final_price = models.PositiveIntegerField(
        verbose_name=_("Final Price"),
    )

    description = models.JSONField(
        verbose_name=_("Description"),
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name=_("Is Paid"),
    )

    class Meta(BaseModel.Meta):
        ordering = BaseModel.Meta.ordering + [
            "is_paid",
        ]
        indexes = BaseModel.Meta.indexes + [
            models.Index(fields=["is_paid"]),
            models.Index(fields=["mobile_number"]),
            models.Index(fields=["first_name","last_name"]),
        ]


    def __str__(self):
        return f"{self.mobile_number} : {self.final_price}"


