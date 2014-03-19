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

from peers.models import *
from flowspec.forms import *
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
