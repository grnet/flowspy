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
from flowspy.accounts.models import *

from django.forms.models import model_to_dict

from flowspy.flowspec.forms import * 
from flowspy.flowspec.models import *

from copy import deepcopy

def days_offset(): return datetime.now() + timedelta(days = settings.EXPIRATION_DAYS_OFFSET)

@login_required
def user_routes(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse('login'))
    user_routes = Route.objects.filter(applier=request.user)
    return render_to_response('user_routes.html', {'routes': user_routes},
                              context_instance=RequestContext(request))

@login_required
def group_routes(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse('login'))
    peer = request.user.get_profile().peer
    if peer:
       peer_members = UserProfile.objects.filter(peer=peer)
       users = [prof.user for prof in peer_members]
       group_routes = Route.objects.filter(applier__in=users)
    return render_to_response('user_routes.html', {'routes': group_routes},
                              context_instance=RequestContext(request))


@login_required
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
@login_required
def edit_route(request, route_slug):
    route_edit = get_object_or_404(Route, name=route_slug)
    route_original = deepcopy(route_edit)
    if request.POST:
        form = RouteForm(request.POST, instance = route_edit)
        if form.is_valid():
            route=form.save(commit=False)
            route.name = route_original.name
            route.applier = route_original.applier
            route.expires = route_original.expires
            route.is_active = route_original.is_active
            route.save()
            form.save_m2m()
            route.commit_edit()
            return HttpResponseRedirect(urlresolvers.reverse("user-routes"))
        else:
            return render_to_response('apply.html', {'form': form, 'edit':True},
                                      context_instance=RequestContext(request))
    else:
        dictionary = model_to_dict(route_edit, fields=[], exclude=[])
        form = RouteForm(dictionary)
        return render_to_response('apply.html', {'form': form, 'edit':True},
                                  context_instance=RequestContext(request))

@login_required
def delete_route(request, route_slug):
    if request.is_ajax():
        route = get_object_or_404(Route, name=route_slug)
        if route.applier == request.user:
            route.deactivate()
            route.commit_delete()
    return HttpResponseRedirect(urlresolvers.reverse("user-routes"))
