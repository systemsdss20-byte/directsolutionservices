import datetime

from django.forms import ModelForm, DateInput, CheckboxInput
from .models import Event
from django import forms


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "start_time", "end_time", "public"]
        # datetime-local is a HTML5 input type
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter event title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter event description",
                    "rows": 4
                }
            ),
            "start_time": DateInput(
                attrs={"class": "form-control datetimepicker"},
                format="%m-%d-%Y %H:%M",
            ),
            "end_time": forms.DateInput(
                attrs={"class": "form-control datetimepicker"},
                format="%m-%d-%Y %H:%M",
            ),
            "public": CheckboxInput(attrs={"class": "form-check-input ml-1"})
        }
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # input_formats to parse HTML5 datetime-local input to datetime field
        #self.fields["start_time"] = "2023-05-17T15:00"
        #self.fields["start_time"] = datetime.datetime.strptime(self.fields["start_time"], "%m/%d/%Y")
        #self.fields["start_time"].input_formats = ("%Y-%m-%dT%H:%M",)
        #self.fields["end_time"].input_formats = ("%Y-%m-%dT%H:%M",)

    # def clean(self):
    #     super().clean()
    #     public = self.cleaned_data.get('public')
    #     start_time = self.cleaned_data.get('start_time')
    #
    #     if public:
    #         validate = Event.objects.filter(public=public, start_time=start_time, is_deleted=False).count()
    #         if validate:
    #             msg = "Appointment not available"
    #             self.add_error('start_time', msg)

    def clean_start_time(self):
        today = datetime.datetime.today()
        start_time = self.cleaned_data.get('start_time', False)
        if start_time < today:
            raise forms.ValidationError('You cannot add an appointment on a date before today.')

        return start_time

    def save_return(self, user):
        event = self.save(commit=False)
        event.user = user
        event.save()
        return event