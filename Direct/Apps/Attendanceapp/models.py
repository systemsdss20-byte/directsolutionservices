from datetime import datetime, date, timedelta
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimezoneChoices(models.TextChoices):
    NEW_YORK = 'America/New_York', 'America/New York'
    GUAYAQUIL = 'America/Guayaquil', 'America/Guayaquil'


def users_directory(instance, photo):
    return f'users/{instance.pk}/{photo}'


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    names = models.CharField(max_length=200)
    surnames = models.CharField(max_length=200)
    photo = models.ImageField(null=True, blank=True, upload_to=users_directory)
    date_joined = models.DateTimeField(auto_now_add=True)
    timezone = models.CharField(
        _('Time Zone'),
        max_length=32,
        choices=TimezoneChoices.choices,
        default=settings.TIME_ZONE
    )
    active = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return f'{self.names} {self.surnames}'


class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.DO_NOTHING,
        related_name='attendances'
    )
    date = models.DateField(auto_now_add=True)
    clock_in_at = models.TimeField()
    lunch_in_at = models.TimeField(null=True, blank=True)
    lunch_out_at = models.TimeField(null=True, blank=True)
    clock_out_at = models.TimeField(null=True, blank=True)
    permission_in_at = models.TimeField(null=True, blank=True)
    permission_out_at = models.TimeField(null=True, blank=True)
    overtime = models.DurationField(null=True, blank=True)
    approved = models.BooleanField(default=False, null=True, blank=True)
    hours = models.DurationField(null=True, blank=True)

    @property
    def worked_hours(self):
        if self.clock_in_at and self.clock_out_at:
            if self.lunch_in_at and self.lunch_out_at:
                pre_lunch = datetime.combine(date.today(), self.lunch_in_at) - datetime.combine(date.today(), self.clock_in_at)
                post_lunch = datetime.combine(date.today(), self.clock_out_at) - datetime.combine(date.today(), self.lunch_out_at)
                return pre_lunch + post_lunch
            return datetime.combine(date.today(), self.clock_out_at) - datetime.combine(date.today(), self.clock_in_at)
        return None

    @property
    def permission_hours(self):
        if self.permission_in_at and self.permission_out_at:
            return datetime.combine(date.today(), self.permission_in_at) - datetime.combine(date.today(), self.permission_out_at)
        return None

    @property
    def overtime_hours(self):
        worked = self.worked_hours
        if worked and worked > timedelta(hours=8):
            return worked - timedelta(hours=8)
        return timedelta(0)

    def __str__(self):
        return f'{self.employee.names}-{self.id}/{self.date}'