import logging
from celery import shared_task
from django.db.models import Avg
from apps.user.models import Marketer

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
