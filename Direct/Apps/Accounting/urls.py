from .views import DailyChartView, InvoiceDetailView, CommissionsView
from django.contrib.auth.decorators import login_required
from .tablesView import DailyChartTable, CommissionsTable
from django.urls import path

app_name = "accounting"

urlpatterns = [
    path("daily_chart/", DailyChartView.as_view(), name="daily_chart"),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('dailyChartTable/', DailyChartTable.as_view(), name='dailyChartTable'),
    path('commissions/', CommissionsView.as_view(), name='commissions'),
    path('commissions-list/', login_required(CommissionsTable.as_view(), login_url='Procedure:login'), name='commissions-list'),
]