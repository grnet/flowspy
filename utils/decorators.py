from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def shib_required(f):
    def wrap(request, *args, **kwargs):
        if 'HTTP_SHIB_SESSION_ID' not in request.META or not request.META['HTTP_SHIB_SESSION_ID']:
            return HttpResponseRedirect(reverse('login'))
        return f(request, *args, **kwargs)

    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap
