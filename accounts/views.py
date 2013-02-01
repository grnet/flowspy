#
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
#Copyright © 2011-2013 Greek Research and Technology Network (GRNET S.A.)

#Developed by Leonidas Poulopoulos (leopoul-at-noc-dot-grnet-dot-gr),
#GRNET NOC
#
#Permission to use, copy, modify, and/or distribute this software for any
#purpose with or without fee is hereby granted, provided that the above
#copyright notice and this permission notice appear in all copies.
#
#THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH REGARD
#TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
#FITNESS. IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
#CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
#DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
#ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
#SOFTWARE.
#
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from flowspy.accounts.models import *
from flowspy.peers.models import *
from flowspy.flowspec.forms import *
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