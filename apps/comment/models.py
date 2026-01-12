from django.db import models

from base.base_models import BaseModel
from django.utils.translation import gettext_lazy as _


class CommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='PUBLISHED')


class Comment(BaseModel):
    class CommentStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PUBLISHED = 'PUBLISHED', _('Published')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('User'),
    )

    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Product'),
    )

    content = models.TextField(
        max_length=1000,
        verbose_name=_('Comment'),
    )

    status = models.CharField(
        max_length=10,
        choices=CommentStatus.choices,
        default=CommentStatus.DRAFT,
        verbose_name=_('Status'),
    )

    objects = models.Manager()
    published = CommentManager()

    score = models.FloatField(
        verbose_name=_('Score'),
    )

    class Meta(BaseModel.Meta):
        indexes = BaseModel.Meta.indexes + [
            models.Index(fields=['status'], name='comment_status_index'),
        ]

    def __str__(self):
        return f'{self.user.get_full_name()} : {self.content[:20]}'




class CommentImage(BaseModel):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Comment'),
    )

    image = models.ImageField(
        upload_to='comment/images/%Y/%m/%d',
        verbose_name=_('Image'),
    )

    def __str__(self):
        return f'image with id : {self.id}'
