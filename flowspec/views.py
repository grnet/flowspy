# Create your views here.
import urllib2
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
from django.template.loader import get_template, render_to_string
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

from django.views.decorators.cache import never_cache
from django.conf import settings
from django.core.mail import mail_admins, mail_managers, send_mail


@login_required
def user_routes(request):
    user_routes = Route.objects.filter(applier=request.user)
    return render_to_response('user_routes.html', {'routes': user_routes},
                              context_instance=RequestContext(request))

def welcome(request):
    return render_to_response('welcome.html', context_instance=RequestContext(request))

@login_required
@never_cache
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
@never_cache
def add_route(request):
    applier = request.user.pk
    applier_peer_networks = request.user.get_profile().peer.networks.all()
    if not applier_peer_networks:
         messages.add_message(request, messages.WARNING,
                             "Insufficient rights on administrative networks. Cannot add rule. Contact your administrator")
         return HttpResponseRedirect(reverse("group-routes"))
    if request.method == "GET":
        form = RouteForm()
        return render_to_response('apply.html', {'form': form, 'applier': applier},
                                  context_instance=RequestContext(request))

    else:
        form = RouteForm(request.POST)
        if form.is_valid():
            route=form.save(commit=False)
            route.applier = request.user
            route.status = "PENDING"
            route.save()
            form.save_m2m()
            route.commit_add()
            mail_body = render_to_string("rule_add_mail.txt",
                                             {"route": route})
            mail_admins("Rule %s creation request submitted by %s" %(route.name, route.applier.username),
                          mail_body, fail_silently=True)
            return HttpResponseRedirect(reverse("group-routes"))
        else:
            return render_to_response('apply.html', {'form': form, 'applier':applier},
                                      context_instance=RequestContext(request))

@login_required
@never_cache
def edit_route(request, route_slug):
    applier = request.user.pk
    applier_peer = request.user.get_profile().peer
    route_edit = get_object_or_404(Route, name=route_slug)
    route_edit_applier_peer = route_edit.applier.get_profile().peer
    if applier_peer != route_edit_applier_peer:
        messages.add_message(request, messages.WARNING,
                             "Insufficient rights to edit rule %s" %(route_slug))
        return HttpResponseRedirect(reverse("group-routes"))
    if route_edit.status == "ADMININACTIVE" :
        messages.add_message(request, messages.WARNING,
                             "Administrator has disabled editing of rule %s" %(route_slug))
        return HttpResponseRedirect(reverse("group-routes"))
    if route_edit.status == "EXPIRED" :
        messages.add_message(request, messages.WARNING,
                             "Cannot edit the expired rule %s. Contact helpdesk to enable it" %(route_slug))
        return HttpResponseRedirect(reverse("group-routes"))
    if route_edit.status == "PENDING" :
        messages.add_message(request, messages.WARNING,
                             "Cannot edit a pending rule: %s." %(route_slug))
        return HttpResponseRedirect(reverse("group-routes"))
    route_original = deepcopy(route_edit)
    if request.POST:
        form = RouteForm(request.POST, instance = route_edit)
        if form.is_valid():
            route=form.save(commit=False)
            route.name = route_original.name
            route.applier = request.user
            route.status = "PENDING"
            route.save()
            form.save_m2m()
            route.commit_edit()
            mail_body = render_to_string("rule_edit_mail.txt",
                                             {"route": route})
            mail_admins("Rule %s edit request submitted by %s" %(route.name, route.applier.username),
                          mail_body, fail_silently=True)
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
@never_cache
def delete_route(request, route_slug):
    if request.is_ajax():
        route = get_object_or_404(Route, name=route_slug)
        applier_peer = route.applier.get_profile().peer
        requester_peer = request.user.get_profile().peer
        if applier_peer == requester_peer:
            route.status = "PENDING"
            route.commit_delete()
            mail_body = render_to_string("rule_delete_mail.txt",
                                             {"route": route})
            mail_admins("Rule %s removal request submitted by %s" %(route.name, route.applier.username),
                          mail_body, fail_silently=True)
        html = "<html><body>Done</body></html>"
        return HttpResponse(html)
    else:
        return HttpResponseRedirect(reverse("group-routes"))

@login_required
@never_cache
def user_profile(request):
    user = request.user
    peer = request.user.get_profile().peer
    
    return render_to_response('profile.html', {'user': user, 'peer':peer},
                                  context_instance=RequestContext(request))

@never_cache
def user_login(request):
    try:
        error_username = None
        error_orgname = None
        error_affiliation = None
        error = ''
        username = request.META['HTTP_EPPN']
        if not username:
            error_username = True
        firstname = request.META['HTTP_SHIB_INETORGPERSON_GIVENNAME']
        lastname = request.META['HTTP_SHIB_PERSON_SURNAME']
        mail = request.META['HTTP_SHIB_INETORGPERSON_MAIL']
        organization = request.META['HTTP_SHIB_HOMEORGANIZATION']
        affiliation = request.META['HTTP_SHIB_EP_ENTITLEMENT']
        if settings.SHIB_AUTH_AFFILIATION in affiliation.split(";"):
            has_affiliation = True
        if not has_affiliation:
            error_affiliation = True
        if not organization:
            error_orgname = True
        if error_username:
            error = "Your idP should release the HTTP_EPPN attribute towards this service\n"
        if error_orgname:
            error = error + "Your idP should release the HTTP_SHIB_HOMEORGANIZATION attribute towards this service\n"
        if error_affiliation:
            error = error + "Your idP should release an appropriate HTTP_SHIB_EP_ENTITLEMENT attribute towards this service"
        if error_username or error_orgname or error_affiliation:
            return render_to_response('error.html', {'error': error,},
                                  context_instance=RequestContext(request))
        user = authenticate(username=username, firstname=firstname, lastname=lastname, mail=mail, organization=organization, affiliation=affiliation)
        if user is not None:
            login(request, user)
            update_user_attributes(user, firstname=firstname, lastname=lastname, mail=mail)
            return HttpResponseRedirect(reverse("group-routes"))
                # Redirect to a success page.
                # Return a 'disabled account' error message
        else:
            error = "Something went wrong during user authentication. Contact your administrator"
            return render_to_response('error.html', {'error': error,},
                                  context_instance=RequestContext(request))
    except Exception as e:
        error = "Invalid login procedure"
        return render_to_response('error.html', {'error': error,},
                                  context_instance=RequestContext(request))
        # Return an 'invalid login' error message.
#    return HttpResponseRedirect(reverse("user-routes"))

@login_required
@never_cache
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
            
def update_user_attributes(user, firstname, lastname, mail):
    user.first_name = firstname
    user.last_name = lastname
    user.email = mail
    user.save()

@login_required
@never_cache
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
@never_cache
def user_logout(request):
    return HttpResponseRedirect(settings.SHIB_LOGOUT_URL)
    
@never_cache
def load_jscript(request, file):
    return render_to_response('%s.js' % file, context_instance=RequestContext(request), mimetype="text/javascript")
