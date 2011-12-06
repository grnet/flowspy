from django.contrib import admin
from flowspy.flowspec.models import *
from flowspy.accounts.models import *
from utils import proxy as PR
from flowspec.tasks import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from accounts.models import UserProfile


class RouteAdmin(admin.ModelAdmin):
    
    actions = ['deactivate']
    
    def deactivate(self, request, queryset):
        response = batch_delete.delay(queryset, reason="ADMININACTIVE")
        self.message_user(request, "Added request %s to job que. Check in a while for result" % response)
    deactivate.short_description = "Remove selected routes from network"

    list_display = ('name', 'status', 'applier' , 'applier_peer', 'get_match', 'get_then', 'response')
    fieldsets = [
        (None,               {'fields': ['name','applier']}),
        ("Match",               {'fields': ['source', 'sourceport', 'destination', 'destinationport', 'port']}),
        ('Advanced Match Statements', {'fields': ['dscp', 'fragmenttype', 'icmpcode', 'icmptype', 'packetlength', 'protocol', 'tcpflag'], 'classes': ['collapse']}),
        ("Then",               {'fields': ['then' ]}),
        (None,               {'fields': ['comments',]}),
        
    ]
    
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]
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
admin.site.register(Route, RouteAdmin)
admin.site.register(User, UserProfileAdmin)
admin.site.disable_action('delete_selected')


