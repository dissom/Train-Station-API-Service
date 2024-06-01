from django.contrib import admin

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


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(Station)
admin.site.register(Route)
admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Journey)
admin.site.register(Crew)
admin.site.register(Ticket)
