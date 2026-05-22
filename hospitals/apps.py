from django.apps import AppConfig


class HospitalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hospitals"
    verbose_name = "Hospitals"

    def ready(self):
        """
        Initialize hospital app signals or startup hooks.
        """
        pass