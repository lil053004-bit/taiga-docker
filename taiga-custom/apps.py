from django.apps import AppConfig

class CustomConfig(AppConfig):
    name = 'custom'
    verbose_name = 'Taiga Custom Auto-Assign'

    def ready(self):
        import custom.signals
