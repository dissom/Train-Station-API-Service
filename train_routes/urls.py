from rest_framework import routers
from train_routes.views import (
    StationViewSet,
    RouteViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    JourneyViewSet,
    CrewViewSet,
    OrderViewSet,
)


router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("train-types", TrainTypeViewSet)
router.register("trains", TrainViewSet, basename="train")
router.register("journeys", JourneyViewSet)
router.register("crew", CrewViewSet)
router.register("orders", OrderViewSet)


urlpatterns = router.urls


app_name = "train_routes"
