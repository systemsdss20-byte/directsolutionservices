from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import  EmployeeList, EmployeeCreate, EmployeeUpdate, EmployeeDelete, getUser, AttendanceControl, verifyStatusAttendance, AttendanceControlList
from .tables_views import EmployeeDataView, AttendanceDataView
from .report_views import Attendance_Report
urlpatterns = [
    #path('', IndexView.as_view(), name='index'),
    path('employees/', login_required(EmployeeList.as_view(), login_url='Procedure:login'), name='employees' ),
    path('new-employee', login_required(EmployeeCreate.as_view(), login_url='Procedure:login'), name='new-employee' ),
    path('edit-employee/<int:pk>', login_required(EmployeeUpdate.as_view(), login_url='Procedure:login'), name='edit-employee'),
    path('delete-employee/', login_required(EmployeeDelete.as_view(), login_url='Procedure:login'), name='delete-employee'),
    path('getUser/<int:id>', login_required(getUser), name='getUser'),
    path('datatable_employees/', login_required(EmployeeDataView.as_view(), login_url='Procedure:login'), name='datatable_employees'),
    #path('control/', AttendanceControl.as_view(), name='entry_time'),
    #path('control/<str:control>', login_required(AttendanceControl.as_view(), login_url='Procedure:login'), name='entry_times'),
    path('control/', login_required(AttendanceControl.as_view(), login_url='Procedure:login')),
    path('attendance-control/', AttendanceControlList.as_view(), name='attendance-control'),
    path('attendance-control/<int:pk>', AttendanceControlList.as_view(), name='edit-attendance-control'),
    path('datatable-attendance-control/', login_required(AttendanceDataView.as_view(), login_url='Procedure:login'), name='datatable-attendance-control'),
    path('attendance-report/', login_required(Attendance_Report.as_view(), login_url='Procedure:login'), name='attendance-report')
]