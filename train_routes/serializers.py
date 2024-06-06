from django.db import transaction
from rest_framework import serializers

from train_routes.models import (
    Station,
    Route,
    TrainType,
    Train,
    Journey,
    Crew,
    Order,
    Ticket
)


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longtitude")


class RouteSerializer(serializers.ModelSerializer):
    source = StationSerializer(many=False, read_only=False)
    destination = StationSerializer(many=False, read_only=False)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=False)
    destination = StationSerializer(many=False, read_only=False)


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class TrainTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "image"
        )

    @transaction.atomic()
    def create(self, validated_data):
        train_type = validated_data.pop("train_type")
        train = Train.objects.create(train_type=train_type, **validated_data)

        return train


class TrainListSerializer(TrainSerializer):
    train_type = serializers.CharField(
        read_only=True,
        source="train_type.name"
    )


class TrainImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = (
            "id",
            "image",
        )


class JourneySerializer(serializers.ModelSerializer):

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time"
        )

    @transaction.atomic
    def create(self, validated_data):
        route = validated_data.pop("route")
        train = validated_data.pop("train")
        journey = Journey.objects.create(
            train=train,
            route=route,
            **validated_data
        )

        return journey


class JourneyDetailSerializer(serializers.ModelSerializer):
    train = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    route = RouteSerializer()
    taken_places = serializers.IntegerField(
        read_only=True,
        source="tickets.count"
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "taken_places",
            "departure_time",
            "arrival_time"
        )


class JourneyListSerializer(serializers.ModelSerializer):
    train = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    route = serializers.SlugRelatedField(
        read_only=True,
        slug_field="distance"
    )
    tickets_available = serializers.IntegerField(
        read_only=True,
    )
    cargo_num_available = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "tickets_available",
            "cargo_num_available",
            "departure_time",
            "arrival_time"
        )


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "journeys"
        )


class CrewListSerializer(CrewSerializer):
    journeys = JourneyListSerializer(many=True)


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = (
            "id",
            "cargo",
            "seat",
            "journey",
        )

    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            serializers.ValidationError
        )
        return data


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(
        many=False,
        read_only=True,
    )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets"
        )

    @transaction.atomic()
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(
                order=order, **ticket_data
            )

        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets"
        )


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketListSerializer(read_only=True, many=True)
