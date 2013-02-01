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
from django.db import models
from django.contrib.auth.models import User
from flowspy.peers.models import *


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    peer = models.ForeignKey(Peer)
    
    class Meta:
        permissions = (
                ("overview", "Can see registered users and rules"),
            )

    
    def __unicode__(self):
        return "%s:%s" %(self.user.username, self.peer.peer_name)

    def get_address_space(self):
        networks = self.domain.networks.all()
        if not networks:
            return False
        return networks