import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )

    title = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_("Title"),
    )

    description = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name=_("Description"),
    )

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
        ]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="sub_categories",
    )

    title = models.CharField(
        max_length=50,
    )

    class Meta:
        indexes = [
            models.Index(fields=["title","category"]),
        ]
        unique_together = ("title","category")
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return f"{self.title} : {self.category.title}"

