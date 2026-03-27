from django.db import models
from simple_history.models import HistoricalRecords
from ..Procedure.models import User, Customers, Drivers, Exams


# Create your models here.
class RandomList(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    current_drivers = models.IntegerField()
    year = models.IntegerField()
    quarter = models.IntegerField()
    drug_testing_rate = models.DecimalField(max_digits=6, decimal_places=2)
    alcohol_testing_rate = models.DecimalField(max_digits=6,decimal_places=2)
    show = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()


class Detail_RandomList(models.Model):
    random_list = models.ForeignKey(RandomList, models.CASCADE)
    customer = models.ForeignKey(Customers, models.DO_NOTHING)
    driver = models.ForeignKey(Drivers, models.DO_NOTHING, null=True, blank=True)
    updated_by = models.ForeignKey(User, models.DO_NOTHING, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    test_substances = models.BooleanField(default=False)
    test_alcohol = models.BooleanField(default=False)
    # test_file = models.TextField(max_length=40, null=True, blank=True)
    test_file = models.OneToOneField(Exams, models.DO_NOTHING, null=True, blank=True)
    status = models.CharField(max_length=40, null=True, blank=True)
    history = HistoricalRecords()


class Comments(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    updated_at = models.DateTimeField(null=True, blank=True)
    detail_random_list = models.ForeignKey(Detail_RandomList, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()
