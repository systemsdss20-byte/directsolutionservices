from django.contrib import admin
from django import forms
from .models import Commission_Value
from ..Attendanceapp.models import Employee

#Register your models here.
#admin.site.unregister(Commission_Value)    
# class CommissionValueAdmin(admin.ModelAdmin):
#     list_display = ('service', 'commission_value', 'employee', 'is_active')
#     form = CommissionValueForm
#     add_form = CommissionValueForm
    
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('names', 'surnames', 'user')
    search_fields = ['names', 'surnames']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(active=True)
    
class CommissionValueAdmin(admin.ModelAdmin):
    list_display = ('service', 'commission_value', 'employee', 'is_active')
    autocomplete_fields = ['service', 'employee']

admin.site.register(Employee, EmployeeAdmin)    
admin.site.register(Commission_Value, CommissionValueAdmin)