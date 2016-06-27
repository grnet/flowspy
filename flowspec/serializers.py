"""
Serializers for flowspec models
"""
from rest_framework import serializers
from flowspec.models import (
    Route, MatchPort, ThenAction, FragmentType, MatchProtocol, MatchDscp)
from flowspec.validators import (
    clean_source, clean_destination, clean_expires, clean_status)


class RouteSerializer(serializers.HyperlinkedModelSerializer):
    """
    A serializer for `Route` objects
    """
    applier = serializers.CharField(source='applier_username', read_only=True)

    def validate_source(self, attrs, source):
        user = self.context.get('request').user
        source_ip = attrs.get('source')
        res = clean_source(user, source_ip)
        if res != source_ip:
            raise serializers.ValidationError(res)
        return attrs

    def validate_destination(self, attrs, source):
        user = self.context.get('request').user
        destination = attrs.get('destination')
        res = clean_destination(user, destination)
        if res != destination:
            raise serializers.ValidationError(res)
        return attrs

    def validate_expires(self, attrs, source):
        expires = attrs.get('expires')
        res = clean_expires(expires)
        if res != expires:
            raise serializers.ValidationError(res)
        return attrs

    def validate_status(self, attrs, source):
        status = attrs.get('status')
        res = clean_status(status)
        if res != status:
            raise serializers.ValidationError(res)
        return attrs

    class Meta:
        model = Route
        fields = (
            'name', 'id', 'comments', 'applier', 'source', 'sourceport',
            'destination', 'destinationport', 'port', 'dscp', 'fragmenttype',
            'icmpcode', 'packetlength', 'protocol', 'tcpflag', 'then', 'filed',
            'last_updated', 'status', 'expires', 'response', 'comments',
            'requesters_address')
        read_only_fields = (
            'requesters_address', 'response', 'last_updated', 'id', 'filed')


class PortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MatchPort
        fields = ('id', 'port', )
        read_only_fields = ('id', )


class ThenActionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ThenAction
        fields = ('id', 'action', 'action_value')
        read_only_fields = ('id', )


class FragmentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FragmentType
        fields = ('id', 'fragmenttype', )
        read_only_fields = ('id', )


class MatchProtocolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MatchProtocol
        fields = ('id', 'protocol', )
        read_only_fields = ('id', )


class MatchDscpSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MatchDscp
        fields = ('id', 'dscp', )
        read_only_fields = ('id', )
