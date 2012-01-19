from django.contrib import admin
from flowspy.flowspec.models import *
from flowspy.accounts.models import *
from utils import proxy as PR
from flowspec.tasks import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from flowspy.accounts.models import UserProfile
from flowspy.peers.models import *
from flowspy.flowspec.forms import *
import datetime
from django.conf import settings
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple

class PeerAdminForm(ModelForm):
    networks=forms.ModelMultipleChoiceField(PeerRange.objects.all(),widget=
            FilteredSelectMultiple("PeerRange",True), required=False)

    class Meta:
        model= Peer

class PeerAdmin(admin.ModelAdmin):
    form = PeerAdminForm

class PeerTechcAdmin(admin.ModelAdmin):
    list_display = ('get_peer_name', 'emails')

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
    actions = ['deactivate', 'activate']
    list_display = ('username', 'email', 'first_name' , 'last_name', 'is_staff', 'is_active','get_userprofile_peer')
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

#admin.site.register(MatchAddress)
admin.site.unregister(User)
admin.site.register(MatchPort)
admin.site.register(MatchDscp)
admin.site.register(UserProfile)
#admin.site.register(MatchFragmentType)
#admin.site.register(MatchIcmpCode)
#admin.site.register(MatchIcmpType)
#admin.site.register(MatchPacketLength)
#admin.site.register(MatchProtocol)
#admin.site.register(MatchTcpFlag)
admin.site.register(ThenAction)
#admin.site.register(ThenStatement)
#admin.site.register(MatchStatement)
admin.site.register(Peer, PeerAdmin)
admin.site.register(PeerTechc, PeerTechcAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(User, UserProfileAdmin)
admin.site.disable_action('delete_selected')


