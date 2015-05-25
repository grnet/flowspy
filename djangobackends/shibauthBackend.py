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

from django.contrib.auth.models import User


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
