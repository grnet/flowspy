from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework import viewsets
from flowspec.models import (
    Route,
    MatchPort,
    ThenAction,
    FragmentType,
    MatchProtocol
)

from flowspec.serializers import (
    RouteSerializer,
    PortSerializer,
    ThenActionSerializer,
    FragmentTypeSerializer,
    MatchProtocolSerializer,
)

from rest_framework.response import Response

from django.contrib.auth.models import User


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous or self.request.user.is_superuser:
            return Route.objects.all()
        else:
            return Route.objects.filter(applier=self.request.user)

    def list(self, request):
        serializer = RouteSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        route = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = RouteSerializer(route)
        return Response(serializer.data)

    def pre_save(self, obj):
        if self.request.user.is_anonymous:
            obj.applier = User.objects.all()[0]
        else:
            obj.applier = self.request.user


class PortViewSet(viewsets.ModelViewSet):
    queryset = MatchPort.objects.all()
    serializer_class = PortSerializer


class ThenActionViewSet(viewsets.ModelViewSet):
    queryset = ThenAction.objects.all()
    serializer_class = ThenActionSerializer


class FragmentTypeViewSet(viewsets.ModelViewSet):
    queryset = FragmentType.objects.all()
    serializer_class = FragmentTypeSerializer


class MatchProtocolViewSet(viewsets.ModelViewSet):
    queryset = MatchProtocol.objects.all()
    serializer_class = MatchProtocolSerializer

