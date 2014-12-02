# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright (C) 2010-2014 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from accounts.models import *
from peers.models import *
from flowspec.forms import *
from registration.models import RegistrationProfile
from registration.views import activate as registration_activate
from django.views.decorators.cache import never_cache

@never_cache
def activate(request, activation_key):
    account = None
    if request.method == "GET":
        activation_key = activation_key.lower() # Normalize before trying anything with it.
        context = RequestContext(request)
        try:
            rp = RegistrationProfile.objects.get(activation_key=activation_key)
            
        except RegistrationProfile.DoesNotExist:
            return render_to_response("registration/activate.html",
                                  { 'account': account,
                                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                                  context_instance=context)
        try:
            userProfile = rp.user.get_profile()
        except UserProfile.DoesNotExist:
            return render_to_response("registration/activate.html",
                                  { 'account': account,
                                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                                  context_instance=context)
        
        form = UserProfileForm(instance=userProfile)
        form.fields['user'] = forms.ModelChoiceField(queryset=User.objects.filter(pk=rp.user.pk), empty_label=None)
        form.fields['peer'] = forms.ModelChoiceField(queryset=Peer.objects.all(), empty_label=None)
        
        return render_to_response("registration/activate_edit.html",
                                  { 'account': account,
                                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                    'form': form },
                                  context_instance=context)
            
    if request.method == "POST":
        context = RequestContext(request)
        request_data = request.POST.copy()
        try:
            user = User.objects.get(pk=request_data['user'])
            up = user.get_profile()
            up.peer = Peer.objects.get(pk=request_data['peer'])
            up.save()
            
        except:
            return render_to_response("registration/activate_edit.html",
                                  { 'account': account,
                                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
                                     },
                                  context_instance=context)
        activation_key = activation_key.lower() # Normalize before trying anything with it.
        try:
            rp = RegistrationProfile.objects.get(activation_key=activation_key)
            account = RegistrationProfile.objects.activate_user(activation_key)
        except Exception as e:
            pass
    
        if account:
            # A user has been activated
            email = render_to_string("registration/activation_complete.txt",
                                     {"site": Site.objects.get_current(),
                                      "user": account})
            send_mail(_("%sUser account activated") % settings.EMAIL_SUBJECT_PREFIX,
                  email, settings.SERVER_EMAIL, [account.email])
        context = RequestContext(request)
        return render_to_response("registration/activate.html",
                                  { 'account': account,
                                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                                  context_instance=context)