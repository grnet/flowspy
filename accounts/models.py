from django.db import models
from django.contrib.auth.models import User
from flowspy.peers.models import *


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    domain = models.ForeignKey(Peer)

    def get_address_space(self):
        networks = self.domain.networks.all()
        if not networks:
            return False
        return networks