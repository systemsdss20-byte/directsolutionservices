from django.urls import path
from .views import customers_page, CustomersAjaxDatatableView, customers_export

urlpatterns = [
    path('customers/', customers_page, name='customers_page'),
    path('customers/data/', CustomersAjaxDatatableView.as_view(), name='customers_data'),
    path('customers/export/', customers_export, name='customers_export'),
]
