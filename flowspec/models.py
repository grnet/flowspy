# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from utils import proxy as PR
from ipaddr import *
from datetime import *
import logging
from flowspec.tasks import *
from time import sleep

from flowspy.utils import beanstalkc


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


def days_offset(): return datetime.now() + timedelta(days = settings.EXPIRATION_DAYS_OFFSET)
    
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
    action = models.CharField(max_length=60, choices=THEN_CHOICES, verbose_name="Action")
    action_value = models.CharField(max_length=255, blank=True, null=True, verbose_name="Action Value")
    def __unicode__(self):
        return "%s: %s" %(self.action, self.action_value)
    class Meta:
        db_table = u'then_action'

class Route(models.Model):
    name = models.SlugField(max_length=128)
    applier = models.ForeignKey(User, blank=True, null=True)
    source = models.CharField(max_length=32, blank=True, null=True, help_text=u"Network address. Use address/CIDR notation", verbose_name="Source Address")
    sourceport = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchSourcePort", verbose_name="Source Port")
    destination = models.CharField(max_length=32, help_text=u"Network address. Use address/CIDR notation", verbose_name="Destination Address")
    destinationport = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchDestinationPort", verbose_name="Destination Port")
    port = models.ManyToManyField(MatchPort, blank=True, null=True, related_name="matchPort", verbose_name="Port" )
    dscp = models.ManyToManyField(MatchDscp, blank=True, null=True, verbose_name="DSCP")
    fragmenttype = models.CharField(max_length=20, choices=FRAGMENT_CODES, blank=True, null=True, verbose_name="Fragment Type")
    icmpcode = models.CharField(max_length=32, blank=True, null=True, verbose_name="ICMP Code")
    icmptype = models.CharField(max_length=32, blank=True, null=True, verbose_name="ICMP Type")
    packetlength = models.IntegerField(blank=True, null=True, verbose_name="Packet Length")
    protocol = models.CharField(max_length=32, blank=True, null=True, verbose_name="Protocol")
    tcpflag = models.CharField(max_length=128, blank=True, null=True, verbose_name="TCP flag")
    then = models.ManyToManyField(ThenAction, verbose_name="Then")
    filed = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    expires = models.DateField(default=days_offset, blank=True, null=True,)
    response = models.CharField(max_length=512, blank=True, null=True)
    comments = models.TextField(null=True, blank=True, verbose_name="Comments")

    
    def __unicode__(self):
        return self.name
    
    class Meta:
        unique_together = (("name", "is_active"),)
        db_table = u'route'
    
    def clean(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        if self.destination:
            try:
                address = IPNetwork(self.destination)
                self.destination = address.exploded
            except Exception:
                raise ValidationError('Invalid network address format at Destination Field')
        if self.source:
            try:
                address = IPNetwork(self.source)
                self.source = address.exploded
            except Exception:
                raise ValidationError('Invalid network address format at Source Field')
    
#    def save(self, *args, **kwargs):
#        edit = False
#        if self.pk:
#            #This is an edit
#            edit = True
#        super(Route, self).save(*args, **kwargs)
#        if not edit:
#            response = add.delay(self)
#            logger.info("Got save job id: %s" %response)
    
    def commit_add(self, *args, **kwargs):
        send_message("Adding route %s. Please wait..." %self.name)
        response = add.delay(self)
        logger.info("Got save job id: %s" %response)

    def deactivate(self):
        self.is_online = False
        self.is_active = False
        self.save()
#    def delete(self, *args, **kwargs):
#        response = delete.delay(self)
#        logger.info("Got delete job id: %s" %response)
        
    def commit_edit(self, *args, **kwargs):
        send_message("Editing route %s. Please wait..." %self.name)
        response = edit.delay(self)
        logger.info("Got edit job id: %s" %response)

    def commit_delete(self, *args, **kwargs):
        send_message("Removing route %s. Please wait..." %self.name)
        response = delete.delay(self)
        logger.info("Got edit job id: %s" %response)
#    
#    def delete(self, *args, **kwargs):
#        response = delete.delay(self)
#        logger.info("Got delete job id: %s" %response)
    def is_synced(self):
        
        found = False
        get_device = PR.Retriever()
        device = get_device.fetch_device()
        try:
            routes = device.routing_options[0].routes
        except Exception as e:
            self.is_online = False
            self.save()
            logger.error("No routing options on device. Exception: %s" %e)
            return False
        for route in routes:
            if route.name == self.name:
                found = True
                logger.info('Found a matching route name')
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
                try:
                    assert(self.protocol)
                    assert(devicematch['protocol'][0])
                    if self.protocol == devicematch['protocol'][0]:
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
            ret = '%s Destination Address:<strong>%s</strong><br/>' %(ret, self.destination)
        if self.fragmenttype:
            ret = "%s Fragment Type:<strong>%s</strong><br/>" %(ret, self.fragmenttype)
        if self.icmpcode:
            ret = "%s ICMP code:<strong>%s</strong><br/>" %(ret, self.icmpcode)
        if self.icmptype:
            ret = "%s ICMP Type:<strong>%s</strong><br/>" %(ret, self.icmptype)
        if self.packetlength:
            ret = "%s Packet Length:<strong>%s</strong><br/>" %(ret, self.packetlength)
        if self.protocol:
            ret = "%s Protocol:<strong>%s</strong><br/>" %(ret, self.protocol)
        if self.source:
            ret = "%s Source Address:<strong>%s</strong><br/>" %(ret, self.source)
        if self.tcpflag:
            ret = "%s TCP flag:<strong>%s</strong><br/>" %(ret, self.tcpflag)
        if self.port:
            for port in self.port.all():
                    ret = ret + "Port:<strong>%s</strong><br/>" %(port)
        if self.destinationport:
            for port in self.destinationport.all():
                    ret = ret + "Destination Port:<strong>%s</strong><br/>" %(port)
        if self.sourceport:
            for port in self.sourceport.all():
                    ret = ret +"Source Port:<strong>%s</strong><br/>" %(port)
        if self.dscp:
            for dscp in self.dscp.all():
                    ret = ret + "%s Port:<strong>%s</strong><br/>" %(ret, dscp)
        return ret.rstrip('<br/>')
        
    get_match.short_description = 'Match statement'
    get_match.allow_tags = True

def send_message(msg):
    b = beanstalkc.Connection()
    b.use(settings.POLLS_TUBE)
    b.put(str(msg))
    b.close()
