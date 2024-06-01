from rest_framework import viewsets

from train_routes.models import (
    Station,
    Route,
    TrainType,
    Train,
    Journey,
    Crew,
    Order,
)
from train_routes.serializers import (
    CrewListSerializer,
    JourneyListSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    RouteDetailSerializer,
    RouteListSerializer,
    StationSerializer,
    RouteSerializer,
    TrainListSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    JourneySerializer,
    CrewSerializer,
    OrderSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = RouteListSerializer
        elif self.action == "retrieve":
            serializer = RouteDetailSerializer
        return serializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action in ("list", "retrieve"):
            serializer = TrainListSerializer
        return serializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action in ("list", "retrieve"):
            serializer = JourneyListSerializer
        return serializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = CrewListSerializer
        return serializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = OrderListSerializer
        elif self.action == "retrieve":
            serializer = OrderDetailSerializer
        return serializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# class TicketViewSet(viewsets.ModelViewSet):
#     queryset = Ticket.objects.all()
#     serializer_class = TicketSerializer
