# --- FILE: core/apps.py (UPDATED CODE) ---

from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    # ADD THIS FUNCTION
    def ready(self):
        # This line imports your signals file, connecting the signals.
        import core.signals