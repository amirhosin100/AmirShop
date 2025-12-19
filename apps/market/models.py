from django.db import models
from base.base_models import BaseModel
from django_resized import ResizedImageField


class Market(BaseModel):
    marketer = models.ForeignKey(
        "user.Marketer",
        on_delete=models.PROTECT,
        related_name="markets",
    )
    name = models.CharField(
        max_length=255,
    )
    icon = ResizedImageField(
        upload_to="market/icons",
        crop=["center", "middle"],
        quality=100,
        size=[500, 500],
        null=True,
        blank=True,
    )
    bio = models.TextField(
        max_length=1000,
        null=True,
        blank=True,
    )
    number_phone_1 = models.CharField(
        max_length=11,
        null=True,
        blank=True,
    )
    number_phone_2 = models.CharField(
        max_length=11,
        null=True,
        blank=True,
    )
    website = models.URLField(
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.name} -- {self.marketer.user.get_full_name()}"
