from django.contrib import admin
from flowspy.flowspec.models import *
from utils import proxy as PR

class RouteAdmin(admin.ModelAdmin):
    
    actions = ['deactivate']

    def deactivate(self, request, queryset):
        applier = PR.Applier(route_objects=queryset)
        commit, response = applier.apply(configuration=applier.delete_routes())
        if commit:
            rows = queryset.update(is_online=False)
            queryset.update(response="Successfully removed route from network")
            self.message_user(request, "Successfully removed %s routes from network" % rows)
        else:
            self.message_user(request, "Could not remove routes from network")
    deactivate.short_description = "Remove selected routes from network"

    list_display = ('name', 'get_match', 'get_then', 'is_online', 'applier', 'response')
    fields = ('name', 'match','then','applier', 'expires')

    #def formfield_for_dbfield(self, db_field, **kwargs):
    #    if db_field.name == 'password':
    #        kwargs['widget'] = PasswordInput
    #    return db_field.formfield(**kwargs)

admin.site.register(MatchAddress)
admin.site.register(MatchPort)
admin.site.register(MatchDscp)
admin.site.register(MatchFragmentType)
admin.site.register(MatchIcmpCode)
admin.site.register(MatchIcmpType)
admin.site.register(MatchPacketLength)
admin.site.register(MatchProtocol)
admin.site.register(MatchTcpFlag)
admin.site.register(ThenAction)
admin.site.register(ThenStatement)
admin.site.register(MatchStatement)
admin.site.register(Route, RouteAdmin)

admin.site.disable_action('delete_selected')


