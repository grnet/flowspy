#
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
#Copyright © 2011-2013 Greek Research and Technology Network (GRNET S.A.)

#Developed by Leonidas Poulopoulos (leopoul-at-noc-dot-grnet-dot-gr),
#GRNET NOC
#
#Permission to use, copy, modify, and/or distribute this software for any
#purpose with or without fee is hereby granted, provided that the above
#copyright notice and this permission notice appear in all copies.
#
#THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH REGARD
#TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
#FITNESS. IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
#CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
#DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
#ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
#SOFTWARE.
#
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
