from rest_framework import serializers
from flowspec.models import (
    Route,
    MatchPort,
    ThenAction,
    FragmentType,
    MatchProtocol
)
from flowspec.validators import (
    clean_source,
    clean_destination,
    clean_expires,
    check_if_rule_exists
)


class RouteSerializer(serializers.HyperlinkedModelSerializer):
    applier = serializers.CharField(source='applier_username', read_only=True)

    def validate(self, data):
        user = self.context.get('request').user
        # validate source
        source = data.get('source')
        res = clean_source(
            user,
            source
        )
        if res != source:
            raise serializers.ValidationError(res)

        # validate destination
        destination = data.get('destination')
        res = clean_destination(
            user,
            destination
        )
        if res != destination:
            raise serializers.ValidationError(res)

        # validate expires
        expires = data.get('expires')
        res = clean_expires(
            expires
        )
        if res != expires:
            raise serializers.ValidationError(res)

        # check if rule already exists with different name
        fields = {
            'source': data.get('source'),
            'destination': data.get('destination'),
        }
        exists = check_if_rule_exists(fields)
        if exists:
            raise serializers.ValidationError(exists)
        return data

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
            'requesters_address',
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
