# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2011-2014 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2011-2014 Leonidas Poulopoulos (@leopoul)
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.


from django.contrib.auth.models import User, UserManager, Permission, Group
from django.conf import settings

class shibauthBackend:
    def authenticate(self, **kwargs):
        username = kwargs.get('username')
        firstname = kwargs.get('firstname')
        lastname = kwargs.get('lastname')
        mail = kwargs.get('mail')
        authsource = kwargs.get('authsource')
        if authsource != 'shibboleth':
            return None
        try:
            user = self._auth_user(username, firstname, lastname, mail)
        except:
            return None
        if not user:
            return None
        return user

    def _auth_user(self, username, firstname, lastname, mail):

        try:
            user = User.objects.get(username__exact=username)
        # The user did not exist. Create one with no privileges
        except: 
            user = User.objects.create_user(username, mail, None)
            user.first_name = firstname
            user.last_name = lastname
            user.is_staff = False
            user.is_superuser = False
            user.is_active = False
            user.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
