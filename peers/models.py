from django.db import models
from utils.whois import *
from django.contrib.auth.models import User

# Create your models here.
class PeerRange(models.Model):
    network = models.CharField(max_length=128)
    def __unicode__(self):
        return self.network
    class Meta:
        db_table = u'peer_range'

# Create your models here.
class Peer(models.Model):
    peer_id = models.IntegerField(primary_key=True)
    peer_name = models.CharField(max_length=128)
    peer_as = models.IntegerField()
    peer_tag = models.CharField(max_length=64)
    domain_name = models.CharField(max_length=128, null=True, blank=True)
    networks = models.ManyToManyField(PeerRange, null=True, blank=True)

    def __unicode__(self):
        return self.peer_name
    class Meta:
        db_table = u'peer'
        
    def fill_networks(self):
        network_range = []
        peer_as = "AS%s" %self.peer_as
        network_range = whois(peer_as)
        if network_range:
            for network_item in network_range:
                range, created = PeerRange.objects.get_or_create(network=network_item.compressed)
                if not range.network in self.networks.all():
                    self.networks.add(range)
            self.save()
                    
            
