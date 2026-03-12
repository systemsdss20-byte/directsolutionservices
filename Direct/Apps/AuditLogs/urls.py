from django.contrib.auth.decorators import permission_required, login_required
from django.urls import path

from .views import IndexView, CustomerAuditLogView, CardsAuditLogView, UnitAuditLogView, DriversAuditLogView
from .tables_views import CustomerAuditLogDataView, CardsAuditLogDataView, UnitAuditLogDataView, DriversAuditLogDataView
app_name = 'AuditLogs'

urlpatterns = [
    path('', login_required(IndexView.as_view(), login_url='Procedure:login'), name='index'),
    path('customers_audit_log/', login_required(CustomerAuditLogView.as_view(), login_url='Procedure:login'), name='customer'),
    path('cutomer_table_audit/', login_required(CustomerAuditLogDataView.as_view(), login_url='Procedure:login'), name='customer_audit_log'),
    path('cards_audit_log/', login_required(CardsAuditLogView.as_view(), login_url='Procedure:login'), name='cards'),
    path('cards_table_audit/', login_required(CardsAuditLogDataView.as_view(), login_url='Procedure:login'), name='cards_audit_log'),
    path('drivers_audit_log/', login_required(DriversAuditLogView.as_view(), login_url='Procedure:login'), name='drivers'),
    path('drivers_table_audit/', login_required(DriversAuditLogDataView.as_view(), login_url='Procedure:login'), name='drivers_audit_log'),
    path('unit_audit_log/', login_required(UnitAuditLogView.as_view(), login_url='Procedure:login'), name='unit'),
    path('unit_table_audit/', login_required(UnitAuditLogDataView.as_view(), login_url='Procedure:login'), name='unit_audit_log'),
]