from django.apps import AppConfig


class AiCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_core'
    
    def ready(self):
        import ai_core.signals