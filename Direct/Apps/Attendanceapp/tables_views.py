import datetime

from ajax_datatable import AjaxDatatableView
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from ..helpers.utils import normalize_date

from .models import Employee, Attendance


class EmployeeDataView(AjaxDatatableView):
    model = Employee
    code = 'Employee'
    initial_order = [['names', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'

    column_defs = [
        {'name': 'pk', 'visible': False, 'searchable': False },
        {'name': 'photo', 'visible': True, 'searchable': False},
        {'name': 'names', 'visible': True, },
        {'name': 'surnames', 'visible': True},
        {'name': 'date_joined', 'visible': True},
        {'name': 'active', 'visible': True, 'searchable': False, 'autofilter': True},
        {'name': 'edit', 'title': 'Edit', 'searchable': False, 'orderable': False, },
        {'name': 'delete', 'title': 'Delete', 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
        row['photo'] = "<span class='avatar' style='background-image:url(/media/%s)'></span>"%(str(obj.photo))
        row['active'] = "<span class='badge bg-%s'>%s</span>" % ('success' if obj.active else 'danger', 'Active' if obj.active else 'Inactive')
        row['edit'] = "<a href='#' class='btn btn-info btn-sm edit' onclick='update(%s);'><i class='fas fa-pencil-alt'></i>&nbspEdit</a>" %obj.id
        row['delete'] = "<button type='button' class='btn btn-danger btn-sm' onclick='delete_modal(%s, \"%s\");'><i class='fas fa-trash'></i>&nbspDelete</button>" %(obj.id, obj.names + " "+ obj.surnames)


class AttendanceDataView(AjaxDatatableView):
    model = Attendance
    code = 'Attendance'
    initial_order = [['date', 'desc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    latest_by = 'date'
    show_date_filters = False
    column_defs = []
    permits = {}
    
    def get_column_defs(self, request):
        content_type = ContentType.objects.get_for_model(Attendance)
        Permission.objects.get_or_create(codename='edit_field_attendance', name='Edit Field', content_type=content_type)
        self.permits = {
            'edit': request.user.has_perm('attendanceapp.edit_field_attendance'),
        }
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'pk', 'visible': False, 'searchable': False },
            {'name': 'photo', 'title': 'Employees', 'searchable': False, 'orderable': False, },
            {'name': 'names', 'foreign_field': 'employee__names'},
            {'name': 'surnames', 'foreign_field': 'employee__surnames'},
            {'name': 'date', 'visible': True, 'searchable': True},
            {'name': 'clock_in_at', 'visible': True, 'searchable': False},
            {'name': 'lunch_in_at', 'visible': True, 'searchable': False},
            {'name': 'lunch_out_at', 'visible': True, 'searchable': False},
            {'name': 'clock_out_at', 'visible': True, 'searchable': False},
            {'name': 'hours', 'title': 'Hours Worked', 'searchable': False},
            {
                'name': 'edit', 'title': 'Edit', 'searchable': False, 
                'orderable': False, 'visible': False if not self.permits['edit'] else True, 
            },
        ]
        return  self.column_defs

    def customize_row(self, row, obj):
        row['photo'] = "<span class='avatar' style='background-image:url(/media/%s)'></span>" % (str(obj.employee.photo))
        
        if obj.hours:
            total_seconds = int(obj.hours.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            row['hours'] = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

        if self.permits['edit']:
            row['edit'] = "<a href='#' class='btn btn-info btn-sm edit' onclick='update(%s);'><i class='fas fa-pencil-alt'></i>&nbspEdit</a>" % obj.id

    def render_row_details(self, pk, request=None):
        attendance = self.model.objects.get(pk=pk)
        return render_to_string('Attendance/AttendanceControl/details.html', {'attendance': attendance})

    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        
        date_from_str = request.POST.get('date_from')
        date_to_str = request.POST.get('date_to')
        if date_from_str and date_to_str:
            try:
                date_from = normalize_date(date_from_str)
                date_to = normalize_date(date_to_str)
                return self.model.objects.filter(
                    date__gte=date_from, date__lte=date_to
                )
            except (ValueError, TypeError) as e:
                print(f"Error normalizing dates: {e}")
        today = datetime.date.today()
        queryset = self.model.objects.filter(
            date__month=today.month,
            date__year=today.year
        )
        return queryset