from django.db import models
from utils.whois import *
from django.contrib.auth.models import User

class PeerRange(models.Model):
    network = models.CharField(max_length=128)
    def __unicode__(self):
        return self.network
    class Meta:
        db_table = u'peer_range'
        ordering = ['network']

class TechcEmail(models.Model):
    email = models.CharField(max_length=352, db_column="email")
    def __unicode__(self):
        return self.email
    class Meta:
        db_table="techc_email"

class Peer(models.Model):
    peer_id = models.IntegerField(primary_key=True)
    peer_name = models.CharField(max_length=128)
    peer_as = models.IntegerField()
    peer_tag = models.CharField(max_length=64)
    domain_name = models.CharField(max_length=128, null=True, blank=True)
    networks = models.ManyToManyField(PeerRange, null=True, blank=True)
    techc_emails = models.ManyToManyField(TechcEmail, null=True, blank=True)

    def __unicode__(self):
        return self.peer_name
    class Meta:
        db_table = u'peer'
        ordering = ['peer_name']

        
    def fill_networks(self):
        network_range = []
        networks_list = []
        peer_as = "AS%s" %self.peer_as
        network_range = whois(peer_as)
        if network_range:
            for network_item in network_range:
                range, created = PeerRange.objects.get_or_create(network=network_item.compressed)
                networks_list.append(range)
            self.networks = networks_list
            self.save()


