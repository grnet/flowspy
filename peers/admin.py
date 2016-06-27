# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright (C) 2010-2014 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django.contrib import admin

from peers.models import PeerRange, TechcEmail, Peer, PeerNotify
from django import forms
from django.forms import ModelForm
from django.contrib.admin.widgets import FilteredSelectMultiple


class PeerAdminForm(ModelForm):
    networks = forms.ModelMultipleChoiceField(
        PeerRange.objects.all(),
        widget=FilteredSelectMultiple("PeerRange", True),
        required=False
    )

    techc_emails = forms.ModelMultipleChoiceField(
        TechcEmail.objects.all(),
        widget=FilteredSelectMultiple("TechcEmail", True),
        required=False
    )

    class Meta:
        fields = '__all__'
        model = Peer


class PeerAdmin(admin.ModelAdmin):
    search_fields = ['peer_name', 'networks__network']
    form = PeerAdminForm


class PeerRangeAdmin(admin.ModelAdmin):
    search_fields = ['network']


class TechcEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']


class PeerNotifyAdmin(admin.ModelAdmin):
    list_display = ('peer', 'user', 'peer_activation_notified')
    search_fields = ['peer', 'user']


admin.site.register(Peer, PeerAdmin)
admin.site.register(PeerRange, PeerRangeAdmin)
admin.site.register(TechcEmail, TechcEmailAdmin)
admin.site.register(PeerNotify, PeerNotifyAdmin)
