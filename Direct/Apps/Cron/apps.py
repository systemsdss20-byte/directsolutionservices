from django.apps import AppConfig


class CronConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Direct.Apps.Cron'

    def ready(self):
        from . import views
        views.start()
