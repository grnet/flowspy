from rest_framework import serializers
from flowspec.models import (
    Route,
    MatchPort,
    ThenAction,
    FragmentType,
    MatchProtocol
)


# Serializers define the API representation.
class RouteSerializer(serializers.HyperlinkedModelSerializer):
    applier = serializers.CharField(source='applier_username', read_only=True)

    class Meta:
        model = Route
        fields = (
            'name',
            'id',
            'comments',
            'applier',
            'source',
            'sourceport',
            'destination',
            'destinationport',
            'port',
            'dscp',
            'fragmenttype',
            'icmpcode',
            'packetlength',
            'protocol',
            'tcpflag',
            'then',
            'filed',
            'last_updated',
            'status',
            'expires',
            'response',
            'comments',
            'requesters_address'
        )
        read_only_fields = ('status', 'expires', 'requesters_address', 'response')


class PortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MatchPort
        fields = ('port', )


class ThenActionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ThenAction
        fields = ('action', 'action_value')


class FragmentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FragmentType
        fields = ('fragmenttype', )


class MatchProtocolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MatchProtocol
        fields = ('protocol', )
