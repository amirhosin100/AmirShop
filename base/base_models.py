from django.db import models
from uuid import uuid4


class BaseModel(models.Model):

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=[
                "-created_at",
            ])
        ,]
