from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db.models.manager import BaseManager
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from train_routes.models import (
    Crew,
    Journey,
    Order,
    Route,
    Station,
    Train,
    TrainType,
)
from train_routes.serializers import (
    JourneyListSerializer,
    RouteSerializer,
    TrainListSerializer,
)


TRAIN_URL = reverse("train_routes:train-list")
ROUTE_URL = reverse("train_routes:route-list")
ORDER_URL = reverse("train_routes:order-list")
JOURNEY_URL = reverse("train_routes:journey-list")
STATION_URL = reverse("train_routes:station-list")


def detail_train_url(train_id):
    return reverse("train_routes:train-detail", args=[train_id])


def sample_station(**params):
    defaults = {"name": "TestStation", "latitude": 50.05, "longtitude": 20.02}
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    source = Station.objects.create(
        name="TestStation", latitude=50.05, longtitude=20.02
    )
    destination = Station.objects.create(
        name="TestStation2", latitude=30.00, longtitude=0.15
    )
    defaults = {"source": source, "destination": destination, "distance": 100}
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_train_type(**params):
    defaults = {"name": "Test_Type"}
    defaults.update(params)
    train_type, created = TrainType.objects.get_or_create(
        name=defaults["name"], defaults=defaults
    )
    return train_type


def sample_train(**params):
    train_type = sample_train_type()
    defaults = {
        "name": "Test",
        "cargo_num": 100,
        "places_in_cargo": 100,
        "train_type": train_type,
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


def sample_journey(**params):
    route = sample_route()
    train = sample_train()
    defaults = {
        "route": route,
        "train": train,
        "departure_time": "2024-06-29 00:15",
        "arrival_time": "2024-06-29 10:20",
    }

    defaults.update(params)

    return Journey.objects.create(**defaults)


def sample_crew(**params):
    defaults = {"first_name": "Test", "last_name": "User"}
    defaults.update(params)
    crew = Crew.objects.create(**defaults)

    if "journeys" in params:
        crew.journeys.set(params["journeys"])

    return crew


def sample_user(**params):
    defaults = {
        "email": "test@test.com",
        "password": "testpass",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


class UnauthenticatedApiTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(JOURNEY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_station(self) -> None:
        station = {
            "name": "TestStation",
            "latitude": 50.05,
            "longtitude": 20.02
        }

        response = self.client.post(STATION_URL, station)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_train(self) -> None:
        train = sample_train()

        url = detail_train_url(train.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_take_list_of_routes(self):

        response = self.client.get(ROUTE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):

        journey = sample_journey()

        tickets_data = [
            {"cargo": 1, "seat": 2, "journey": journey.id},
            {"cargo": 2, "seat": 3, "journey": journey.id},
        ]

        payload = {
            "created_at": datetime.now(),
            "user": self.user.id,
            "tickets": tickets_data,
        }

        response = self.client.post(
            ORDER_URL,
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(id=response.data["id"])

        self.assertEqual(order.tickets.count(), 2)


class AdminApiTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_station(self):
        station = {
            "name": "TestStation",
            "latitude": 50.05,
            "longtitude": 20.02
        }

        response = self.client.post(STATION_URL, station)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_route_and_take_list_of_routes(self):
        source = sample_station()
        destination = sample_station(
            name="TestStation2",
            latitude=30,
            longtitude=45
        )

        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 100
        }

        response = self.client.post(ROUTE_URL, payload)

        routes = Route.objects.all()
        serializer = RouteSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data[-1])
        self.assertEqual(routes.count(), 1)

    def test_filter_trains_by_type(self):
        train_type_1 = sample_train_type(name="Type_1")
        train_type_2 = sample_train_type(name="Type_2")

        train_1 = sample_train(
            name="Train 1",
            train_type=train_type_1
        )
        train_2 = sample_train(
            name="Train 2",
            train_type=train_type_2
        )

        response = self.client.get(
            TRAIN_URL,
            {"types": f"{train_1.train_type}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer1 = TrainListSerializer(train_1)
        serializer2 = TrainListSerializer(train_2)

        self.assertIn(serializer1.data, response.data["results"])
        self.assertNotIn(serializer2.data, response.data["results"])

    def test_filter_journeys(self):
        route: Route = sample_route()
        train = sample_train()
        unique_train = sample_train(name="Unique")

        journey_1 = Journey.objects.create(
            route=route,
            train=train,
            departure_time=datetime.now(),
            arrival_time=datetime.now() + timedelta(days=1),
        )
        journey_2 = Journey.objects.create(
            route=route,
            train=unique_train,
            departure_time=datetime.now(),
            arrival_time=datetime.now() + timedelta(days=1),
        )

        response = self.client.get(
            JOURNEY_URL,
            {"train_name": f"{journey_1.train}"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer1 = JourneyListSerializer(journey_1)
        serializer2 = JourneyListSerializer(journey_2)

        self.assertEqual(
            serializer1.data["id"], response.data["results"][-1]["id"]
        )
        self.assertNotEqual(
            serializer2.data["id"], response.data["results"][-1]["id"]
        )
