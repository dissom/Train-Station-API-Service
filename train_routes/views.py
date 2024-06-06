from datetime import datetime
from django.db.models import F, Count
# from django.db.models.manager import BaseManager
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

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
    JourneyDetailSerializer,
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


def _params_to_int(qs) -> list[int]:
    """Convert a list of strings to a list of integers"""
    return [int(id) for id in qs.split(",")]


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
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
    queryset = Train.objects.all().select_related("train_type")
    serializer_class = TrainSerializer

    def get_queryset(self):
        """Retrieve trains with filters"""
        queryset = self.queryset
        types = self.request.query_params.get("types")

        if types:
            queryset = queryset.filter(train_type__name__icontains=types)

        return queryset

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action in ("list", "retrieve"):
            serializer = TrainListSerializer
        return serializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser]
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to Train"""
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="train types",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by types (ex. ?types={type_name1}, {type_name2})"
                )
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """A list of trains"""
        return super().list(request, *args, **kwargs)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all().select_related()
    serializer_class = JourneySerializer

    def get_queryset(self):
        """Retrieve journeys with filters"""
        queryset = self.queryset

        train_name = self.request.query_params.get("train_name")
        if train_name:
            queryset = queryset.filter(train__name__icontains=train_name)

        departure = self.request.query_params.get("departure")
        if departure:
            queryset = queryset.filter(departure_time__contains=departure)

        arrival = self.request.query_params.get("arrival")
        if departure:
            queryset = queryset.filter(arrival_time__contains=arrival)

        if self.action == "list":
            queryset = (
                queryset
                .annotate(
                    tickets_available=F("train__places_in_cargo")
                    - Count("tickets"),
                    cargo_num_available=F("train__cargo_num")
                    - Count("tickets__cargo")
                )
                .order_by("id")
            )
        elif self.action == "retrieve":
            queryset = queryset
        return queryset

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = JourneyListSerializer
        elif self.action == "retrieve":
            serializer = JourneyDetailSerializer
        return serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="journeys",
                type=OpenApiTypes.STR,
                description="Filter journeys by train name "
                            "(ex. ?train_name={train_name1}, {train_name2}...)"
            ),
            OpenApiParameter(
                name="departure",
                type=OpenApiTypes.DATE,
                description="Filter by departure date "
                            "(ex. ?departure=2024-06-29)"
            ),
            OpenApiParameter(
                name="arrival",
                type=OpenApiTypes.DATE,
                description="Filter by arrival date "
                            "(ex. ?departure=2024-06-29)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """A list of journeys"""
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all().prefetch_related(
        "journeys__route",
        "journeys__train",
        "journeys__train",
        "journeys__route__source",
        "journeys__route__destination",
    )
    serializer_class = CrewSerializer

    def get_queryset(self):
        """Retrieve crew with filters"""
        queryset = self.queryset

        train_name = self.request.query_params.get("train_name")
        if train_name:
            queryset = queryset.filter(
                journeys__train__name__icontains=train_name
            )

        journeys = self.request.query_params.get("journeys")
        if journeys:
            journeys_ids = _params_to_int(journeys)
            queryset = queryset.filter(journeys__id__in=journeys_ids)

        departure = self.request.query_params.get("departure")
        if departure:
            queryset = queryset.filter(
                journeys__departure_time__icontains=departure
            )

        arrival = self.request.query_params.get("arrival")
        if arrival:
            queryset = queryset.filter(
                journeys__arrival_time__icontains=arrival
            )

        return queryset

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = CrewListSerializer
        return serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="train name",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by train name (ex. ?train={train_name1}"
                    ", {train_name2}...)"
                )
            ),
            OpenApiParameter(
                name="journeys",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by journeys ids (ex. ?journeys=1,5)"
            ),
            OpenApiParameter(
                name="departure",
                type=OpenApiTypes.DATE,
                description="Filter by departure date "
                            "(ex. ?departure_date=2024-06-01)"
            ),
            OpenApiParameter(
                name="arrival",
                type=OpenApiTypes.DATE,
                description="Filter by arrival date "
                            "(ex. ?arrival_date=2024-06-01)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get crew list"""
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related(
        "tickets__order",
    )
    serializer_class = OrderSerializer
    permission_classes = ()

    def get_queryset(self):
        """A list of user orders"""
        queryset = self.queryset.filter(user=self.request.user)

        orders_ids = self.request.query_params.get("orders_ids")
        print(orders_ids)
        if orders_ids:
            orders_ids = _params_to_int(orders_ids)
            queryset = queryset.filter(id__in=orders_ids)

        created_at = self.request.query_params.get("created_at")

        if created_at:
            created_at = datetime.strptime(created_at, "%Y-%m-%d").date()
            queryset = queryset.filter(created_at__icontains=created_at)

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="created_at",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter orders by creation date "
                            "(ex. ?created_at=2024-06-01)"
            ),
            OpenApiParameter(
                name="orders_ids",
                type=OpenApiTypes.DATE,
                description="Filter orders by IDs (ex. ?orders_ids=1,2,3...)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """A list of oders"""
        return super().list(request, *args, **kwargs)
