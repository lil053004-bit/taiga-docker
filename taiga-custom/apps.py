from django.apps import AppConfig
import os

class CustomConfig(AppConfig):
    name = 'custom'
    verbose_name = 'Taiga Custom Auto-Assign'

    def ready(self):
        import custom.signals

        if os.environ.get('RUN_MAIN') != 'true':
            from django.core.management import call_command
            try:
                call_command('initialize_taiga')
            except Exception as e:
                print(f'Initialization skipped or already complete: {e}')
