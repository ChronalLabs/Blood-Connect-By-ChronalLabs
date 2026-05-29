from django import template

from bloodconnect.i18n import translate_text

register = template.Library()


@register.simple_tag
def t(text):
    return translate_text(text)
