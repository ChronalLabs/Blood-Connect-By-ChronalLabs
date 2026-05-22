from django.apps import AppConfig


class DonorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "donors"

    verbose_name = "Blood Donor Management"

    def ready(self):
        """
        Initialize signals, schedulers,
        or startup tasks for the donors app.
        """
        try:
            import donors.signals  # noqa
        except ImportError:
            pass