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

from django.contrib import admin
from flowspec.models import *
from accounts.models import *
from utils import proxy as PR
from tasks import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from peers.models import *
from flowspec.forms import *
import datetime
from django.conf import settings

from monkey_patch.forms import UserCreationForm, UserChangeForm

class RouteAdmin(admin.ModelAdmin):
    form = RouteForm
    actions = ['deactivate']
    
    def deactivate(self, request, queryset):
        queryset = queryset.filter(status='ACTIVE')
        response = batch_delete.delay(queryset, reason="ADMININACTIVE")
        self.message_user(request, "Added request %s to job que. Check in a while for result" % response)
    deactivate.short_description = "Remove selected routes from network"

    def save_model(self, request, obj, form, change):
        obj.status = "PENDING"
        obj.save()
        if change:
            obj.commit_edit()
        else:
            obj.commit_add()

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('name', 'status', 'applier' , 'applier_peer', 'get_match', 'get_then', 'response', "expires", "comments")

    fieldsets = [
        (None,               {'fields': ['name','applier']}),
        ("Match",               {'fields': ['source', 'sourceport', 'destination', 'destinationport', 'port']}),
        ('Advanced Match Statements', {'fields': ['dscp', 'fragmenttype', 'icmpcode', 'icmptype', 'packetlength', 'protocol', 'tcpflag'], 'classes': ['collapse']}),
        ("Then",               {'fields': ['then' ]}),
        ("Expires",               {'fields': ['expires' ]}),
        (None,               {'fields': ['comments',]}),
        
    ]
    


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    
class UserProfileAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    actions = ['deactivate', 'activate']
    list_display = ('username', 'email', 'first_name' , 'last_name', 'is_staff', 'is_active', 'is_superuser', 'get_userprofile_peer')
    inlines = [UserProfileInline]

    def deactivate(self, request, queryset):
        queryset = queryset.update(is_active=False)
    deactivate.short_description = "Deactivate Selected Users"

    def activate(self, request, queryset):
        queryset = queryset.update(is_active=True)
    activate.short_description = "Activate Selected Users"

    def get_userprofile_peer(self, instance):
        # instance is User instance
        return instance.get_profile().peer
    get_userprofile_peer.short_description = "User Peer"
#    fields = ('name', 'applier', 'expires')

    #def formfield_for_dbfield(self, db_field, **kwargs):
    #    if db_field.name == 'password':
    #        kwargs['widget'] = PasswordInput
    #    return db_field.formfield(**kwargs)

admin.site.unregister(User)
admin.site.register(MatchPort)
admin.site.register(MatchProtocol)
admin.site.register(MatchDscp)
admin.site.register(ThenAction)
admin.site.register(FragmentType)
admin.site.register(Route, RouteAdmin)
admin.site.register(User, UserProfileAdmin)
admin.site.disable_action('delete_selected')


