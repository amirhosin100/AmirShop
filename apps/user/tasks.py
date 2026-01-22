from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from apps.user.models import OTP
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def remove_temp_opts():
    now = timezone.now()
    opts = OTP.objects.filter(created_at__lt=now - timedelta(hours=1))
    count = opts.count()

    if count:
        opts.delete()
        logger.info(f'{count} Expired opts have been deleted')
    else:
        logger.info('There was no expired opts!')
