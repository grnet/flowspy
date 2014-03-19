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

from django.db import models
from django.contrib.auth.models import User
from peers.models import *


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