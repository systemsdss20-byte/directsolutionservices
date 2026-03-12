from datetime import datetime, timedelta
from django.db import models
from django.db.models import Q
from django.urls import reverse

from ..Procedure.models import User


class EventManager(models.Manager):
    """ Event manager """

    @staticmethod
    def get_all_events(user):
        events = Event.objects.filter( Q(public=True) | Q(user=user), is_active=True, is_deleted=False )
        return events

    @staticmethod
    def get_running_events(user):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        running_events = list()
        events = Event.objects.filter(
            Q(user=user) | Q(public=True),
            is_active=True,
            is_deleted=False,
            end_time__gte=datetime.now().date(),
        ).order_by("start_time")
        for event in events:
            event_color = 'bg-cyan'
            if today.strftime("%Y-%m-%d") == event.start_time.strftime("%Y-%m-%d") or event.end_time.strftime("%Y-%m-%d") <= today.strftime("%Y-%m-%d"):
                event_color = 'bg-danger'
            if tomorrow.strftime("%Y-%m-%d") == event.start_time.strftime("%Y-%m-%d"):
                event_color = 'bg-warning'
            running_events.append({
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "background": event_color
            })
        return running_events

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=False)

    objects = EventManager()
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("Calendar:event-detail", args=(self.id,))

    @property
    def get_html_url(self):
        url = reverse("Calendar:event-detail", args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'