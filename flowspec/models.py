# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from utils import proxy as PR
from ipaddr import *
import datetime
import logging
from time import sleep

import beanstalkc
from flowspy.utils.randomizer import id_generator as id_gen

from flowspec.tasks import *

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


FRAGMENT_CODES = (
    ("dont-fragment", "Don't fragment"),
    ("first-fragment", "First fragment"),
    ("is-fragment", "Is fragment"),
    ("last-fragment", "Last fragment"),
    ("not-a-fragment", "Not a fragment")
)

THEN_CHOICES = (
    ("accept", "Accept"),
    ("discard", "Discard"),
    ("community", "Community"),
    ("next-term", "Next term"),
    ("routing-instance", "Routing Instance"),
    ("rate-limit", "Rate limit"),
    ("sample", "Sample")                
)

MATCH_PROTOCOL = (
    ("ah", "ah"),
    ("egp", "egp"),
    ("esp", "esp"),
    ("gre", "gre"),
    ("icmp", "icmp"),
    ("icmp6", "icmp6"),
    ("igmp", "igmp"),
    ("ipip", "ipip"),
    ("ospf", "ospf"),
    ("pim", "pim"),
    ("rsvp", "rsvp"),
    ("sctp", "sctp"),
    ("tcp", "tcp"),
    ("udp", "udp"),
)

ROUTE_STATES = (
    ("ACTIVE", "ACTIVE"),
    ("ERROR", "ERROR"),
    ("EXPIRED", "EXPIRED"),
    ("PENDING", "PENDING"),
    ("OUTOFSYNC", "OUTOFSYNC"),
    ("INACTIVE", "INACTIVE"),
    ("ADMININACTIVE", "ADMININACTIVE"),           
)


def days_offset(): return datetime.date.today() + datetime.timedelta(days = settings.EXPIRATION_DAYS_OFFSET)
    
class MatchPort(models.Model):
    port = models.CharField(max_length=24, unique=True)
    def __unicode__(self):
        return self.port
    class Meta:
        db_table = u'match_port'    

class MatchDscp(models.Model):
    dscp = models.CharField(max_length=24)
    def __unicode__(self):
        return self.dscp
    class Meta:
        db_table = u'match_dscp'

class MatchProtocol(models.Model):
    protocol = models.CharField(max_length=24, unique=True)
    def __unicode__(self):
        return self.protocol
    class Meta:
        db_table = u'match_protocol'

   
class ThenAction(models.Model):
    action = models.CharField(max_length=60, choices=THEN_CHOICES, verbose_name="Action")
    action_value = models.CharField(max_length=255, blank=True, null=True, verbose_name="Action Value")
    def __unicode__(self):
        ret = "%s:%s" %(self.action, self.action_value)
        return ret.rstrip(":")
    class Meta:
        db_table = u'then_action'
        ordering = ['action', 'action_value']
        unique_together = ("action", "action_value")

class Route(models.Model):
    name = models.SlugField(max_length=128, verbose_name=_("Name"))
    applier = models.ForeignKey(User, blank=True, null=True)
    source = models.CharField(max_length=32, help_text=_("Network address. Use address/CIDR notation"), verbose_name=_("Source Address"))
    sourceport = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchSourcePort", verbose_name=_("Source Port"))
    destination = models.CharField(max_length=32, help_text=_("Network address. Use address/CIDR notation"), verbose_name=_("Destination Address"))
    destinationport = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchDestinationPort", verbose_name=_("Destination Port"))
    port = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchPort", verbose_name=_("Port"))
    dscp = models.ManyToManyField(MatchDscp, blank=True, null=True, verbose_name="DSCP")
    fragmenttype = models.CharField(max_length=20, choices=FRAGMENT_CODES, blank=True, null=True, verbose_name="Fragment Type")
    icmpcode = models.CharField(max_length=32, blank=True, null=True, verbose_name="ICMP Code")
    icmptype = models.CharField(max_length=32, blank=True, null=True, verbose_name="ICMP Type")
    packetlength = models.IntegerField(blank=True, null=True, verbose_name="Packet Length")
    protocol = models.ManyToManyField(MatchProtocol, blank=True, null=True, verbose_name=_("Protocol"))
    tcpflag = models.CharField(max_length=128, blank=True, null=True, verbose_name="TCP flag")
    then = models.ManyToManyField(ThenAction, verbose_name=_("Then"))
    filed = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ROUTE_STATES, blank=True, null=True, verbose_name=_("Status"), default="PENDING")
#    is_online = models.BooleanField(default=False)
#    is_active = models.BooleanField(default=False)
    expires = models.DateField(default=days_offset, verbose_name=_("Expires"))
    response = models.CharField(max_length=512, blank=True, null=True, verbose_name=_("Response"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("Comments"))

    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'route'
        verbose_name = "Rule"
        verbose_name_plural = "Rules"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            hash = id_gen()
            self.name = "%s_%s" %(self.name, hash)
        super(Route, self).save(*args, **kwargs) # Call the "real" save() method.

        
    def clean(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        if self.destination:
            try:
                address = IPNetwork(self.destination)
                self.destination = address.exploded
            except Exception:
                raise ValidationError(_('Invalid network address format at Destination Field'))
        if self.source:
            try:
                address = IPNetwork(self.source)
                self.source = address.exploded
            except Exception:
                raise ValidationError(_('Invalid network address format at Source Field'))
   
    def commit_add(self, *args, **kwargs):
        peer = self.applier.get_profile().peer.domain_name
        send_message("[%s] Adding rule %s. Please wait..." %(self.applier.username, self.name), peer)
        response = add.delay(self)
        logger.info("Got add job id: %s" %response)
        
    def commit_edit(self, *args, **kwargs):
        peer = self.applier.get_profile().peer.domain_name
        send_message("[%s] Editing rule %s. Please wait..." %(self.applier.username, self.name), peer)
        response = edit.delay(self)
        logger.info("Got edit job id: %s" %response)

    def commit_delete(self, *args, **kwargs):
        reason_text = ''
        reason = ''
        if "reason" in kwargs:
            reason = kwargs['reason']
            reason_text = "Reason: %s. " %reason
        peer = self.applier.get_profile().peer.domain_name
        send_message("[%s] Suspending rule %s. %sPlease wait..." %(self.applier.username, self.name, reason_text), peer)
        response = delete.delay(self, reason=reason)
        logger.info("Got delete job id: %s" %response)

    def has_expired(self):
        today = datetime.date.today()
        if today > self.expires:
            return True
        return False
    
    def check_sync(self):
        if not self.is_synced():
            self.status = "OUTOFSYNC"
            self.save()
    
    def is_synced(self):
        found = False
        get_device = PR.Retriever()
        device = get_device.fetch_device()
        try:
            routes = device.routing_options[0].routes
        except Exception as e:
            self.status = "EXPIRED"
            self.save()
            logger.error("No routing options on device. Exception: %s" %e)
            return True
        for route in routes:
            if route.name == self.name:
                found = True
                logger.info('Found a matching rule name')
                devicematch = route.match
                try:
                    assert(self.destination)
                    assert(devicematch['destination'][0])
                    if self.destination == devicematch['destination'][0]:
                        found = found and True
                        logger.info('Found a matching destination')
                    else:
                        found = False
                        logger.info('Destination fields do not match')
                except:
                    pass
                try:
                    assert(self.source)
                    assert(devicematch['source'][0])
                    if self.source == devicematch['source'][0]:
                        found = found and True
                        logger.info('Found a matching source')
                    else:
                        found = False
                        logger.info('Source fields do not match')
                except:
                    pass
                try:
                    assert(self.fragmenttype)
                    assert(devicematch['fragment'][0])
                    if self.fragmenttype == devicematch['fragment'][0]:
                        found = found and True
                        logger.info('Found a matching fragment type')
                    else:
                        found = False
                        logger.info('Fragment type fields do not match')
                except:
                    pass
                try:
                    assert(self.icmpcode)
                    assert(devicematch['icmp-code'][0])
                    if self.icmpcode == devicematch['icmp-code'][0]:
                        found = found and True
                        logger.info('Found a matching icmp code')
                    else:
                        found = False
                        logger.info('Icmp code fields do not match')
                except:
                    pass
                try:
                    assert(self.icmptype)
                    assert(devicematch['icmp-type'][0])
                    if self.icmptype == devicematch['icmp-type'][0]:
                        found = found and True
                        logger.info('Found a matching icmp type')
                    else:
                        found = False
                        logger.info('Icmp type fields do not match')
                except:
                    pass
                if found and self.status != "ACTIVE":
                    logger.error('Rule is applied on device but appears as offline')
                    self.status = "ACTIVE"
                    self.save()
                    found = True
            if self.status == "ADMININACTIVE" or self.status == "INACTIVE" or self.status == "EXPIRED":
                found = True
        return found

    def get_then(self):
        ret = ''
        then_statements = self.then.all()
        for statement in then_statements:
            if statement.action_value:
                ret = "%s %s:<strong>%s</strong><br/>" %(ret, statement.action, statement.action_value)
            else: 
                ret = "%s %s<br>" %(ret, statement.action)
        return ret.rstrip(',')
    
    get_then.short_description = 'Then statement'
    get_then.allow_tags = True
#
    def get_match(self):
        ret = ''
        if self.destination:
            ret = '%s Dst Addr:<strong>%s</strong> <br/>' %(ret, self.destination)
        if self.fragmenttype:
            ret = "%s Fragment Type:<strong>%s</strong><br/>" %(ret, self.fragmenttype)
        if self.icmpcode:
            ret = "%s ICMP code:<strong>%s</strong><br/>" %(ret, self.icmpcode)
        if self.icmptype:
            ret = "%s ICMP Type:<strong>%s</strong><br/>" %(ret, self.icmptype)
        if self.packetlength:
            ret = "%s Packet Length:<strong>%s</strong><br/>" %(ret, self.packetlength)
        if self.source:
            ret = "%s Src Addr:<strong>%s</strong> <br/>" %(ret, self.source)
        if self.tcpflag:
            ret = "%s TCP flag:<strong>%s</strong><br/>" %(ret, self.tcpflag)
        if self.port:
            for port in self.port.all():
                    ret = ret + "Port:<strong>%s</strong> <br/>" %(port)
        if self.protocol:
            for protocol in self.protocol.all():
                    ret = ret + "Protocol:<strong>%s</strong> <br/>" %(protocol)
        if self.destinationport:
            for port in self.destinationport.all():
                    ret = ret + "Dst Port:<strong>%s</strong> <br/>" %(port)
        if self.sourceport:
            for port in self.sourceport.all():
                    ret = ret +"Src Port:<strong>%s</strong> <br/>" %(port)
        if self.dscp:
            for dscp in self.dscp.all():
                    ret = ret + "%s Port:<strong>%s</strong> <br/>" %(ret, dscp)
        return ret.rstrip('<br/>')
        
    get_match.short_description = 'Match statement'
    get_match.allow_tags = True
    
    @property
    def applier_peer(self):
        try:
            applier_peer = self.applier.get_profile().peer
        except:
            applier_peer = None
        return applier_peer
    
    @property
    def days_to_expire(self):
        if self.status not in ['EXPIRED', 'ADMININACTIVE', 'ERROR', 'INACTIVE']:
            expiration_days = (self.expires - datetime.date.today()).days
            if expiration_days < settings.EXPIRATION_NOTIFY_DAYS:
                return "%s" %expiration_days
            else:
                return False
        else:
            return False

def send_message(msg, user):
#    username = user.username
    peer = user
    b = beanstalkc.Connection()
    b.use(settings.POLLS_TUBE)
    tube_message = json.dumps({'message': str(msg), 'username':peer})
    b.put(tube_message)
    b.close()
