from rest_framework import serializers
from flowspec.models import (
    MatchProtocol,
    FragmentType,
    ThenAction,
    Route,
    MatchPort
)


class MatchProtocolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MatchProtocol
        fields = ('protocol',)


class FragmentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FragmentType
        fields = ('fragmenttype',)


class ThenActionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ThenAction
        fields = ('action', 'action_value')


class RouteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Route
        fields = ('name', 'applier', 'source', 'sourceport', 'destination', 'destinationport', 'port', 'dscp', 'fragmenttype', 'protocol', 'then', 'status', 'comments', 'expires')


class PortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MatchPort
        fields = ('port',)
