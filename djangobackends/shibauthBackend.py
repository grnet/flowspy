# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

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
