from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

register = template.Library()

@register.filter
def unescape(value):
    return mark_safe(force_unicode(value).replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'").replace('&amp;', '&'))
