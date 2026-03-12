from django.urls import path
from . import views

app_name = "Calendar"

urlpatterns = [
    path("", views.CalendarViewNew.as_view(), name="index"),
    path("event-add/", views.EventView.as_view(), name="add"),
    path("event-edit/<int:id>/", views.EventView.as_view(), name="edit"),
    path("event-details/<int:event_id>", views.event_details),
    path("running-events/", views.CalendarViewNew.as_view(action="running-events")),
]