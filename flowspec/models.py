# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

from django.db import models
from django.contrib.auth.models import User

import nxpy as np
from ncclient import manager
from ncclient.transport.errors import AuthenticationError, SSHError
from lxml import etree as ET
from ipaddr import *

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
            assert(IPNetwork(self.address))
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

class MatchFragmentType(models.Model):
    fragmenttype = models.CharField(max_length=20, choices=FRAGMENT_CODES)
    def __unicode__(self):
        return self.fragmenttype
    class Meta:
        db_table = u'match_fragment_type'
    
class MatchIcmpCode(models.Model):
    icmp_code = models.CharField(max_length=64)
    def __unicode__(self):
        return self.icmp_code
    class Meta:
        db_table = u'match_icmp_code'    

class MatchIcmpType(models.Model):
    icmp_type = models.CharField(max_length=64)
    class Meta:
        db_table = u'match_icmp_type'    

class MatchPacketLength(models.Model):
    packet_length = models.IntegerField()
    class Meta:
        db_table = u'match_packet_length'    

class MatchProtocol(models.Model):
    protocol = models.CharField(max_length=64)
    def __unicode__(self):
        return self.protocol
    class Meta:
        db_table = u'match_protocol'    

class MatchTcpFlag(models.Model):
    tcp_flag = models.CharField(max_length=255)
    def __unicode__(self):
        return self.tcp_flag
    class Meta:
        db_table = u'match_tcp_flag'    
    
class ThenAction(models.Model):
    action = models.CharField(max_length=60, choices=THEN_CHOICES)
    action_value = models.CharField(max_length=255, blank=True, null=True)
    def __unicode__(self):
        return "%s %s" %(self.action, self.action_value)
    class Meta:
        db_table = u'then_action'

class ThenStatement(models.Model):
    thenaction = models.ManyToManyField(ThenAction)
    class Meta:
        db_table = u'then'    

class MatchStatement(models.Model):
    matchDestination = models.ForeignKey(MatchAddress, blank=True, null=True, related_name="matchDestination")
    matchDestinationPort = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchDestinationPort")
    matchdscp = models.ManyToManyField(MatchDscp, blank=True, null=True)
    matchfragmenttype = models.ForeignKey(MatchFragmentType, blank=True, null=True)
    matchicmpcode = models.ForeignKey(MatchIcmpCode, blank=True, null=True)
    matchicmptype = models.ForeignKey(MatchIcmpType, blank=True, null=True)
    matchpacketlength = models.ForeignKey(MatchPacketLength, blank=True, null=True)
    matchport = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchPort")
    matchprotocol = models.ForeignKey(MatchProtocol, blank=True, null=True)
    matchSource = models.ForeignKey(MatchAddress, blank=True, null=True, related_name="matchSource")
    matchSourcePort = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchSourcePort")
    matchTcpFlag = models.ForeignKey(MatchTcpFlag, blank=True, null=True)
    
#    def clean(self, *args, **kwargs):
#        clean_error = True
#        from django.core.exceptions import ValidationError
#        if not (self.matchDestination or self.matchfragmenttype or self.matchicmpcode or self.matchicmptype 
#                   or self.matchpacketlength or self.matchprotocol or self.matchSource or self.matchTcpFlag):
#            clean_error = False
#        try:
#            assert(self.matchDestinationPort)
#            clean_error = False
#        except:
#            pass
#        try: 
#            assert(self.matchSourcePort)
#            clean_error = False
#        except:
#            pass
#        try:
#            assert(self.matchport)
#            clean_error = False
#        except:
#            pass
#        try:
#            print self.matchdscp
#            assert(self.matchdscp)
#            clean_error = False
#        except:
#            pass
#        if clean_error:
#            raise ValidationError('At least one match statement has to be declared')
        
    class Meta:
        db_table = u'match'

class Route(models.Model):
    name = models.CharField(max_length=128)
    applier = models.ForeignKey(User)
    match = models.ForeignKey(MatchStatement)
    then = models.ForeignKey(ThenStatement)
    filed = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    expires = models.DateTimeField()
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = u'route'
        
    def save(self, *args, **kwargs):
        # Begin translation to device xml configuration
        device = np.Device()
        flow = np.Flow()
        route = np.Route()
        flow.routes.append(route)
        device.routing_options.append(flow)
        route.name = self.name
        match = self.match
        if match.matchSource:
            route.match['source'].append(match.matchSource.address)
        if match.matchDestination:
            route.match['destination'].append(match.matchDestination.address)
        if match.matchprotocol:
            route.match['protocol'].append(match.matchprotocol.protocol)
        if match.matchport:
            for port in match.matchport.all():
                route.match['port'].append(port.port)
        if match.matchDestinationPort:
            for port in match.matchDestinationPort.all():
                route.match['destination-port'].append(port.port)
        if match.matchSourcePort:
            for port in match.matchSourcePort.all():
                route.match['source-port'].append(port.port)
        if match.matchicmpcode:
            route.match['icmp-code'].append(match.matchicmpcode.icmp_code)
        if match.matchicmptype:
            route.match['icmp-type'].append(match.matchicmptype.icmp_type)
        if match.matchTcpFlag:
            route.match['tcp-flags'].append(match.matchTcpFlag.tcp_flags)
        if match.matchdscp:
            for dscp in match.matchdscp.all():
                route.match['dscp'].append(dscp.dscp)
        if match.matchfragmenttype:
            route.match['fragment'].append(match.matchfragmenttype.fragmenttype)
        then = self.then
        for thenaction in then.thenaction.all():
            if thenaction.action_value:
                route.then[thenaction.action] = thenaction.action_value
            else:
                route.then[thenaction.action] = True
        print ET.tostring(device.export())
        super(Route, self).save(*args, **kwargs)