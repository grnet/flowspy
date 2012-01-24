from django.contrib import admin
from flowspy.accounts.models import *
from django.contrib.auth.models import User
from flowspy.peers.models import *
from django.conf import settings

class UserPrAdmin(admin.ModelAdmin):
    list_display = ('user', 'peer')

admin.site.register(UserProfile, UserPrAdmin)