from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
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
    history = HistoricalRecords()
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
    hours = models.DurationField(null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.employee.names}-{self.id}/{self.date}'