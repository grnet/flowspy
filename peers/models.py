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

from django.contrib.auth.models import User
from django.db import models
from utils.whois import *
from django.conf import settings


class PeerRange(models.Model):
    network = models.CharField(max_length=128)

    def __unicode__(self):
        return self.network

    class Meta:
        db_table = u'peer_range'
        ordering = ['network']
        managed = settings.PEER_RANGE_MANAGED_TABLE


class TechcEmail(models.Model):
    email = models.CharField(max_length=352, db_column="email")

    def __unicode__(self):
        return self.email

    class Meta:
        db_table = "techc_email"
        managed = settings.PEER_TECHC_MANAGED_TABLE


class Peer(models.Model):
    peer_id = models.AutoField(primary_key=True)
    peer_name = models.CharField(max_length=128)
    peer_as = models.IntegerField(null=True, blank=True)
    # This needs to be converted to slug and an info message needs to be added.
    peer_tag = models.CharField(max_length=64)
    domain_name = models.CharField(max_length=128, null=True, blank=True)
    networks = models.ManyToManyField(PeerRange, blank=True)
    techc_emails = models.ManyToManyField(
        TechcEmail, blank=True, db_constraint=settings.PEER_TECHC_MANAGED_TABLE)

    def __unicode__(self):
        return self.peer_name

    class Meta:
        db_table = u'peer'
        ordering = ['peer_name']
        managed = settings.PEER_MANAGED_TABLE

    def fill_networks(self):
        network_range = []
        networks_list = []
        peer_as = "AS%s" % self.peer_as
        network_range = whois(peer_as)
        if network_range:
            for network_item in network_range:
                range, created = PeerRange.objects.get_or_create(network=network_item.compressed)
                networks_list.append(range)
            self.networks = networks_list
            self.save()


class PeerNotify(models.Model):
    peer = models.ForeignKey(Peer, db_constraint=settings.PEER_MANAGED_TABLE)
    user = models.ForeignKey(User)
    peer_activation_notified = models.BooleanField(default=True)
    
    class Meta:
        db_table = u'peers_peernotify'
