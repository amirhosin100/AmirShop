from .backend import AIBackend
from apps.product.models import Product
from apps.comment.models import Comment
import logging

logger = logging.getLogger(__name__)


class CommentSummarizing:
    initial_text = """
    من از تو می خواهم که این کامنت ها رو بگیری و آنها را در 4 خط خلاصه بنویسی
    بدون هیچ گونه ایموجی یا پیام اضافه
    اگر کامنتی وجود نداشت یا کامنت ها مفید نبودند هیچ پیامی ارسال نکن
    """

    def __init__(self):
        self.backend = AIBackend()

    def summarize_product(self, product: Product):
        text = ""
        comments = Comment.objects.filter(product=product)
        number = 1
        for comment in comments.all():
            text += f"{number} : {comment.content}\n"
            number += 1

        result = self.backend.send_message(
            f"{self.initial_text}\n{text}",
        )
        if result and len(result) <= 2000:
            product.summary_comments = result
            product.save()
            logger.info(f'created summary for product with id : {product.pk}')
        else:
            logger.error(
                "Summarizing product failed"
                "Product id is {%s}" % product.id
            )

    def summarize_from_query_set(self, queryset):
        for product in queryset:
            self.summarize_product(product)
