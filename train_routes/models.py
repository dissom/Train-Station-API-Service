from django.db import models
from train_service import settings


class Station(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longtitude = models.FloatField()

    class Meta:
        verbose_name_plural = "stations"
        ordering = ["name",]

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routes_from",
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routes_to",
    )
    distance = models.IntegerField()

    class Meta:
        verbose_name_plural = "routes"
        indexes = [
            models.Index(
                fields=["source", "destination"]
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.source.name} - {self.destination.name}: {self.distance} km"
        )


class TrainType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    class Meta:
        ordering = ["name",]

    def __str__(self) -> str:
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains",
    )

    def __str__(self) -> str:
        return self.name


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["id",]

    def __str__(self) -> str:
        return f"{self.route} on {self.train.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    journeys = models.ManyToManyField(
        Journey,
        related_name="crew"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.full_name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at",]

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    def __str__(self):
        return f"Ticket {self.id} for Journey {self.journey}"
