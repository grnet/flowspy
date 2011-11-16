from django.contrib import admin
from flowspy.flowspec.models import *

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
admin.site.register(Route)
