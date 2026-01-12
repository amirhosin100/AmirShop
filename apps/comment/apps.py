from django.apps import AppConfig


class CommentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.comment'

    def ready(self):
        import apps.comment.signals
