from django.db import models
from django.contrib.auth.models import User

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
    destination = models.CharField(max_length=255)
    class Meta:
        db_table = u'match_address'

class MatchPort(models.Model):
    port = models.CharField(max_length=24)
    class Meta:
        db_table = u'match_port'    

class MatchDscp(models.Model):
    dscp = models.CharField(max_length=24)
    class Meta:
        db_table = u'match_dscp'

class MatchFragmentType(models.Model):
    fragmenttype = models.CharField(max_length=20, choices=FRAGMENT_CODES)
    class Meta:
        db_table = u'match_fragment_type'
    
class MatchIcmpCode(models.Model):
    icmp_code = models.CharField(max_length=64)
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
    class Meta:
        db_table = u'match_protocol'    

class MatchTcpFlag(models.Model):
    tcp_flag = models.CharField(max_length=255)
    class Meta:
        db_table = u'match_tcp_flag'    
    
class ThenAction(models.Model):
    action = models.CharField(max_length=60, choices=THEN_CHOICES)
    action_value = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        db_table = u'then_action'

class ThenStatement(models.Model):
    thenaction = models.ManyToManyField(ThenAction, blank=True, null=True)
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
    matchport = models.ManyToManyField(MatchPort, blank=True, null=True)
    matchprotocol = models.ForeignKey(MatchProtocol, blank=True, null=True)
    matchSource = models.ManyToManyField(MatchAddress, blank=True, null=True, related_name="matchSource")
    matchSourcePort = models.ForeignKey(MatchPort, blank=True, null=True, related_name="matchSourcePort")
    matchTcpFlag = models.ForeignKey(MatchTcpFlag, blank=True, null=True)
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
    class Meta:
        db_table = u'route'