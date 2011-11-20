# Create your views here.
import urllib2
import re
import socket
from django import forms
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.core.context_processors import request
from django.template.context import RequestContext
from django.template.loader import get_template
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib import messages

from flowspy.flowspec.models import *

def user_routes(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse('login'))
    user_routes = Route.objects.filter(applier=request.user)
    print user_routes
    return render_to_response('user_routes.html', {'routes': user_routes},
                              context_instance=RequestContext(request))


