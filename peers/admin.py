from django.contrib import admin

from flowspy.peers.models import *
from flowspy.flowspec.forms import *
from django.conf import settings
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple

class PeerAdminForm(ModelForm):
    networks=forms.ModelMultipleChoiceField(PeerRange.objects.all(),widget=
            FilteredSelectMultiple("PeerRange",True), required=False)
    techc_emails=forms.ModelMultipleChoiceField(TechcEmail.objects.all(),widget=
            FilteredSelectMultiple("TechcEmail",True), required=False)
    class Meta:
        model= Peer

class PeerAdmin(admin.ModelAdmin):
    form = PeerAdminForm

admin.site.register(Peer, PeerAdmin)
admin.site.register(PeerRange)
admin.site.register(TechcEmail)
