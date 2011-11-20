# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

from django.db import models
from django.contrib.auth.models import User
from utils import proxy as PR
from ipaddr import *
import logging

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


    
class MatchAddress(models.Model):
    address = models.CharField(max_length=255, help_text=u"Network address. Use address/CIDR notation")
    def __unicode__(self):
        return self.address

    def clean(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        try:
            address = IPNetwork(self.address)
            self.address = address.exploded
        except Exception:
            raise ValidationError('Invalid network address format')

    class Meta:
        db_table = u'match_address'

class MatchPort(models.Model):
    port = models.CharField(max_length=24)
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

   
class ThenAction(models.Model):
    action = models.CharField(max_length=60, choices=THEN_CHOICES)
    action_value = models.CharField(max_length=255, blank=True, null=True)
    def __unicode__(self):
        return "%s %s" %(self.action, self.action_value)
    class Meta:
        db_table = u'then_action'

class Route(models.Model):
    name = models.CharField(max_length=128)
    applier = models.ForeignKey(User)
    destination = models.CharField(max_length=32, blank=True, null=True, help_text=u"Network address. Use address/CIDR notation")
    destinationport = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchDestinationPort")
    dscp = models.ManyToManyField(MatchDscp, blank=True, null=True)
    fragmenttype = models.CharField(max_length=20, choices=FRAGMENT_CODES, blank=True, null=True)
    icmpcode = models.CharField(max_length=32, blank=True, null=True)
    icmptype = models.CharField(max_length=32, blank=True, null=True)
    packetlength = models.IntegerField(blank=True, null=True)
    port = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchPort")
    protocol = models.CharField(max_length=32, blank=True, null=True)
    source = models.CharField(max_length=32, blank=True, null=True, help_text=u"Network address. Use address/CIDR notation")
    sourceport = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchSourcePort")
    tcpflag = models.CharField(max_length=128, blank=True, null=True)
    then = models.ManyToManyField(ThenAction)
    filed = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    expires = models.DateTimeField()
    response = models.CharField(max_length=512, blank=True, null=True)
    comments = models.TextField(null=True, blank=True)

    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'route'
    
    def clean(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        if self.destination:
            try:
                address = IPNetwork(self.address)
                self.address = address.exploded
            except Exception:
                raise ValidationError('Invalid network address format')
        if self.source:
            try:
                address = IPNetwork(self.address)
                self.address = address.exploded
            except Exception:
                raise ValidationError('Invalid network address format')
    
    def save(self, *args, **kwargs):
        applier = PR.Applier(route_object=self)
        commit, response = applier.apply()
        if commit:
            self.is_online = True
            self.response = response
        else:
            self.is_online = False
            self.response = response
        super(Route, self).save(*args, **kwargs)
    
    def is_synced(self):
        
        found = False
        get_device = PR.Retriever()
        device = get_device.fetch_device()
        try:
            routes = device.routing_options[0].routes
        except Exception as e:
            logger.error("No routing options on device. Exception: %s" %e)
            return False
        for route in routes:
            if route.name == self.name:
                found = True
                logger.info('Found a matching route name')
                devicematch = route.match
                routematch = self.match
                try:
                    assert(routematch.matchDestination.address)
                    assert(devicematch['destination'][0])
                    if routematch.matchDestination.address == devicematch['destination'][0]:
                        found = found and True
                        logger.info('Found a matching destination')
                    else:
                        found = False
                        logger.info('Destination fields do not match')
                except:
                    pass
                try:
                    assert(routematch.matchSource.address)
                    assert(devicematch['source'][0])
                    if routematch.matchSource.address == devicematch['source'][0]:
                        found = found and True
                        logger.info('Found a matching source')
                    else:
                        found = False
                        logger.info('Source fields do not match')
                except:
                    pass
                try:
                    assert(routematch.matchfragmenttype.fragmenttype)
                    assert(devicematch['fragment'][0])
                    if routematch.matchfragmenttype.fragmenttype == devicematch['fragment'][0]:
                        found = found and True
                        logger.info('Found a matching fragment type')
                    else:
                        found = False
                        logger.info('Fragment type fields do not match')
                except:
                    pass
                try:
                    assert(routematch.matchicmpcode.icmp_code)
                    assert(devicematch['icmp-code'][0])
                    if routematch.matchicmpcode.icmp_code == devicematch['icmp-code'][0]:
                        found = found and True
                        logger.info('Found a matching icmp code')
                    else:
                        found = False
                        logger.info('Icmp code fields do not match')
                except:
                    pass
                try:
                    assert(routematch.matchicmptype.icmp_type)
                    assert(devicematch['icmp-type'][0])
                    if routematch.matchicmpcode.icmp_type == devicematch['icmp-type'][0]:
                        found = found and True
                        logger.info('Found a matching icmp type')
                    else:
                        found = False
                        logger.info('Icmp type fields do not match')
                except:
                    pass
                try:
                    assert(routematch.matchprotocol.protocol)
                    assert(devicematch['protocol'][0])
                    if routematch.matchprotocol.protocol == devicematch['protocol'][0]:
                        found = found and True
                        logger.info('Found a matching protocol')
                    else:
                        found = False
                        logger.info('Protocol fields do not match')
                except:
                    pass
                if found and not self.is_online:
                     logger.error('Rule is applied on device but appears as offline')
                     found = False
        
        return found

    
    def get_then(self):
        ret = ''
        then_statements = self.then.thenaction.all()
        for statement in then_statements:
            if statement.action_value:
                ret = "%s %s:<strong>%s</strong><br/>" %(ret, statement.action, statement.action_value)
            else: 
                ret = "%s %s<br>" %(ret, statement.action)
        return ret.rstrip(',')
    
    get_then.short_description = 'Then statement'
    get_then.allow_tags = True

    def get_match(self):
        ret = ''
        match = self.match
        if match.matchDestination:
            ret = ret = '%s Destination Address:<strong>%s</strong><br/>' %(ret, match.matchDestination)
        if match.matchfragmenttype:
            ret = ret = "%s Fragment Type:<strong>%s</strong><br/>" %(ret, match.matchfragmenttype)
        if match.matchicmpcode:
            ret = ret = "%s ICMP code:<strong>%s</strong><br/>" %(ret, match.matchicmpcode)
        if match.matchicmptype:
            ret = ret = "%s ICMP Type:<strong>%s</strong><br/>" %(ret, match.matchicmptype)
        if match.matchpacketlength:
            ret = ret = "%s Packet Length:<strong>%s</strong><br/>" %(ret, match.matchpacketlength)
        if match.matchprotocol:
            ret = ret = "%s Protocol:<strong>%s</strong><br/>" %(ret, match.matchprotocol)
        if match.matchSource:
            ret = ret = "%s Source Address:<strong>%s</strong><br/>" %(ret, match.matchSource)
        if match.matchTcpFlag:
            ret = ret = "%s TCP flag:<strong>%s</strong><br/>" %(ret, match.matchTcpFlag)
        if match.matchport:
            for port in match.matchport.all():
                    ret = "%s Port:<strong>%s</strong><br/>" %(ret, port)
        if match.matchDestinationPort:
            for port in match.matchDestinationPort.all():
                    ret = "%s Port:<strong>%s</strong><br/>" %(ret, port)
        if match.matchSourcePort:
            for port in match.matchSourcePort.all():
                    ret = "%s Port:<strong>%s</strong><br/>" %(ret, port)
        if match.matchdscp:
            for dscp in match.matchdscp.all():
                    ret = "%s Port:<strong>%s</strong><br/>" %(ret, dscp)
        return ret.rstrip('<br/>')
        
    get_match.short_description = 'Match statement'
    get_match.allow_tags = True

