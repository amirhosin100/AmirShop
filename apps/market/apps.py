from celery.signals import import_modules
from django.apps import AppConfig


class MarketConfig(AppConfig):
    name = 'apps.market'

    def ready(self):
        import apps.market.signals
