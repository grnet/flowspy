# Create your views here.
import urllib2
import re
import socket
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.core import urlresolvers
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.core.context_processors import request
from django.template.context import RequestContext
from django.template.loader import get_template
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib import messages

from flowspy.flowspec.forms import * 
from flowspy.flowspec.models import *

def days_offset(): return datetime.now() + timedelta(days = settings.EXPIRATION_DAYS_OFFSET)

def user_routes(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse('login'))
    user_routes = Route.objects.filter(applier=request.user)
    return render_to_response('user_routes.html', {'routes': user_routes},
                              context_instance=RequestContext(request))


def add_route(request):
    if request.method == "GET":
        form = RouteForm()
        return render_to_response('apply.html', {'form': form},
                                  context_instance=RequestContext(request))

    else:
        form = RouteForm(request.POST)
        if form.is_valid():
            route=form.save(commit=False)
            route.applier = request.user
            route.expires = days_offset()
            route.save()
            form.save_m2m()
            route.commit_add()
            return HttpResponseRedirect(urlresolvers.reverse("user-routes"))
        else:
            return render_to_response('apply.html', {'form': form},
                                      context_instance=RequestContext(request))
