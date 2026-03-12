from rest_framework.authtoken import views
from django.urls import path
from .views import customers_list, units_list, created_recive

urlpatterns = [
    path('customers/<int:pk>/', customers_list, name='customers-list'),
    path('units/<int:customer_id>/', units_list, name='units-list'),
    path('receipt/', created_recive, name='recive-list'),
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
]