from django.apps import AppConfig


class FueltaxesapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Direct.Apps.FueltaxesApi'
    
    def ready(self):
        import Direct.Apps.FueltaxesApi.signals 
