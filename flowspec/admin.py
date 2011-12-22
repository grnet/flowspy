from django.contrib import admin
from flowspy.flowspec.models import *
from flowspy.accounts.models import *
from utils import proxy as PR
from flowspec.tasks import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from accounts.models import UserProfile
from flowspy.flowspec.forms import *
import datetime

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
        obj.expires = datetime.date.today()
        obj.save()
        obj.commit_add()

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('name', 'status', 'applier' , 'applier_peer', 'get_match', 'get_then', 'response', "expires", "comments")

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


