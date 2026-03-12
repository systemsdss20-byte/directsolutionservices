import calendar
import json
from datetime import timedelta, datetime, date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import generic
from calendar import HTMLCalendar

from django.views.generic import ListView

from .forms import EventForm
from .models import Event
from django.shortcuts import render

from ..Procedure.models import Task
from ..helpers.message import MessageResponse


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


class CalendarView(LoginRequiredMixin, generic.ListView):
    login_url = "Procedure:login"
    model = Event
    template_name = "calendar/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        return context


class EventView(LoginRequiredMixin, generic.ListView):
    login_url = "Procedure:login"
    form_class = EventForm
    url = ""
    method = "POST"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        if 'id' in kwargs:
            event = Event.objects.get(id=kwargs['id'])
            form = EventForm(instance=event)
            self.url = "/calendar/event-edit/%s/" % kwargs['id']
            self.method = "PUT"
        return render(request, "Calendar/form.html", {"form": form, "url": self.url, "method": self.method})

    def put(self, request, *args, **kwargs):
        event = Event.objects.get(pk=kwargs["id"])
        params = json.loads(request.body)
        form = EventForm(params, instance=event)
        if form.is_valid():
            try:
                event = form.save_return(request.user)
                event = event_to_json(request, event)
                return MessageResponse(data=event, description="Updated successfully").success()
            except Exception as e:
                return MessageResponse(description=e).error()
        else:
            return MessageResponse(data={'fields': form.errors}, description="Validation").warning()


class CalendarViewNew(LoginRequiredMixin, generic.View):
    login_url = "Procedure:login"
    template_name = "calendar/calendar.html"
    form_class = EventForm
    action = ""

    def get(self, request, *args, **kwargs):
        events = Event.objects.get_all_events(user=request.user)
        events_month = Event.objects.get_running_events(user=request.user)
        if self.action == "running-events":
            return render(request, 'Calendar/running_events.html', {"events_month": events_month})
        event_list = []
        tasks_list = []
        tasks = Task.objects.filter(Q(created_by=request.user.id, is_completed=False) | Q(assigned_to=request.user.id,
                                                                                          is_completed=False)).filter(
            archived=False)
        # start: '2020-09-16T16:00:00'
        for event in events:
            event_list.append(event_to_json(request, event))
        for task in tasks:
            tasks_list.append(event_to_json(request, task, True))
        event_list.extend(tasks_list)
        context = {"events": event_list, "events_month": events_month, "tasks": tasks,
                   "today": datetime.today().strftime("%m/%d/%Y")}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        forms = self.form_class(request.POST)
        if forms.is_valid():
            if forms.cleaned_data['public'] is None or forms.cleaned_data['public'] == False:
                validate = Event.objects.filter(user=request.user, start_time=forms.clean_start_time(),
                                                is_deleted=False).count()
                if validate != 0:
                    return MessageResponse(description="Appointment not available").error()
            event = forms.save_return(request.user)
            event = event_to_json(request, event)
            return MessageResponse(data=event, description="Successfully saved").success()
        else:
            errors = forms.errors
            return MessageResponse(data={'fields': errors}, description="Validation").warning()

    def delete(self, request, *args, **kwargs):
        params = json.loads(request.body)
        try:
            if 'event_id' in params.keys():
                Event.objects.filter(id=params['event_id']).update(is_deleted=True)
                return MessageResponse(description='Event removed').success()
            return redirect("Calendar:index")
        except Exception as e:
            print(e)
            return MessageResponse(description='Internal Server Error').error()


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day)
        d = ""
        for event in events_per_day:
            d += f"<li> {event.get_html_url} </li>"
        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return "<td></td>"

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ""
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f"<tr> {week} </tr>"

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        events = Event.objects.filter(
            start_time__year=self.year, start_time__month=self.month
        )
        cal = (
            '<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        )  # noqa
        cal += (
            f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n"
        )  # noqa
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, events)}\n"
        return cal


class AllEventsListView(ListView):
    """ All event list views """

    template_name = "calendarapp/events_list.html"
    model = Event

    def get_queryset(self):
        return Event.objects.get_all_events(user=self.request.user)


class RunningEventsListView(ListView):
    """ Running events list view """

    template_name = "calendarapp/events_list.html"
    model = Event

    def get_queryset(self):
        return Event.objects.get_running_events(user=self.request.user)


@login_required(login_url='Procedure:login')
def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    context = {'event': event}
    return render(request, 'Calendar/event_details.html', context)


def event_to_json(request, event, tasks=False):
    groups = []
    color = "#28a745"
    event_calendar = {
        "id": event.id if not tasks else '{0}-{1}'.format('T', event.id),
        "title": event.title,
        "end": '' if tasks else event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if not tasks:
        if event.public and tasks == False:
            groups.append("group1")
        if event.public:
            color = "#023e8a"
        if event.user == request.user:
            groups.append("group2")
        event_calendar["start"] = event.start_time.strftime("%Y-%m-%dT%H:%M:%S")

    if tasks:
        groups.append("group3")
        color = "#347474"
        event_calendar["start"] = event.created_at.strftime("%Y-%m-%d")
    event_calendar["backgroundColor"] = color
    event_calendar["borderColor"] = color
    event_calendar["groups"] = groups
    return event_calendar
