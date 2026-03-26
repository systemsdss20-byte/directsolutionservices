from datetime import datetime, timedelta

from pytz import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.views.generic import View
from ..helpers.message import MessageResponse
from .forms import EmployeeForm, AttendanceForm
from .models import Employee, Attendance
from ..Procedure.models import User


class IndexView(View):
    template_name = 'Attendance/create.html'

    @login_required(login_url='Procedure:login')
    def get(self, request, *args, **kwargs):
        form = EmployeeForm()
        users = User.objects.all().only("id", "fullname", "avatar")
        employees = Employee.objects.all()
        form2 = AttendanceForm()
        context = {
            'employees': employees,
            'form': form, 'form2': form2,
            'users': users
        }
        return render(request, 'Attendance/Employee/list.html', context)


class EmployeeList(View):
    template_name = 'Attendance/Employee/list.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})


class EmployeeCreate(View):
    template_name = 'Attendance/Employee/create.html'

    def get(self, request, *args, **kwargs):
        form = EmployeeForm()
        users = User.objects.filter(is_active=True).only("id", "fullname", "avatar")
        users_json = list()
        for user in users:
            employee = Employee.objects.filter(user=user).only('id')
            if len(employee) == 0:
                users_json.append({"id": user.id, "fullname": user.fullname, "avatar": user.avatar})
        context = {
            'form': form,
            'users': users_json
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                photo = form.cleaned_data['photo']
                employee = form.save(commit=False)
                if photo is None:
                    photo = form.cleaned_data['user'].avatar
                    employee.photo = photo
                employee.save()
                response = JsonResponse({'description': 'Save success', 'type': 'success'})
                return HttpResponse(response, content_type='application/json', status=200)
            except Exception as e:
                print(e)
                response = JsonResponse({'description': '{}'.format(e), 'type': 'error'})
                return HttpResponse(response, content_type='application/json', status=500)
        else:
            errors = form.errors.as_json(escape_html=False)
            print(errors)
            return HttpResponse(JsonResponse({'description': 'Check if filled fields', 'type': 'warning'}),
                                content_type='application/json', status=500)


class EmployeeUpdate(View):
    template_name = 'Attendance/Employee/update.html'

    def get(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, pk=kwargs['pk'])
        form = EmployeeForm(instance=employee)
        context = {'form': form, 'employee': employee}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, pk=kwargs['pk'])
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            try:
                photo = form.cleaned_data['photo']
                employee = form.save(commit=False)
                if photo is None:
                    photo = form.cleaned_data['user'].avatar
                    employee.photo = photo
                employee.save()
                response = JsonResponse({'description': 'Save success', 'type': 'success'})
                return HttpResponse(response, content_type='application/json', status=200)
            except Exception as e:
                print(e)
                response = JsonResponse({'description': '{}'.format(e), 'type': 'error'})
                return HttpResponse(response, content_type='application/json', status=500)
        else:
            errors = form.errors.as_json(escape_html=False)
            print(errors)
            return HttpResponse(JsonResponse({'description': 'Check if filled fields', 'type': 'warning'}),
                                content_type='application/json', status=500)


class EmployeeDelete(View):
    def post(self, request):
        id = int(request.POST.get('id'))
        if id:
            try:
                Employee.objects.filter(pk=id).update(active=False)
                return HttpResponse(JsonResponse({'description': 'Employee deleted'}), content_type='application/json',
                                    status=200)
            except Exception as e:
                return HttpResponse(JsonResponse({'description': 'Error %s' % e}), content_type='application/json',
                                    status=500)


def getUser(request, id):
    if request.method == 'GET':
        user = User.objects.only('last_name', 'first_name', 'avatar').get(pk=id)
        return JsonResponse({'last_name': user.last_name, 'first_name': user.first_name, 'photo': str(user.avatar)})


def formatTime(hours, to_string=False, is_string=False):
    if to_string:
        return hours.strftime('%H:%M:%S')
    if is_string:
        return datetime.strptime(hours, '%H:%M:%S')
    return datetime.strptime(hours.strftime('%H:%M:%S'), '%H:%M:%S')


def verifyStatusAttendance(request):
    try:
        if request.method == 'GET':
            employee = Employee.objects.get(user=request.user)
            # Current time in UTC
            now_utc = datetime.now(timezone('UTC'))
            # Convert to employee time zone
            now_office = now_utc.astimezone(timezone(employee.timezone))
            attendance = Attendance.objects.filter(date=now_office.today(), employee=employee)
            if attendance:
                current = attendance[0]
                # Show Lunch-In
                if current.lunch_in_at is None and current.clock_out_at is None:
                    data = {'register_event': 'Lunch-In', 'last_event': 'Clock-In', 'recorded_time': formatTime(current.clock_in_at, True), 'class_name': 'checkout'}
                # Show Lunch-Out (after valid lunch in)
                elif current.lunch_out_at is None and current.clock_out_at is None and current.lunch_in_at is not None:
                    data = {'register_event': 'Lunch-Out', 'last_event': 'Lunch-In', 'recorded_time': formatTime(current.lunch_in_at, True), 'class_name': 'checkin'}
                # Show Permission-Out allowed after lunch-out and before clock-out
                elif current.permission_out_at is None and current.clock_out_at is None and current.lunch_out_at is not None:
                    data = {'register_event': 'Permission-Out', 'last_event': 'Lunch-Out', 'recorded_time': formatTime(current.lunch_out_at, True), 'class_name': 'warning'}
                # Show Permission-In when permission has been recorded
                elif current.permission_out_at is not None and current.permission_in_at is None and current.clock_out_at is None:
                    data = {'register_event': 'Permission-In', 'last_event': 'Permission-Out', 'recorded_time': formatTime(current.permission_out_at, True), 'class_name': 'checkin'}
                # Show Clock-Out after lunch / permission completed or skipped
                elif current.clock_out_at is None and current.clock_in_at is not None:
                    if current.permission_out_at and current.permission_in_at is None:
                        data = {'msg_attendance': 'Please finish permission before clock-out'}
                        return data
                    data = {'register_event': 'Clock-Out', 'last_event': 'Lunch-Out', 'recorded_time': formatTime(current.lunch_out_at, True) if current.lunch_out_at else formatTime(current.clock_in_at, True), 'class_name': 'checkout'}
                else:
                    request.session['msg_attendance'] = '%s Hours Worked' % attendance[0].clock_out_at
                    request.session['register_event'] = 'Clock-In'
                    request.session['last_event'] = 'Clock-Out'
                    request.session['class_name'] = 'checkin'
                    return {'msg_attendance': 'All events are already registered'}
                weekday = datetime.today().strftime('%A')
                if weekday == 'Saturday':
                    if data['register_event'] == 'Lunch-In':
                        data['register_event'] = 'Clock-Out'
                request.session['register_event'] = data['register_event']
                request.session['last_event'] = data['last_event']
                request.session['recorded_time'] = data['recorded_time']
                request.session['class_name'] = data['class_name']
                if attendance[0].clock_out_at is None and attendance[0].lunch_out_at:
                    clock_in = formatTime(attendance[0].clock_in_at)
                    lunch_out = formatTime(attendance[0].lunch_out_at)
                    lunch_in = formatTime(attendance[0].lunch_in_at)
                    current_time = formatTime(now_office.time())
                    current_hours = lunch_in - clock_in
                    missing_hours = formatTime("08:00:00", is_string=True) - current_hours
                    add_hour = timedelta(hours=missing_hours.hour, minutes=missing_hours.minute, seconds=missing_hours.second)
                    complete_hours = lunch_out + add_hour
                    request.session['msg_attendance'] = "You complete 8 hours at %s" % complete_hours.time()
                    data["workedhours"] = abs(lunch_out - current_time) + current_hours
                else:
                    request.session['msg_attendance'] = "%s at %s"% (data['last_event'], data['recorded_time'])
                return data
            else:
                #Show Clock-In
                data = {'register_event': 'Clock-In', 'class_name': 'checkin'}
                request.session['register_event'] = data['register_event']
                request.session['class_name'] = data['class_name']
                request.session['recorded_time'] = ''
                request.session['msg_attendance'] = 'Please clock-in'
                return data
    except Exception as e:
        print(f'AttendanceControl Error: {e}')
        pass


class AttendanceControl(View):

    def get(self, request, *args, **kwargs):
        status_attendance = verifyStatusAttendance(request)
        if status_attendance.get('msg_attendance') is not None:
            return HttpResponse("<script>notification(' "+status_attendance['msg_attendance']+"', 'error');</script>")
        else:
            return render(request, 'Attendance/AttendanceControl/attendance_modal.html', status_attendance)

    def post(self, request, *args, **kwargs):
        employee = Employee.objects.get(user=request.user)
        registered_event = str(request.POST.get('register_event'))
        try:
            # Current time in UTC
            now_utc = datetime.now(timezone('UTC'))
            # Convert to employee time zone
            now_office = now_utc.astimezone(timezone(employee.timezone))
            check_attendance = Attendance.objects.filter(date=now_office.today(), employee=employee).count()
            last_event = ''
            register_event = ''
            class_name = ''
            recorded_time = ''
            text_label = ''
            additional_information = ''
            safe = False
            if registered_event == 'Clock-In':
                if check_attendance == 0:
                    attendance = Attendance()
                    attendance.employee = employee
                    attendance.clock_in_at = formatTime(now_office.time(), to_string=True)
                    attendance.save()
                    weekday = now_office.today().strftime('%A')
                    last_event = 'Clock-In'
                    register_event = 'Lunch-In' if weekday != 'Thursday' else 'Clock-Out'
                    class_name = 'checkout'
                    recorded_time = attendance.clock_in_at
                    text_label = 'Clock-In at %s' % recorded_time
                else:
                    return JsonResponse({'save': False, 'error': "This event has already been registered"})
            elif check_attendance:
                attendance = Attendance.objects.get(date=now_office.today(), employee=employee)
                if registered_event == 'Lunch-In' and attendance.lunch_in_at is None:
                    if attendance.clock_in_at is not None:
                        if attendance.clock_out_at is None:
                            attendance.lunch_in_at = formatTime(now_office.time(), to_string=True)
                            first_hour = formatTime(attendance.clock_in_at)
                            second_hour = formatTime(now_office.time())
                            hours_worked = abs(second_hour-first_hour)
                            attendance.hours = hours_worked
                            attendance.save()
                            last_event = 'Lunch-In'
                            register_event = 'Lunch-Out'
                            class_name = 'checkin'
                            recorded_time = attendance.lunch_in_at
                            text_label = 'Lunch-In at %s' % recorded_time
                            additional_information = '%s Hours Worked' % hours_worked
                            safe = True
                        else:
                            return JsonResponse({'save': safe, 'error': "Your lunch time cannot be register because your clock-out is registered"})
                    else:
                        return JsonResponse({'save': safe, 'error': "Your check-in is not register"})
                elif registered_event == 'Lunch-Out' and attendance.lunch_out_at is None:
                    if attendance.clock_in_at is not None:
                        if attendance.lunch_in_at is not None:
                            if attendance.clock_out_at is None:
                                attendance.lunch_out_at = formatTime(now_office.time(), to_string=True)
                                lunch_in = formatTime(attendance.lunch_in_at)
                                validate_lunch = abs(formatTime(attendance.lunch_out_at, is_string=True) - lunch_in)
                                #if validate_lunch > timedelta(minutes=55):
                                if validate_lunch > timedelta(minutes=30):
                                    recorded_time = attendance.lunch_out_at
                                    if timedelta(minutes=55) < validate_lunch < timedelta(minutes=59):
                                        attendance.lunch_out_at = lunch_in + timedelta(hours=1)
                                        recorded_time = formatTime(attendance.lunch_out_at, to_string=True)
                                    attendance.save()
                                    last_event = 'Lunch-Out'
                                    register_event = 'Clock-Out'
                                    class_name = 'checkout'
                                    text_label = 'Lunch-Out at %s' % recorded_time
                                    safe = True
                                else:
                                    return JsonResponse({'save':safe, 'error': 'Your lunch time is {0}  minutes, you have to complete 1 hour or 30 minutes'.format(validate_lunch)})
                            else:
                                return JsonResponse({'save': safe, 'error': "Your lunch time cannot be register because your check-out is registered"})
                        else:
                            return JsonResponse({'save': safe,
                                                 'error': "You did not record the end time of your lunch"})
                    else:
                        return JsonResponse({'save': safe,
                                             'error': "Your check-in time is not recorded"})
                elif registered_event == 'Permission-Out' and attendance.permission_out_at is None:
                    if attendance.clock_out_at is None:
                        attendance.permission_out_at = formatTime(now_office.time(), to_string=True)
                        attendance.save()
                        last_event = 'Permission-Out'
                        register_event = 'Permission-In'
                        class_name = 'checkin'
                        recorded_time = attendance.permission_out_at
                        text_label = 'Permission-Out at %s' % recorded_time
                        safe = True
                    else:
                        return JsonResponse({'save': safe, 'error': 'Your clock-out is already registered'})
                elif registered_event == 'Permission-In' and attendance.permission_out_at is not None and attendance.permission_in_at is None:
                    if attendance.clock_out_at is None:
                        attendance.permission_in_at = formatTime(now_office.time(), to_string=True)
                        attendance.save()
                        last_event = 'Permission-In'
                        register_event = 'Clock-Out'
                        class_name = 'checkout'
                        recorded_time = attendance.permission_in_at
                        text_label = 'Permission-In at %s' % recorded_time
                        permission_duration = attendance.permission_hours
                        if permission_duration is not None:
                            additional_information = 'Permission Hours: %s' % permission_duration
                        safe = True
                    else:
                        return JsonResponse({'save': safe, 'error': 'Your clock-out is already registered'})
                elif registered_event == 'Clock-Out' and attendance.clock_out_at is None:
                    if attendance.clock_in_at is not None:
                        if attendance.permission_out_at and attendance.permission_in_at is None:
                            return JsonResponse({'save': False, 'error': 'Please complete permission return before clock-out'})
                        attendance.clock_out_at = formatTime(now_office.time(), to_string=True)
                        if attendance.lunch_in_at is not None:
                            if attendance.lunch_out_at is not None:
                                hours_worked = abs(formatTime(attendance.lunch_in_at) - formatTime(attendance.clock_in_at))
                                first_hour = formatTime(attendance.lunch_out_at)
                                second_hour = formatTime(attendance.clock_out_at, is_string=True)
                                hours_worked = abs(second_hour - first_hour) + hours_worked
                            else:
                                return JsonResponse({'save': safe, 'error': 'Your lunch end time is not registered'})
                        else:
                            first_hour = formatTime(attendance.clock_in_at)
                            second_hour = formatTime(attendance.clock_out_at, is_string=True)
                            hours_worked = abs(second_hour - first_hour)
                        attendance.hours = hours_worked
                        attendance.overtime = attendance.overtime_hours
                        if attendance.overtime > timedelta(seconds=0):
                            attendance.approved = False
                        attendance.save()
                        last_event = 'Clock-Out'
                        register_event = 'Clock-In'
                        class_name = 'checkin'
                        recorded_time = attendance.clock_out_at
                        text_label = 'Clock-Out at %s' % str(recorded_time)
                        additional_information = '%s Hours Worked' % str(hours_worked)
                        if attendance.permission_hours:
                            additional_information += ' | Permission %s' % str(attendance.permission_hours)
                        if attendance.overtime and attendance.overtime > timedelta(seconds=0):
                            additional_information += ' | Overtime %s' % str(attendance.overtime)
                        safe = True
                    else:
                        return JsonResponse({'save': safe, 'error': "Your check-in time is not recorded"})
                else:
                    return JsonResponse({'save': safe, 'error': 'This event has already been registered'})
            else:
                return JsonResponse({'save': safe, 'error': 'You have not register clock-in'})
            request.session['last_event'] = last_event
            request.session['register_event'] = register_event
            request.session['class_name'] = class_name
            request.session['recorded_time'] = recorded_time

            return JsonResponse({
                'save': True, 'text_label': text_label, 'class_name': class_name,
                'register_event': register_event, 'additional_information': additional_information, 'last_event': last_event
            })
        except Exception as e:
            print('Error saveAttendance', e)
            return JsonResponse({'save': False, 'error': '%s' % e})


class AttendanceControlList(LoginRequiredMixin, View):
    template_name = 'Attendance/AttendanceControl/list.html'
    permission_required = 'attendanceapp.view_attendance'
    login_url = 'Procedure:login'
    # raise_exception = False
  
    
    def get(self, request, *args, **kwargs):
        if kwargs.get('pk', None) is not None:
            attendance = Attendance.objects.get(id=kwargs.get('pk'))
            form = AttendanceForm(instance=attendance)
            return render(request, 'Attendance/AttendanceControl/update.html', {'form': form, 'id': kwargs.get('pk')})
        employees = Employee.objects.filter(active=True).values('id', 'surnames', 'names')
        return render(request, self.template_name, {'employees': employees})
    
    def post(self, request, *args, **kwargs):
        try:
            permission = request.user.has_perm('attendanceapp.change_attendance')
            if not permission:
                return MessageResponse(description='You do not have permission to edit attendance records').error()
            
            form = AttendanceForm(request.POST)
            if form.is_valid():
                form_date = request.POST.get('attendance_date')
                form.cleaned_data['date'] = datetime.strptime(form_date, '%m/%d/%Y').date()
                Attendance.objects.filter(id=kwargs.get('pk')).update(
                    date=form.cleaned_data['date'],
                    clock_in_at=form.cleaned_data['clock_in_at'],
                    lunch_in_at=form.cleaned_data['lunch_in_at'],
                    lunch_out_at=form.cleaned_data['lunch_out_at'],
                    clock_out_at=form.cleaned_data['clock_out_at'],
                    hours=form.cleaned_data['hours'],
                )
                return MessageResponse(description='Save success').success()
            else:
                return MessageResponse(data={'fields': form.errors}, description='Validation').warning()    
        except ValueError as e:
            print(e)
            return MessageResponse(description='An error occurred: {}'.format(e)).error()