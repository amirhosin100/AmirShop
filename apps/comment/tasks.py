import logging
from celery import shared_task
from django.db.models import Avg, Count

from apps.product.models import Product
from apps.user.models import Marketer
from core.comment.summarizing import CommentSummarizing
import asyncio

logger = logging.getLogger(__name__)


@shared_task
def calculate_score():
    for marketer in Marketer.objects.all():
        for market in marketer.markets.all():
            market.score = market.products.aggregate(Avg('score'))['score__avg']
            market.save()
        marketer.score = marketer.markets.aggregate(Avg('score'))['score__avg']
        marketer.save()

    logger.info('Scores went updated')


@shared_task
def summarizing_comments():
    summarizer = CommentSummarizing()

    products = Product.objects.annotate(Count('comments'))
    products = list(products.filter(comments__count__gte=0))

    asyncio.run(summarizer.summarize_from_query_set(products))
