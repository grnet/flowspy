from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
import socket

register = template.Library()


@register.filter
def tofqdn(value):
    try:
        fqdn = socket.getfqdn(value)
        if fqdn == value:
            return False
        else:
            return fqdn
    except:
        return False
