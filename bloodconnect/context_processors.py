"""Context processors for language-related template state."""

from .i18n import SUPPORTED_LANGUAGES, get_current_language, get_language_label


def language_context(request):
    current_language = get_current_language(getattr(request, "LANGUAGE_CODE", None))
    return {
        "current_language": current_language,
        "current_language_label": get_language_label(current_language),
        "supported_languages": [
            {"code": code, "label": label}
            for code, label in SUPPORTED_LANGUAGES.items()
        ],
    }
