from django.db import models
from base.base_models import BaseModel
from django.utils.translation import gettext_lazy as _

# Create your models here.

class MarketRequest(BaseModel):
    user = models.ForeignKey(
       "user.User",
        on_delete=models.SET_NULL,
        related_name="market_requests",
        null=True,
        verbose_name=_("User"),
    )

    mobile_number = models.CharField(
        max_length=11,
        verbose_name=_("Mobile Number"),
    )

    city = models.CharField(
        max_length=30,
        verbose_name=_("City"),
    )

    national_code = models.CharField(
        max_length=10,
        verbose_name=_("National Code"),
    )

    province = models.CharField(
        max_length=30,
        verbose_name=_("Province"),
    )

    address = models.CharField(
        max_length=200,
        verbose_name=_("Address"),
    )

    description = models.TextField(
        verbose_name=_("Description"),
    )
    age = models.PositiveIntegerField(
        verbose_name=_("Age"),
    )

    class Meta(BaseModel.Meta):
        indexes = BaseModel.Meta.indexes + [
            models.Index(fields=["city"]),
        ]
        verbose_name = _("Market Request")
        verbose_name_plural = _("Market Requests")

    def __str__(self):
        return f"{self.user.get_full_name()[:20]} : {self.mobile_number}"
