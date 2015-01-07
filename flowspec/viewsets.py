from rest_framework import viewsets
from flowspec.serializers import (
    MatchProtocolSerializer,
    FragmentTypeSerializer,
    ThenActionSerializer,
    RouteSerializer,
    PortSerializer
)


from flowspec.models import (
    MatchProtocol,
    FragmentType,
    ThenAction,
    Route,
    MatchPort
)


class MatchProtocolViewSet(viewsets.ModelViewSet):
    queryset = MatchProtocol.objects.all()
    serializer_class = MatchProtocolSerializer


class FragmentTypeViewSet(viewsets.ModelViewSet):
    queryset = FragmentType.objects.all()
    serializer_class = FragmentTypeSerializer


class ThenActionViewSet(viewsets.ModelViewSet):
    queryset = ThenAction.objects.all()
    serializer_class = ThenActionSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class PortViewSet(viewsets.ModelViewSet):
    queryset = MatchPort.objects.all()
    serializer_class = PortSerializer
