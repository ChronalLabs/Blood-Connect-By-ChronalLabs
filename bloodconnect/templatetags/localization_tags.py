from django import template

from bloodconnect.i18n import translate_text
from bloodconnect.i18n import TRANSLATIONS, get_current_language
import json
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def t(text):
    return translate_text(text)


@register.simple_tag
def translations_json():
    """Return the translations dict for the current language as JSON (safe).

    This is intended for embedding into frontend JS as window.TRANSLATIONS.
    """
    code = get_current_language()
    data = TRANSLATIONS.get(code, {})
    # ensure unicode characters are preserved
    return mark_safe(json.dumps(data, ensure_ascii=False))
