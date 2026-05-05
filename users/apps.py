from django.apps import AppConfig
from django.core import checks


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        checks.register(_check_field_encryption_key)


@checks.register(checks.Tags.security)
def _check_field_encryption_key(app_configs, **kwargs):
    from django.conf import settings
    key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
    if not key:
        return [
            checks.Warning(
                "FIELD_ENCRYPTION_KEY is not set. "
                "Aadhaar card numbers cannot be encrypted without it.",
                hint=(
                    "Set FIELD_ENCRYPTION_KEY in your environment. "
                    "Generate a key with: "
                    "python -c \"from cryptography.fernet import Fernet; "
                    "print(Fernet.generate_key().decode())\""
                ),
                id="users.W001",
            )
        ]
    return []
