from django.apps import AppConfig


class ProductConfig(AppConfig):
    name = 'apps.product'

    def ready(self):
        import apps.product.signals
