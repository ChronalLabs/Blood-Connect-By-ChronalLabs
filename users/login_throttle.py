"""
Helpers for login throttling and temporary lockouts.
"""

from django.core.cache import cache

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60
THROTTLE_PREFIX = "bloodconnect:login"


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "").strip()


def _normalize_identifier(value):
    return (value or "").strip().lower()


def _attempts_key(scope, kind, value):
    return f"{THROTTLE_PREFIX}:{scope}:{kind}:{_normalize_identifier(value)}:attempts"


def _lock_key(scope, kind, value):
    return f"{THROTTLE_PREFIX}:{scope}:{kind}:{_normalize_identifier(value)}:locked"


def is_login_locked(scope, username, ip_address):
    identifiers = []
    if username:
        identifiers.append(("user", username))
    if ip_address:
        identifiers.append(("ip", ip_address))

    return any(cache.get(_lock_key(scope, kind, value)) for kind, value in identifiers)


def register_login_failure(scope, username, ip_address):
    identifiers = []
    if username:
        identifiers.append(("user", username))
    if ip_address:
        identifiers.append(("ip", ip_address))

    locked = False
    for kind, value in identifiers:
        attempts_key = _attempts_key(scope, kind, value)
        if not cache.add(attempts_key, 1, LOCKOUT_SECONDS):
            try:
                attempts = cache.incr(attempts_key)
            except ValueError:
                attempts = 1
                cache.set(attempts_key, attempts, LOCKOUT_SECONDS)
        else:
            attempts = 1

        if attempts >= MAX_LOGIN_ATTEMPTS:
            cache.set(_lock_key(scope, kind, value), True, LOCKOUT_SECONDS)
            locked = True

    return locked


def reset_login_throttle(scope, username, ip_address):
    identifiers = []
    if username:
        identifiers.append(("user", username))
    if ip_address:
        identifiers.append(("ip", ip_address))

    for kind, value in identifiers:
        cache.delete(_attempts_key(scope, kind, value))
        cache.delete(_lock_key(scope, kind, value))
