"""
Custom encrypted model field using Fernet symmetric encryption.
The plaintext value is encrypted before being written to the database
and decrypted transparently when read back.
"""

import logging

from django.conf import settings
from django.db import models
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

_fernet_instance = None


def _get_fernet():
    global _fernet_instance
    if _fernet_instance is None:
        key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
        if not key:
            raise ValueError(
                "FIELD_ENCRYPTION_KEY must be set in settings to use EncryptedCharField."
            )
        _fernet_instance = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet_instance


class EncryptedCharField(models.TextField):
    """
    A TextField that transparently encrypts its value with Fernet before
    writing to the database and decrypts it when reading back.

    The column is stored as a TextField (ciphertext is ~100 chars for a
    12-digit input) so there is no length constraint at the DB level.
    The form/application layer enforces the plaintext max_length separately.
    """

    def __init__(self, *args, **kwargs):
        # Remember the plaintext max_length for form validation but don't pass
        # it to the parent TextField (which has no meaningful max_length).
        self.plaintext_max_length = kwargs.pop('max_length', None)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.plaintext_max_length is not None:
            kwargs['max_length'] = self.plaintext_max_length
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        return self._decrypt(value)

    def to_python(self, value):
        return self._decrypt(value)

    def get_prep_value(self, value):
        if value is None or value == '':
            return value
        return _get_fernet().encrypt(str(value).encode()).decode()

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _decrypt(value):
        if value is None or value == '':
            return value
        try:
            return _get_fernet().decrypt(value.encode()).decode()
        except InvalidToken:
            logger.error(
                "EncryptedCharField: decryption failed for a stored value. "
                "This may indicate a key mismatch or data corruption."
            )
            return ''
