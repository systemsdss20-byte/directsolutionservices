from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import RandomListView, consortium 
from .tableViews import DetailListRandomTable

urlpatterns = [
    path('', consortium, name='consortium'),
    path('list/', login_required(RandomListView.as_view(), login_url='Procedure:login'), name='list'),
    path('list/<int:table>/', login_required(RandomListView.as_view(), login_url='Procedure:login'), name='list'),
    path('datatable/', login_required(DetailListRandomTable.as_view(), login_url='Procedure:login'), name='table'),
    path('newlist/', login_required(RandomListView.as_view(), login_url='Procedure:login'), name='index'),
]
