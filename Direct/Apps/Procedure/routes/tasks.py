from django.contrib.auth.decorators import login_required
from django.urls import path

from ..views import TaskView

urlpatterns = [
    path('add/<int:project_id>', login_required(TaskView.as_view(action='Add'), login_url='Procedure:login'), name='add_task'),
    path('add/', login_required(TaskView.as_view(action='Add'), login_url='Procedure:login'), name='add_task'),
    path('project/<int:project_id>', login_required(TaskView.as_view(action='Project'), login_url='Procedure:login'), name='list_tasks'),
    path('list/', login_required(TaskView.as_view(action='List', template='Procedure/Tasks/list.html'), login_url='Procedure:login'), name='list_tasks'),
    path('list/<int:is_calendar>', login_required(TaskView.as_view(action='List', template='Procedure/Tasks/list.html'), login_url='Procedure:login'), name='list_tasks'),
    path('completed/<int:task_id>', login_required(TaskView.as_view(action='is-completed'), login_url='Procedure:login'), name='is-completed'),
    path('archive/<int:is_calendar>', login_required(TaskView.as_view(action='archive-task'), login_url='Procedure:login'), name='delete-task'),
    path('details/<int:task_id>', login_required(TaskView.as_view(action='Details', template='Procedure/Tasks/details.html'), login_url='Procedure:login'), name='details')
]