from django.db import models
from simple_history.models import HistoricalRecords
from ..Procedure.models import Services, Invoice_det
from ..Attendanceapp.models import Employee

# Create your models here.
class Commission_Value(models.Model):
    commission_value  = models.DecimalField(max_digits=5, decimal_places=2)
    service = models.OneToOneField(Services, on_delete=models.DO_NOTHING)
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.employee is None:
            return self.service.description + " - $" + str(self.commission_value)
        else:
            return self.service.description + " - $" + str(self.commission_value) + " - " + self.employee.names
    
class Commission(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'PENDING'),
        ('PAID', 'PAID'),
        ('REJECTED', 'REJECTED')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    payment_datetime = models.DateTimeField(null=True, blank=True)
    details = models.ForeignKey(Invoice_det, on_delete=models.DO_NOTHING)
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=True, blank=True)
    amount_commission = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    history = HistoricalRecords()