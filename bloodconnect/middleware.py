"""Request middleware for activating the selected interface language."""

from django.utils import translation

from .i18n import DEFAULT_LANGUAGE, LANGUAGE_SESSION_KEY, normalize_language_code


class LanguagePreferenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_language = request.session.get(LANGUAGE_SESSION_KEY, DEFAULT_LANGUAGE)
        query_language = request.GET.get("lang")

        if query_language:
            session_language = normalize_language_code(query_language)
            request.session[LANGUAGE_SESSION_KEY] = session_language

        active_language = normalize_language_code(session_language)
        translation.activate(active_language)
        request.LANGUAGE_CODE = active_language

        response = self.get_response(request)
        response["Content-Language"] = active_language
        translation.deactivate()
        return response
