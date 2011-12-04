# Create your views here.
import urllib2
import re
import socket
import json
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.core import urlresolvers
from django.core import serializers
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

from django.contrib.auth import authenticate, login

from django.forms.models import model_to_dict

from flowspy.flowspec.forms import * 
from flowspy.flowspec.models import *

from copy import deepcopy
from flowspy.utils.decorators import shib_required

def days_offset(): return datetime.now() + timedelta(days = settings.EXPIRATION_DAYS_OFFSET)

@login_required
def user_routes(request):
    user_routes = Route.objects.filter(applier=request.user)
    return render_to_response('user_routes.html', {'routes': user_routes},
                              context_instance=RequestContext(request))

@login_required
def group_routes(request):
    group_routes = []
    peer = request.user.get_profile().peer
    if peer:
       peer_members = UserProfile.objects.filter(peer=peer)
       users = [prof.user for prof in peer_members]
       group_routes = Route.objects.filter(applier__in=users)
    return render_to_response('user_routes.html', {'routes': group_routes},
                              context_instance=RequestContext(request))


@login_required
def add_route(request):
    applier = request.user.pk
    if request.method == "GET":
        form = RouteForm()
        return render_to_response('apply.html', {'form': form, 'applier': applier},
                                  context_instance=RequestContext(request))

    else:
        form = RouteForm(request.POST)
        if form.is_valid():
            route=form.save(commit=False)
            route.applier = request.user
            route.expires = days_offset()
            route.status = "PENDING"
            route.save()
            form.save_m2m()
            route.commit_add()
            return HttpResponseRedirect(reverse("group-routes"))
        else:
            return render_to_response('apply.html', {'form': form, 'applier':applier},
                                      context_instance=RequestContext(request))

@login_required
def add_then(request):
    applier = request.user.pk
    if request.method == "GET":
        form = RouteForm()
        return render_to_response('apply.html', {'form': form, 'applier': applier},
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
            return HttpResponseRedirect(reverse("group-routes"))
        else:
            return render_to_response('apply.html', {'form': form, 'applier':applier},
                                      context_instance=RequestContext(request))

@login_required
def edit_route(request, route_slug):
    applier = request.user.pk
    route_edit = get_object_or_404(Route, name=route_slug)
    route_original = deepcopy(route_edit)
    if request.POST:
        form = RouteForm(request.POST, instance = route_edit)
        if form.is_valid():
            route=form.save(commit=False)
            route.name = route_original.name
            route.applier = request.user
            route.expires = route_original.expires
            route.status = "PENDING"
            route.save()
            form.save_m2m()
            route.commit_edit()
            return HttpResponseRedirect(reverse("group-routes"))
        else:
            return render_to_response('apply.html', {'form': form, 'edit':True, 'applier': applier},
                                      context_instance=RequestContext(request))
    else:
        dictionary = model_to_dict(route_edit, fields=[], exclude=[])
        #form = RouteForm(instance=route_edit)
        form = RouteForm(dictionary)
        return render_to_response('apply.html', {'form': form, 'edit':True, 'applier': applier},
                                  context_instance=RequestContext(request))

@login_required
def delete_route(request, route_slug):
    if request.is_ajax():
        route = get_object_or_404(Route, name=route_slug)
        applier_peer = route.applier.get_profile().peer
        requester_peer = request.user.get_profile().peer
        if applier_peer == requester_peer:
            route.deactivate()
            route.commit_delete()
        html = "<html><body>Done</body></html>"
        return HttpResponse(html)
    else:
        return HttpResponseRedirect(reverse("group-routes"))

@login_required
def user_profile(request):
    user = request.user
    peer = request.user.get_profile().peer
    
    return render_to_response('profile.html', {'user': user, 'peer':peer},
                                  context_instance=RequestContext(request))


def user_login(request):
    try:
        error_username = None
        error_orgname = None
        username = request.META['HTTP_EPPN']
        if not username:
            error_username = True
        firstname = request.META['HTTP_SHIB_INETORGPERSON_GIVENNAME']
        lastname = request.META['HTTP_SHIB_PERSON_SURNAME']
        mail = request.META['HTTP_SHIB_INETORGPERSON_MAIL']
        organization = request.META['HTTP_SHIB_HOMEORGANIZATION']
        if not organization:
            error_orgname = True

        if error_orgname or error_username:
            error = "Your idP should release the HTTP_EPPN, HTTP_SHIB_HOMEORGANIZATION attributes towards this service" 
            return render_to_response('error.html', {'error': error,},
                                  context_instance=RequestContext(request))
        user = authenticate(username=username, firstname=firstname, lastname=lastname, mail=mail, organization=organization, affiliation=None)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("group-routes"))
                # Redirect to a success page.
                # Return a 'disabled account' error message
        else:
            html = "<html><body>Invalid User</body></html>"
            return HttpResponse(html)
    except Exception as e:
        html = "<html><body>Invalid Login Procedure %s </body></html>" %e
        return HttpResponse(html)
        # Return an 'invalid login' error message.
#    return HttpResponseRedirect(reverse("user-routes"))

@login_required
def add_rate_limit(request):
    if request.method == "GET":
        form = ThenPlainForm()
        return render_to_response('add_rate_limit.html', {'form': form,},
                                  context_instance=RequestContext(request))

    else:
        form = ThenPlainForm(request.POST)
        if form.is_valid():
            then=form.save(commit=False)
            then.action_value = "%sk"%then.action_value
            then.save()
            response_data = {}
            response_data['pk'] = "%s" %then.pk
            response_data['value'] = "%s:%s" %(then.action, then.action_value)
            return HttpResponse(simplejson.dumps(response_data), mimetype='application/json')
        else:
            return render_to_response('add_rate_limit.html', {'form': form,},
                                      context_instance=RequestContext(request))

@login_required
def add_port(request):
    if request.method == "GET":
        form = PortPlainForm()
        return render_to_response('add_port.html', {'form': form,},
                                  context_instance=RequestContext(request))

    else:
        form = PortPlainForm(request.POST)
        if form.is_valid():
            port=form.save()
            response_data = {}
            response_data['value'] = "%s" %port.pk
            response_data['text'] = "%s" %port.port
            return HttpResponse(simplejson.dumps(response_data), mimetype='application/json')
        else:
            return render_to_response('add_port.html', {'form': form,},
                                      context_instance=RequestContext(request))

@login_required
def user_logout(request):
    return HttpResponseRedirect(settings.SHIB_LOGOUT_URL)
    
    
def load_jscript(request, file):
    return render_to_response('%s.js' % file, context_instance=RequestContext(request), mimetype="text/javascript")
