from django.db import models
from django.contrib.auth.models import User
from flowspy.peers.models import *


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    peer = models.ForeignKey(Peer)
    
    def __unicode__(self):
        return "%s:%s" %(self.user.username, self.peer.peer_name)

    def get_address_space(self):
        networks = self.domain.networks.all()
        if not networks:
            return False
        return networks