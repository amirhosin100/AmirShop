from .backend import AIBackend
from apps.product.models import Product
from apps.comment.models import Comment
from asgiref.sync import sync_to_async
import logging
import asyncio

logger = logging.getLogger(__name__)


class CommentSummarizing:
    initial_text = """
    من از تو می خواهم که این کامنت ها رو بگیری و آنها را در 4 خط خلاصه بنویسی
    بدون هیچ گونه ایموجی یا پیام اضافه
    اگر کامنتی وجود نداشت یا کامنت ها مفید نبودند هیچ پیامی ارسال نکن
    """

    def __init__(self):
        self.backend = AIBackend()

    @sync_to_async
    def get_comment_text(self, product_id):
        text = ""
        comments = Comment.objects.filter(product_id=product_id)
        number = 1
        for comment in comments.all():
            text += f"{number} : {comment.content}\n"
            number += 1

        return text

    @sync_to_async
    def save_summary(self, product, content):
        product.summary_comments = content
        product.save()

    async def summarize_product(self, product: Product):

        text = await self.get_comment_text(product.id)

        result = await self.backend.send_message(
            f"{self.initial_text}\n{text}",
        )
        if result and len(result) <= 2000:
            await self.save_summary(product, result)
            logger.info(f'created summary for product with id : {product.pk}')
        else:
            logger.error(
                "Summarizing product failed"
                "Product id is {%s}" % product.id
            )

    async def summarize_from_query_set(self, queryset):
        requests = [self.summarize_product(product) for product in queryset]

        for request in asyncio.as_completed(requests):
            await request
