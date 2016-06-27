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
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache

from rest_framework.authtoken.models import Token
from accounts.models import UserProfile
from peers.models import Peer
from flowspec.forms import UserProfileForm
from registration.models import RegistrationProfile


def generate_token(request):
    user = request.user
    try:
        token = user.auth_token
    except Token.DoesNotExist:
        token = Token.objects.create(user=request.user)
    return HttpResponse(token)


@never_cache
def activate(request, activation_key):
    account = None
    if request.method == "GET":
        activation_key = activation_key.lower()  # Normalize before trying anything with it.
        try:
            rp = RegistrationProfile.objects.get(activation_key=activation_key)

        except RegistrationProfile.DoesNotExist:
            return render(
                request,
                'registration/activate.html',
                {
                    'account': account,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
                }
            )
        try:
            userProfile = rp.user.userprofile
        except UserProfile.DoesNotExist:
            return render(
                request,
                'registration/activate.html',
                {
                    'account': account,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
                }
            )

        form = UserProfileForm(instance=userProfile)

        return render(
            request,
            'registration/activate_edit.html',
            {
                'account': account,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                'form': form
            },
        )

    if request.method == "POST":
        request_data = request.POST.copy()
	try:
            user = User.objects.get(pk=request_data['user'])
            up = user.userprofile

            # use getlist to get the list of peers (might be multiple)
            profile_peers = request.POST.getlist('peers')

            # remove already assigned peers, as these are selected by
            # the user, no admin has yet verified those. They will be
            # replaced by the admin's selection.
            up.peers.clear()

            for peer in profile_peers:
                up.peers.add(Peer.objects.get(pk=peer))
            up.save()

        except:
            return render(
                request,
                'registration/activate_edit.html',
                {
                    'account': account,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
                },
            )
        activation_key = activation_key.lower()  # Normalize before trying anything with it.
        try:
            rp = RegistrationProfile.objects.get(activation_key=activation_key)
            account = RegistrationProfile.objects.activate_user(activation_key)
        except Exception:
            pass

        if account:
            # A user has been activated
            email = render_to_string(
                'registration/activation_complete.txt',
                {
                    'site': Site.objects.get_current(),
                    'user': account
                }
            )
            send_mail(
                _("%sUser account activated") % settings.EMAIL_SUBJECT_PREFIX,
                email,
                settings.SERVER_EMAIL,
                [account.email]
            )
        return render(
            request,
            'registration/activate.html',
            {
                'account': account,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS
            },
        )
