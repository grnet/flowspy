from django import template
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
