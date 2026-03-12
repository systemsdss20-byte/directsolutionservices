import json
import shutil
from datetime import date, datetime, timedelta
import os
import openpyxl
import zipcodes
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Q, Value as V, CharField
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import View

from Direct.Apps.Procedure.email_views import SendCertificateRandomTestEmail
from ..Accounting.views import saveCommision, deleteCommission
from docxtpl import DocxTemplate

from .forms import Customers, CustomersForm, Units, UnitForm, InvoiceForm, InvoicesDetFormSet, PaidForm, \
    UpdatePaidFrm, MillagesForm, ReciveForm, DriverForm, ExamForm, NotesForm, CardsForm, UploadReceipts, \
    NotesProjectsForm, CategoryRoadTaxForm, CustomerFilesForm, TaskForm, ProjectsForm, FloridaTagTaxForm
# Create your views here.
from .models import User, Invoices, Services, Invoice_paid, Credits, Projects, Invoice_det, Millages, Recive, Drivers, \
    Exams, \
    Notes, Payable, Cards, States, NotesProjects, RandomTest, Road_Taxes, Customer_Files, News, Log_Invoice_cancel, \
    Task, Fl_Tag_Price_Month
from ..Attendanceapp.views import verifyStatusAttendance
from ..Calendar.models import Event
from ..helpers.message import MessageResponse
from ..helpers.utils import normalize_date
from ..helpers.update_dot import queryDOT
from ... import settings


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.change_password:
                return HttpResponseRedirect('/Procedure/change_password/')
            else:
                return HttpResponseRedirect("/Procedure/index/")
        else:
            messages.error(request, 'Wrong username or password')
            return render(request, 'login.html', {})
    elif request.user.is_authenticated:
        return HttpResponseRedirect("/Procedure/index/")
    else:
        return render(request, 'login.html', {})


@login_required(login_url='Procedure:login')
def user_logout(request):
    logout(request)
    return render(request, 'login.html', {'msj': 'true'})


@login_required(login_url='Procedure:login')
def index(request):
    summary = summary_projects(request)
    # if not request.session.has_key('last_event'):
    alertNotifications(request=request)
    verifyStatusAttendance(request)
    return render(request, 'Procedure/index.html', {'summary': summary, 'today': date.today().strftime('%Y/%m/%d')})

def handler404(request, exception):
    return render(request, 'error-404.html', status=404)

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

@login_required(login_url='Procedure:login')
def alertNotifications(request):
    today = datetime.now().date()
    # Calcula la fecha de un día antes
    filter_tomorrow = today + timedelta(days=2)
    filter_today = today + timedelta(days=1)
    appointments_tomorrow = Event.objects.filter(Q(user=request.user) | Q(public=True),
                                                 start_time__range=[filter_today, filter_tomorrow],
                                                 is_deleted=False).count()
    appointments_today = Event.objects.filter(Q(user=request.user) | Q(public=True),
                                              Q(start_time__range=[today, filter_today]) | Q(
                                                  end_time__range=[today, filter_today]), is_deleted=False).count()
    total_tasks = TaskView.user_tasks(request).count()
    total_notifications = appointments_tomorrow + appointments_today + total_tasks
    # Creamos las variables de session
    request.session['total_tasks'] = total_tasks
    request.session['appointments_today'] = appointments_today
    request.session['appointments_tomorrow'] = appointments_tomorrow
    request.session['total_notifications'] = total_notifications
    if request.method == 'GET':
        return JsonResponse({
            'total_tasks': total_tasks, 
            'appointments_today': appointments_today, 
            'appointments_tomorrow': appointments_tomorrow,
            'total_notifications': total_notifications
        })


def summary_projects(request, reload=0):
    today = date.today()
    projects = get_projects_by_user(request)
    open_projects = projects.filter(status='Opened', invoice__paid_date__isnull=False)
    # in_process_projects = projects.filter(status='In Process', iduserlast=request.user)
    in_process_projects = projects.filter(
        Q(status='In Process', iduserlast=request.user) | Q(service_name__contains='FUEL TAXES', status='In Process'))
    date_open_projects = open_projects[0].request if open_projects else ''
    date_inprocess = in_process_projects[0].request if in_process_projects else ''
    new_projects = projects.filter(invoice__paid_date=today, invoice__deu=0, status='Opened', invoice__deleted=False)
    invoices_unpaid = Invoices.objects.filter(deleted=False, status='Unpaid')
    num_unpaid_invoices = invoices_unpaid.count()
    since_invoice_unpaid = invoices_unpaid[0].invdate
    if request.method == 'POST' and reload:
        return JsonResponse(
            {
                'open_projects': open_projects.count(),
                'date_open': date_open_projects.strftime("%b %d, %Y") if date_open_projects else '',
                'date_inprocess': date_inprocess.strftime("%b %d, %Y") if date_inprocess else '',
                'inprocess_project': in_process_projects.count(), 'new_projects': new_projects.count(),
                'invoice_date': since_invoice_unpaid, 'num_invoices': num_unpaid_invoices
            }
        )
    return {'open_projects': open_projects.count(),
            'date_open': date_open_projects.strftime("%b %d, %Y") if date_open_projects else '',
            'date_inprocess': date_inprocess.strftime("%b %d, %Y") if date_inprocess else '',
            'inprocess_project': in_process_projects.count(), 'new_projects': new_projects.count(),
            'invoice_date': since_invoice_unpaid, 'num_invoices': num_unpaid_invoices}


def get_projects_by_user(request):
    groups = request.user.groups.all()
    projects = Projects.objects.filter(
        Q(deleted=False, idcustomer__clientstatus='Active') | Q(iduser=request.user, deleted=False,
                                                                idcustomer__clientstatus='Active',
                                                                invoice__status='Unpaid'))
    projects = projects.filter(service__group__in=groups)
    return projects


class ProjectsView(View):
    action = ''

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            if self.action == 'Add':
                return self.add_project(request, *args, **kwargs)
        else:
            return super().dispatch(*args, **kwargs)

    def add_project(self, request, *args, **kwargs):
        form = ProjectsForm(request.POST)
        if form.is_valid():
            try:
                service = Services.objects.get(idservice=form.cleaned_data['service'])
                today = date.today().strftime("%Y-%m-%d")
                project = Projects()
                project.idcustomer_id = form.cleaned_data['customer']
                project.service = service
                project.service_name = service.description
                project.quantity = form.cleaned_data['quantity']
                project.comments = form.cleaned_data['comment']
                project.request = today
                project.iduser = request.user
                project.statuslast = today
                project.iduserlast = request.user
                project.deleted = False
                project.status = 'In Process'
                project.save()
                summary = summary_projects(request)
                message = {'description': 'Added project', 'type': 'success'}
                return HttpResponse(
                    JsonResponse(
                        {
                            'message': message,
                            'open_projects': summary['open_projects'], 'date_open': summary["date_open"],
                            'date_inprocess': summary["date_inprocess"],
                            'inprocess_project': summary["inprocess_project"],
                            'new_projects': summary["new_projects"], 'invoice_unpaid': summary['num_invoices']
                        }
                    ),
                    content_type='application/json', status=200)
            except Exception as e:
                print(e)
                return HttpResponse(JsonResponse({'description': 'Internal Server error', 'type': 'error'}),
                                    content_type='application/json', status=500)
        else:
            errors = form.errors.as_json(escape_html=False)
            print(errors)
            result = JsonResponse({'errors': errors})
            return HttpResponse(result, content_type='application/json', status=500)


@login_required(login_url='Procedure:login')
def show_projects(request, status):
    today = date.today()
    projects = get_projects_by_user(request)
    if request.method == 'GET':
        summary = summary_projects(request)
        groups = request.user.groups.all()
        services = Services.objects.filter(group__in=groups, is_project=True, need_invoice=False)
        return render(request, 'Procedure/Projects/projects.html', {
            'status': status, 'summary': summary, 'form': ProjectsForm() if status == 'InProcess' else '',
            'services': services
        })
    if  request.method == 'POST':
        if status == 'Opened':
            projects = projects.filter(status='Opened', invoice__paid_date__isnull=False)

        if status == 'InProcess':
            # projects = projects.filter(status='In Process', iduserlast=request.user)
            projects = projects.filter(
                Q(status='In Process', iduserlast=request.user) | Q(service_name__contains='FUEL TAXES',
                                                                    status='In Process'))
        data = list()
        for json in projects:
            num_notes = NotesProjects.objects.filter(project=json).count()
            percentage = round((json.tasks_completed * 100) / json.tasks_number, 2) if json.tasks_number != 0 else 0
            cell_alert = False
            if json.idinvoicedet:
                cell_alert = True if (
                                                 today == json.request or today == json.idinvoicedet.idinvoice.paid_date) and status == 'Opened' else False
            data.append({
                'id': json.idproject,
                'customers': {'idcustomer': json.idcustomer_id, 'cusname': json.idcustomer.cusname},
                'quantity': json.quantity,
                'services': json.service_name, 'comments': json.comments,
                'representative': (json.iduser.first_name + " " + json.iduser.last_name),
                'invoice': json.idinvoicedet.idinvoice.status if json.invoice else 'No Invoice',
                'num_notes': num_notes,
                'request': json.request.strftime('%m/%d/%Y'), 'status': json.status,
                'userlast': (json.iduserlast.first_name + " " + json.iduserlast.last_name).upper(),
                'cell_alert': cell_alert, 'percentage': percentage
            })
        num = projects.count()
        return JsonResponse({'draw': 1, 'recordsTotal': num, 'recordsFiltered': num, 'data': data}, safe=False)


def details_project(request, project_id):
    if request.method == 'GET':
        project = Projects.objects.get(idproject=project_id)
        summary = summary_projects(request)
        project.tasks_number = project.tasks_number if project.tasks_number != 0 else 1
        percentage = round((project.tasks_completed * 100) / project.tasks_number, 2)
        notes = NotesProjects.objects.filter(project=project)
        tasks = Task.objects.filter(project=project, archived=False)
        return render(request, 'Procedure/Projects/details.html',
                      {'project': project, 'project_id': project_id, 'summary': summary, 'percentage': percentage, 'media': settings.MEDIA_URL,
                       'notes': notes, 'tasks': tasks})


def notes_projects(request, idproject, is_chat):
    if request.method == "GET":
        project = Projects.objects.get(idproject=idproject)
        customer = "%s - %s" % (project.idcustomer_id, project.idcustomer.cusname)
        notes = NotesProjects.objects.filter(project=project)
        template = 'Procedure/Projects/'
        template += 'notes_projects_chat.html' if is_chat else 'notes_projects.html'

        return render(request, template, {
            'notes': notes, 'idproject': idproject, 'customer': customer, 'services': project.service,
            'notedate': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'idcustomer': project.idcustomer_id,
            'media': settings.MEDIA_URL
        })
    if  request.method == 'POST':
        form = NotesProjectsForm(request.POST)
        if form.is_valid():
            try:
                notes = form.save()
                data = {
                    'comments': notes.comments, 'date_comment': notes.date_comment.strftime("%b %d, %Y, %H:%M:%S"),
                    'user': notes.iduser.fullname, 'avatar': str(notes.iduser.avatar)
                }
                result = JsonResponse({'data': data})
                return HttpResponse(result, content_type="application/json", status=200)
            except Exception as e:
                print(e)
                return HttpResponse({"errors": "Error while to save"}, content_type='application/json', status=500)
        else:
            errors = form.errors.as_json(escape_html=False)
            result = JsonResponse({'errors': errors})
            return HttpResponse(result, content_type='application/json', status=500)

def assign_project(request):
    content_type = ContentType.objects.get_for_model(Projects)
    Permission.objects.get_or_create(codename='assign_project', name='Assign Project', content_type=content_type)
    if request.method == 'GET':
        users = User.objects.filter(is_active=True).only('id', 'fullname').exclude(id=40)
        return render(request, 'Procedure/Projects/assign_project.html', {'users': users})
    if request.method == 'POST':
        try:
            data = request.POST
            projects = data.getlist('projects[]')
            Projects.objects.filter(idproject__in=projects).update(iduserlast=data.get('user'), status='In Process')
            return MessageResponse(description="Success assign").success()
        except ValueError as v:
            print(v)
            return MessageResponse(description="Internar Server Error").error()



def edit_notes_projects(request, idnote):
    if request.method == 'GET' :
        notes = NotesProjects.objects.only('comments').get(pk=idnote)
        return JsonResponse({'comment': notes.comments})
    if request.method == 'POST' :
        try:
            comment = request.POST.get('comment')
            note = NotesProjects.objects.only('comments').get(id=idnote)
            today = datetime.today()
            note.comments = comment
            note.date_update_comment = timezone.now()
            note.save()
            return HttpResponse(JsonResponse({'comment': comment, 'date_update': today.strftime('%b %d, %Y %H:%M')}),
                                content_type='application/json', status=200)
        except Exception as e:
            print(e)


@login_required(login_url='Procedure:login')
def change_password(request):
    user_find = get_object_or_404(User, pk=request.user.id)
    if user_find.change_password:
        if request.method == 'GET':
            return render(request, 'Users/change_password.html', {})
        if request.method == 'POST':
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                try:
                    form.save()
                    update_session_auth_hash(request, form.user)
                    User.objects.filter(pk=request.user.id).update(change_password=False)
                    return JsonResponse({'message': "Your password has been changed successfully!"})
                except Exception as e:
                    print(e)
                    result = JsonResponse({'errorsave': e})
                    return HttpResponse(result, content_type='application/json', status=500)
            else:
                print(form.errors.as_json(escape_html=False))
                errors = form.errors.as_json(escape_html=False)
                result = JsonResponse({'errors': errors})
                return HttpResponse(result, content_type='application/json', status=500)
    else:
        return HttpResponseRedirect("/Procedure/index/")


@login_required(login_url='Procedure:login')
def open_links(request):
    return render(request, 'Procedure/File/openlinks.html')


@login_required(login_url='Procedure:login')
def search_box(request):
    try:
        if request.method == 'POST':
            search_value = request.POST.get('value_search')
            customers = Customers.objects.only('idcustomer', 'cusname').annotate(
                search=Concat('idcustomer', V('-'), 'cusname', V(' ('), 'mobile1', V(' '), 'owner', V(' '), 'owner_surname',
                              V(')'), output_field=CharField())).filter(
                search__icontains=search_value)
            data = list()
            for customer in customers:
                data.append({'label': customer.search, 'id': customer.idcustomer})
            search_json = json.dumps(data)
            return HttpResponse(search_json, content_type='application/json', status=200)
    except Exception as e:
        print(e)
        return HttpResponse({"redirect": "login"}, content_type='application/json', status=403)


@login_required(login_url='Procedure:login')
@permission_required("Procedure.add_customers", login_url="Procedure:index")
def add_customers(request):
    if request.user.has_perm("Procedure.add_customers"):
        if request.POST:
            try:
                form = CustomersForm(request.POST)
                if form.is_valid():
                    form.save()
                    return MessageResponse(description="Successfully saved").success()
                else:
                    errors = form.errors
                    return MessageResponse(data={'fields': errors}, description='Validation').warning()
            except Exception as e:
                print(e)
                return MessageResponse(description='Internal Server error').error()

        elif request.method == "GET":
            form = CustomersForm()
            nxtidcustomer = Customers.objects.latest("idcustomer")
            return render(request, 'Procedure/Customers/customer.html',
                          {'form': form, 'idcustomer': (nxtidcustomer.idcustomer) + 1})
    else:
        return HttpResponse(
            "<script>$.notify({message: 'No tiene acceso a esa función',},{type: 'warning',offset:{x:330,y:220},"
            "});</script>")


@login_required(login_url='Procedure:login')
@permission_required("Procedure.list_customers", login_url="Procedure:index")
def list_customers(request):
    content_type = ContentType.objects.get_for_model(Customers)
    Permission.objects.get_or_create(
        codename='list_customers',
        name='List Customers',
        content_type=content_type,
    )
    customers = Customers.objects.all().order_by('-idcustomer')
    # customers = Customers.objects.all().filter(clientstatus='Active').order_by('-idcustomer')
    return render(request, "Procedure/Customers/customers.html", {'customers': customers})


@login_required(login_url='Procedure:login')
@permission_required("Procedure.view_customers", login_url="Procedure:index")
def view_customer(request, customer_id):
    customer = get_object_or_404(Customers, idcustomer=customer_id)
    if request.method == "GET":
        birthday = False
        if customer.explic:
            if date.today().month == customer.explic.month and date.today().day == customer.explic.day:
                birthday = True
        compare = datetime.strptime('0001-01-01', '%Y-%m-%d').strftime('%Y-%m-%d')
        customer.since = '01/01/0001' if customer.since is None or customer.since.strftime(
            '%Y-%m-%d') == compare else customer.since.strftime('%m/%d/%Y')
        customer.explic = '01/01/0001' if customer.explic is None or customer.explic.strftime(
            '%Y-%m-%d') == compare else customer.explic.strftime('%m/%d/%Y')
        customer.insuexpire = '01/01/0001' if customer.insuexpire is None or customer.insuexpire.strftime(
            '%Y-%m-%d') == compare else customer.insuexpire.strftime('%m/%d/%Y')
        customer.mcexp = '01/01/0001' if customer.mcexp is None or customer.mcexp.strftime(
            '%Y-%m-%d') == compare else customer.mcexp.strftime('%m/%d/%Y')
        customer.dotidexp = '01/01/0001' if customer.dotidexp is None or customer.dotidexp.strftime(
            '%Y-%m-%d') == compare else customer.dotidexp.strftime('%m/%d/%Y')
        customer.irpexp = '01/01/0001' if customer.irpexp is None or customer.irpexp.strftime(
            '%Y-%m-%d') == compare else customer.irpexp.strftime('%m/%d/%Y')
        customer.iftaexp = '01/01/0001' if customer.iftaexp is None or customer.iftaexp.strftime(
            '%Y-%m-%d') == compare else customer.iftaexp.strftime('%m/%d/%Y')
        customer.mnexp = '01/01/0001' if customer.mnexp is None or customer.mnexp.strftime(
            '%Y-%m-%d') == compare else customer.mnexp.strftime('%m/%d/%Y')
        customer.nyexp = '01/01/0001' if customer.nyexp is None or customer.nyexp.strftime(
            '%Y-%m-%d') == compare else customer.nyexp.strftime('%m/%d/%Y')
        customer.californiaexp = '01/01/0001' if customer.californiaexp is None or customer.californiaexp.strftime(
            '%Y-%m-%d') == compare else customer.californiaexp.strftime('%m/%d/%Y')
        customer.campcexp = '01/01/0001' if customer.campcexp is None or customer.campcexp.strftime(
            '%Y-%m-%d') == compare else customer.campcexp.strftime('%m/%d/%Y')
        customer.caexp = '01/01/0001' if customer.caexp is None or customer.caexp.strftime(
            '%Y-%m-%d') == compare else customer.caexp.strftime('%m/%d/%Y')
        customer.bitexp = '01/01/0001' if customer.bitexp is None or customer.bitexp.strftime(
            '%Y-%m-%d') == compare else customer.bitexp.strftime('%m/%d/%Y')
        customer.floridaexp = '01/01/0001' if customer.floridaexp is None or customer.floridaexp.strftime(
            '%Y-%m-%d') == compare else customer.floridaexp.strftime('%m/%d/%Y')
        customer.state_permits_exp = '01/01/0001' if customer.state_permits_exp is None or customer.state_permits_exp.strftime(
            '%Y-%m-%d') == compare else customer.state_permits_exp.strftime('%m/%d/%Y')
        customer.city_license_exp = '01/01/0001' if customer.city_license_exp is None or customer.city_license_exp.strftime(
            '%Y-%m-%d') == compare else customer.city_license_exp.strftime('%m/%d/%Y')
        customer.county_license_exp = '01/01/0001' if customer.county_license_exp is None or customer.county_license_exp.strftime(
            '%Y-%m-%d') == compare else customer.county_license_exp.strftime('%m/%d/%Y')
        customer.new_jersey_exp = '01/01/0001' if customer.new_jersey_exp is None or customer.new_jersey_exp.strftime(
            '%Y-%m-%d') == compare else customer.new_jersey_exp.strftime('%m/%d/%Y')
        customer.over_weight_exp = '01/01/0001' if customer.over_weight_exp is None or customer.over_weight_exp.strftime(
            '%Y-%m-%d') == compare else customer.over_weight_exp.strftime('%m/%d/%Y')
        customer.over_size_exp = '01/01/0001' if customer.over_size_exp is None or customer.over_size_exp.strftime(
            '%Y-%m-%d') == compare else customer.over_size_exp.strftime('%m/%d/%Y')
        customer.inner_bridge_exp = '01/01/0001' if customer.inner_bridge_exp is None or customer.inner_bridge_exp.strftime(
            '%Y-%m-%d') == compare else customer.inner_bridge_exp.strftime('%m/%d/%Y')
        customer.dot_biennal_update_date = '01/01/0001' if customer.dot_biennal_update_date is None or customer.dot_biennal_update_date.strftime(
            '%Y-%m-%d') == compare else customer.dot_biennal_update_date.strftime('%m/%d/%Y')
        customer.annual_inspection_truck_expiration = '01/01/0001' if customer.annual_inspection_truck_expiration is None or customer.annual_inspection_truck_expiration.strftime(
            '%Y-%m-%d') == compare else customer.annual_inspection_truck_expiration.strftime('%m/%d/%Y')
        customer.annual_inspection_trailer_expiration = '01/01/0001' if customer.annual_inspection_trailer_expiration is None or customer.annual_inspection_trailer_expiration.strftime(
            '%Y-%m-%d') == compare else customer.annual_inspection_trailer_expiration.strftime('%m/%d/%Y')
        customer.city = customer.city.upper() if customer.city else customer.city
        customer.county = customer.county.upper() if customer.county else customer.county
        customer.address = customer.address.upper() if customer.address else customer.address
        # user_login = request.user
        due = Invoices.objects.filter(idcustomer=customer_id).aggregate(due=Sum('deu'))
        form = CustomersForm(instance=customer)
        drivers = Drivers.objects.filter(idcustomer=customer_id, status='Active').only('iddriver', 'nombre',
                                                                                       'random_test')
        customer_notes = Notes.objects.filter(idcustomer=customer_id).filter(
            Q(pin_up=True) | Q(date_expiry__gte=datetime.today().strftime('%Y-%m-%d'))).order_by('-highlight')
        annual_report_opt = list()
        if customer.anreport == 'N/A':
            annual_report_opt.append({'value': 'N/A', 'selected': True})
            annual_report_opt.append({'value': date.today().year + 1, 'selected': False})
        else:
            annual_report_opt.append({'value': 'N/A', 'selected': False})
            if customer.anreport == date.today().year + 1:
                annual_report_opt.append({'value': date.today().year - 1, 'selected': False})
                annual_report_opt.append({'value': date.today().year + 1, 'selected': True})
            else:
                annual_report_opt.append({'value': customer.anreport, 'selected': True})
                annual_report_opt.append({'value': date.today().year + 1, 'selected': False})
        return render(request, 'Procedure/Customers/customer_edit.html',
                      {'form': form, 'customer_id': customer.idcustomer, 'customer_notes': customer_notes,
                       'due': due['due'], 'birthday': birthday,
                       'customer': customer, 'drivers': drivers, 'annual_report_opt': annual_report_opt})


@login_required(login_url='Procedure:login')
@permission_required("Procedure.change_customers", login_url="Procedure:index")
def edit_customer(request, customer_id):
    if customer_id:
        customer = get_object_or_404(Customers, idcustomer=customer_id)
        due = Invoices.objects.filter(idcustomer=customer_id).aggregate(due=Sum('deu'))
        if request.method == "GET":
            birthday = False
            if customer.explic:
                if date.today().month == customer.explic.month and date.today().day == customer.explic.day:
                    birthday = True
            compare = datetime.strptime('0001-01-01', '%Y-%m-%d').strftime('%Y-%m-%d')
            customer.since = '01/01/0001' if customer.since is None or customer.since.strftime(
                '%Y-%m-%d') == compare else customer.since.strftime('%m/%d/%Y')
            customer.explic = '01/01/0001' if customer.explic is None or customer.explic.strftime(
                '%Y-%m-%d') == compare else customer.explic.strftime('%m/%d/%Y')
            customer.insuexpire = '01/01/0001' if customer.insuexpire is None or customer.insuexpire.strftime(
                '%Y-%m-%d') == compare else customer.insuexpire.strftime('%m/%d/%Y')
            customer.mcexp = '01/01/0001' if customer.mcexp is None or customer.mcexp.strftime(
                '%Y-%m-%d') == compare else customer.mcexp.strftime('%m/%d/%Y')
            customer.dotidexp = '01/01/0001' if customer.dotidexp is None or customer.dotidexp.strftime(
                '%Y-%m-%d') == compare else customer.dotidexp.strftime('%m/%d/%Y')
            customer.irpexp = '01/01/0001' if customer.irpexp is None or customer.irpexp.strftime(
                '%Y-%m-%d') == compare else customer.irpexp.strftime('%m/%d/%Y')
            customer.iftaexp = '01/01/0001' if customer.iftaexp is None or customer.iftaexp.strftime(
                '%Y-%m-%d') == compare else customer.iftaexp.strftime('%m/%d/%Y')
            customer.mnexp = '01/01/0001' if customer.mnexp is None or customer.mnexp.strftime(
                '%Y-%m-%d') == compare else customer.mnexp.strftime('%m/%d/%Y')
            customer.nyexp = '01/01/0001' if customer.nyexp is None or customer.nyexp.strftime(
                '%Y-%m-%d') == compare else customer.nyexp.strftime('%m/%d/%Y')
            customer.californiaexp = '01/01/0001' if customer.californiaexp is None or customer.californiaexp.strftime(
                '%Y-%m-%d') == compare else customer.californiaexp.strftime('%m/%d/%Y')
            customer.campcexp = '01/01/0001' if customer.campcexp is None or customer.campcexp.strftime(
                '%Y-%m-%d') == compare else customer.campcexp.strftime('%m/%d/%Y')
            customer.caexp = '01/01/0001' if customer.caexp is None or customer.caexp.strftime(
                '%Y-%m-%d') == compare else customer.caexp.strftime('%m/%d/%Y')
            customer.bitexp = '01/01/0001' if customer.bitexp is None or customer.bitexp.strftime(
                '%Y-%m-%d') == compare else customer.bitexp.strftime('%m/%d/%Y')
            customer.floridaexp = '01/01/0001' if customer.floridaexp is None or customer.floridaexp.strftime(
                '%Y-%m-%d') == compare else customer.floridaexp.strftime('%m/%d/%Y')
            customer.state_permits_exp = '01/01/0001' if customer.state_permits_exp is None or customer.state_permits_exp.strftime(
                '%Y-%m-%d') == compare else customer.state_permits_exp.strftime('%m/%d/%Y')
            customer.city_license_exp = '01/01/0001' if customer.city_license_exp is None or customer.city_license_exp.strftime(
                '%Y-%m-%d') == compare else customer.city_license_exp.strftime('%m/%d/%Y')
            customer.county_license_exp = '01/01/0001' if customer.county_license_exp is None or customer.county_license_exp.strftime(
                '%Y-%m-%d') == compare else customer.county_license_exp.strftime('%m/%d/%Y')
            customer.new_jersey_exp = '01/01/0001' if customer.new_jersey_exp is None or customer.new_jersey_exp.strftime(
                '%Y-%m-%d') == compare else customer.new_jersey_exp.strftime('%m/%d/%Y')
            customer.over_weight_exp = '01/01/0001' if customer.over_weight_exp is None or customer.over_weight_exp.strftime(
                '%Y-%m-%d') == compare else customer.over_weight_exp.strftime('%m/%d/%Y')
            customer.over_size_exp = '01/01/0001' if customer.over_size_exp is None or customer.over_size_exp.strftime(
                '%Y-%m-%d') == compare else customer.over_size_exp.strftime('%m/%d/%Y')
            customer.inner_bridge_exp = '01/01/0001' if customer.inner_bridge_exp is None or customer.inner_bridge_exp.strftime(
                '%Y-%m-%d') == compare else customer.inner_bridge_exp.strftime('%m/%d/%Y')
            customer.dot_biennal_update_date = '01/01/0001' if customer.dot_biennal_update_date is None or customer.dot_biennal_update_date.strftime(
                '%Y-%m-%d') == compare else customer.dot_biennal_update_date.strftime('%m/%d/%Y')
            customer.annual_inspection_truck_expiration = '01/01/0001' if customer.annual_inspection_truck_expiration is None or customer.annual_inspection_truck_expiration.strftime(
                '%Y-%m-%d') == compare else customer.annual_inspection_truck_expiration.strftime('%m/%d/%Y')
            customer.annual_inspection_trailer_expiration = '01/01/0001' if customer.annual_inspection_trailer_expiration is None or customer.annual_inspection_trailer_expiration.strftime(
                '%Y-%m-%d') == compare else customer.annual_inspection_trailer_expiration.strftime('%m/%d/%Y')
            customer.city = customer.city.upper() if customer.city else customer.city
            customer.county = customer.county.upper() if customer.county else customer.county
            customer.address = customer.address.upper() if customer.address else customer.address
            # user_login = request.user
            form = CustomersForm(instance=customer)
            drivers = Drivers.objects.filter(idcustomer=customer_id, status='Active').only('iddriver', 'nombre',
                                                                                           'random_test')
            customer_notes = Notes.objects.filter(idcustomer=customer_id, status='Active').filter(
                Q(pin_up=True) | Q(date_expiry__gte=datetime.today().strftime('%Y-%m-%d'))).order_by('-highlight')
            annual_report_opt = list()

            if customer.anreport == 'N/A':
                annual_report_opt.append({'value': 'N/A', 'selected': True})
                annual_report_opt.append({'value': 'INACTIVE', 'selected': False})
                annual_report_opt.append({'value': date.today().year + 1, 'selected': False})

            elif customer.anreport == 'INACTIVE':
                annual_report_opt.append({'value': 'N/A', 'selected': False})
                annual_report_opt.append({'value': 'INACTIVE', 'selected': True})
                annual_report_opt.append({'value': date.today().year + 1, 'selected': False})
            else:
                annual_report_opt.append({'value': 'N/A', 'selected': False})
                annual_report_opt.append({'value': 'INACTIVE', 'selected': False})
                if customer.anreport == date.today().year + 1:
                    annual_report_opt.append({'value': date.today().year - 1, 'selected': False})
                    annual_report_opt.append({'value': date.today().year + 1, 'selected': True})
                else:
                    annual_report_opt.append({'value': customer.anreport, 'selected': True})
                    annual_report_opt.append({'value': date.today().year + 1, 'selected': False})

            return render(request, 'Procedure/Customers/customer_edit.html',
                          {'form': form, 'customer_id': customer.idcustomer, 'birthday': birthday,
                           'customer': customer, 'drivers': drivers, 'customer_notes': customer_notes,
                           'due': due['due'], 'annual_report_opt': annual_report_opt})
        if request.method == 'POST':
            try:
                form = CustomersForm(request.POST, instance=customer)
                if form.is_valid():
                    customer_drivers = request.POST.getlist('drivers[]')
                    drivers = Drivers.objects.filter(idcustomer=customer_id, random_test=True)
                    if drivers.count != len(customer_drivers):
                        for d in drivers:
                            if d.iddriver in customer_drivers:
                                customer_drivers.remove(d.iddriver)
                            else:
                                driver = Drivers.objects.get(idcustomer=customer_id, iddriver=d.iddriver)
                                driver.random_test = False
                                driver.save(update_fields=['random_test'])
                        if len(customer_drivers) != 0:
                            for id in customer_drivers:
                                driver = Drivers.objects.get(idcustomer=customer_id, iddriver=id)
                                driver.random_test = True
                                driver.save(update_fields=['random_test'])
                    form.save()
                    return MessageResponse(description='Successfully saved').success()
                else:
                    print(form.errors.as_json(escape_html=False))
                    errors = form.errors
                    return MessageResponse(data={'fields': errors}, description='Validation').warning()
            except Exception as e:
                print(e)
                return MessageResponse(description='Customer Edit:Internal Server error').error()


@login_required(login_url='Procedure:login')
@permission_required("Procedure.delete_customers", login_url="Procedure:index")
def delete_customer(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST['idcustomer']
            customer = get_object_or_404(Customers, pk=customer_id)
            customer.delete()
            result = JsonResponse(
                {'message': {'description': "The customer has been deleted", 'type': 'success'}})
            return HttpResponse(result, content_type='application/json', status=200)
        except Exception as e:
            print(e)
            result = JsonResponse({'message': 'Error while deleting'})
            return HttpResponse(result, content_type='application/json', status=500)


@login_required(login_url='Procedure:login')
def list_units(request, customer_id):
    if request.GET.get('unit') and request.GET.get('unit') != '--Select--':
        unit = Units.objects.get(idunit=int(request.GET.get('unit')))
        return JsonResponse(
            {'vin': unit.vin, 'nounit': unit.nounit, 'make': unit.make, 'road_taxes': unit.road_taxes_id})
    else:
        customer = Customers.objects.only('cusname', 'mobile1', 'mobile2').get(pk=customer_id)
        return render(request, "Procedure/Customers/Unit/units.html",
                      {'customer_id': customer_id, 'cusname': customer.cusname, 'customer': customer})


@login_required(login_url="Procedure:login")
def change_status_units(request):
    content_type = ContentType.objects.get_for_model(Units)
    Permission.objects.get_or_create(
        codename="change_status_units",
        name="Change Status Units",
        content_type=content_type
    )
    if  request.method == "GET":
        idunit = int(request.GET.get('idunit'))
        try:
            unit = Units.objects.get(idunit=idunit)
            status = 'Inactive' if unit.status == 'Active' else 'Active'
            unit.status = status
            unit.save(update_fields=['status'])
            status = 200
            message = {"description": "Change Success", "type": "success"}
            result = JsonResponse({"message": message, "data": unit.status})
        except Exception as e:
            print(e)
            status = 500
            message = {'description': 'Error while saving', "type": "error"}
            result = JsonResponse({"message": message})
        return HttpResponse(result, content_type='application/json', status=status)


@login_required(login_url='Procedure:login')
def add_customers_unit(request, customer_id):
    if request.method == "POST":
        try:
            customer = get_object_or_404(Customers, pk=customer_id)
            form = UnitForm(request.POST)
            if form.is_valid():
                unit = form.save(commit=False)
                unit.customer = customer
                # unit.iduser = user_login.id
                unit.status = 'Active'
                unit.save()
                result = JsonResponse({'message': {'status': 'True', 'description': 'Save Success', 'type': 'success'}})
            else:
                print(form.errors)
                errors = form.errors.as_json(escape_html=False)
                result = JsonResponse(
                    {'message': {'status': 'False', 'errors': errors}})
        except Exception as e:
            print(e)
            result = JsonResponse({'message': {'status': 'False', 'description': str(e), 'type': 'danger'}})
        return HttpResponse(result)
    if request.method == "GET":
        form = UnitForm()
        # cusname = Customers.objects.values_list('cusname', flat=True).get(pk=customer_id)
        # customer = Customers.objects.only('cusname', 'mobile1', 'mobile2').get(pk=customer_id)
        url_action = '/Procedure/unit_add/%s' % customer_id
        return render(request, 'Procedure/Customers/Unit/unit.html',
                      {'form': form, 'url_action': url_action, 'customer_id': customer_id, 'modal_title': 'Add Units'})


@login_required(login_url='Procedure:login')
def search_by_vin(request):
    if request.method == 'GET':
        return render(request, 'Procedure/Customers/Unit/search.html')


@login_required(login_url='Procedure:login')
def view_customer_unit(request, unit_id):
    if unit_id:
        unit = get_object_or_404(Units, idunit=unit_id)
        if request.method == "GET":
            unit.road_taxes_date = unit.road_taxes_date.strftime('%m/%d/%Y')
            unit.date = unit.date.strftime('%m/%d/%Y')
            form = UnitForm(instance=unit)
            return render(request, 'Procedure/Customers/Unit/unit.html',
                          {'form': form, 'url_action': 'view', 'modal_title': 'Unit Details'})


@login_required(login_url='Procedure:login')
def edit_customer_unit(request, unit_id):
    if unit_id:
        unit = get_object_or_404(Units, idunit=unit_id)
        nounit = unit.nounit
        if request.method == "GET":
            if request.GET.get('update_date'):
                unit.road_taxes_date = date.today()
                unit.save()
                result = JsonResponse({'message': {'status': 'True', 'description': 'Save Success', 'type': 'success'},
                                       'date': unit.road_taxes_date.strftime('%m/%d/%Y')})
                return HttpResponse(result, content_type='application/json', status=200)
            else:
                unit.road_taxes_date = unit.road_taxes_date.strftime('%m/%d/%Y')
                unit.date = unit.date.strftime('%m/%d/%Y')
                form = UnitForm(instance=unit)
                unit_customer = Units.objects.select_related("idcustomer").get(idunit=unit_id)
                url_action = '/Procedure/unit_edit/%s' % unit_id
                return render(request, 'Procedure/Customers/Unit/unit.html',
                              {'form': form, 'unit_id': unit.idunit, 'url_action': url_action,
                               'customer_id': unit_customer.idcustomer_id, 'modal_title': 'Edit Unit'})
        if request.method == 'POST':
            try:
                form = UnitForm(request.POST, instance=unit)
                if form.is_valid():
                    user_login = request.user
                    unit_frm = form.save(commit=False)
                    # unit_frm.iduser = user_login.id
                    unit_frm.status = 'Active'
                    unit_frm.save()
                    if nounit != unit_frm.nounit:
                        Recive.objects.filter(idunit=nounit, idcustomer=unit_frm.idcustomer).update(
                            idunit=unit_frm.nounit)
                    result = JsonResponse(
                        {'message': {'status': 'True', 'description': 'Save Success', 'type': 'success'}})
                else:
                    print(form.errors)
                    errors = form.errors.as_json(escape_html=False)
                    result = JsonResponse(
                        {'message': {'status': 'False', 'errors': errors}})
            except Exception as e:
                print(e)
                result = JsonResponse({'message': {'status': 'False', 'description': str(e), 'type': 'danger'}})
            return HttpResponse(result)


@login_required(login_url='Procedure:login')
def delete_customer_unit(request):
    if request.method == 'POST':
        try:
            unit_id = request.POST['idunit']
            unit_db = get_object_or_404(Units, idunit=unit_id)
            unit_db.delete = True
            # unit_db.iduser = request.user.id
            unit_db.save()
            result = JsonResponse(
                {'message': {'status': 'True', 'description': 'Unit deleted', 'type': 'success'}})

        except Exception as e:
            print(e)
            result = JsonResponse({'message': {'status': 'False', 'description': str(e), 'type': 'danger'}})
        return HttpResponse(result)


class InvoicesDetails(View):
    content_type = ContentType.objects.get_for_model(Invoices)
    Permission.objects.get_or_create(
        name='Invoices',
        codename='invoices',
        content_type=content_type
    )
    template_name = "Procedure/Customers/Invoices/invoices.html"

    def get(self, request, *args, **kwargs):
        customer_id = kwargs['customer_id']
        customer = Customers.objects.only('cusname', 'mobile1', 'mobile2').get(pk=customer_id)
        return render(request, self.template_name,
                      {'customer_id': customer_id, 'cusname': customer.cusname, 'customer': customer})


'''def list_invoices(request, customer_id):
    content_type = ContentType.objects.get_for_model(Units)
    invoices = Invoices.objects.all().filter(idcustomer=customer_id, delete=False).order_by("idinvoice")
    customer = Customers.objects.only('cusname', 'owner', 'mobile1', 'mobile2').get(pk=customer_id)
    return render(request, "Procedure/Customers/Invoices/invoices.html",
                  {'invoices': invoices, 'customer_id': customer_id, 'cusname': customer.cusname, 'customer': customer}) '''


@login_required(login_url='Procedure:login')
def add_customers_invoice(request, customer_id, project_id):
    if request.method == "POST":
        user_login = request.user
        try:
            form = InvoiceForm(request.POST)
            if form.is_valid():
                invoice = form.customSave(user_login.id, request.POST.get("amount"))
                formset = InvoicesDetFormSet(request.POST, instance=invoice)
                if formset.is_valid():
                    invoice_details = formset.save(commit=False)
                    amount = 0
                    rows_form = 0
                    for detail in invoice_details:
                        amount += detail.amount
                        detail.save()
                        service = Services.objects.get(idservice=detail.code.idservice)
                        if project_id != 0 and service.need_invoice == False:
                            Projects.objects.filter(idproject=project_id).update(invoice=invoice, idinvoicedet=detail)
                        if service.is_project and project_id == 0:
                            project = Projects()
                            project.idinvoicedet = detail
                            project.quantity = detail.quantity
                            project.service = service
                            project.invoice = invoice
                            project.service_name = detail.service
                            if service.idservice == '158' or service.idservice == '216':
                                item_road = 'details-%s-comments_projects' % rows_form
                                if request.POST.get(item_road) is None:
                                    rows_form = rows_form + 1
                                    item_road = 'details-%s-comments_projects' % rows_form
                                    project.comments = request.POST.get(item_road)
                                else:
                                    project.comments = request.POST.get(item_road)
                            else:
                                project.comments = detail.coments
                            project.status = "Opened"
                            project.request = date.today().strftime("%Y-%m-%d")
                            project.iduser = User.objects.get(id=user_login.id)
                            project.statuslast = date.today().strftime("%Y-%m-%d")
                            project.iduserlast = User.objects.get(id=user_login.id)
                            project.idcustomer = Customers.objects.only('idcustomer').get(pk=customer_id)
                            item_notes = 'details-%s-comments_notes' % rows_form
                            project.save()
                            if request.POST.get(item_notes):
                                note_project = NotesProjects()
                                note_project.iduser = project.iduser
                                note_project.comments = request.POST.get(item_notes)
                                note_project.project = project
                                note_project.save()
                        rows_form = rows_form + 1

                    if invoice.amount != amount:
                        invoice.amount = round(amount, 2)
                        invoice.deu = round(amount, 2)
                        invoice.save()
                    data = {"idinvoice": invoice.idinvoice, "amount": amount}
                    message = {'description': 'Invoice saving success', 'type': 'success'}
                    result = JsonResponse({"message": message, "data": data})
                    return HttpResponse(result, content_type="application/json", status=200)
                else:
                    Invoices.objects.filter(idinvoice=invoice.idinvoice).delete()
                    print(formset.errors)
                    errors = formset.errors
                    idinvoice = invoice.idinvoice + 1
                    result = JsonResponse({'message': 'Validation', 'errors': errors, 'idinvoice': idinvoice})
                    return HttpResponse(result, content_type='application/json', status=500)
            else:
                print(form.errors)
                message = {'description': 'Check Fields', 'type': 'warning'}
                result = JsonResponse({"message": message})
                return HttpResponse(result, content_type="application/json", status=500)
        except Exception as e:
            print(e)
            message = {'description': 'Error while saving', 'type': 'error'}
            result = JsonResponse({"message": message})
            return HttpResponse(result, content_type="application/json", status=500)
    if request.method == "GET":
        template = 'Procedure/Customers/Invoices/modal-invoice.html' if project_id else 'Procedure/Customers/Invoices/invoice.html'
        form = InvoiceForm()
        if project_id:
            initial_data = Projects.objects.get(idproject=project_id)
            formset = InvoicesDetFormSet(initial=[{
                'code': initial_data.service.idservice, 'service': initial_data.service_name,
                'cost': initial_data.service.cost, 'rate': initial_data.service.rate, 'coments': initial_data.comments,
                'quantity': initial_data.quantity, 'amount': initial_data.service.rate
            }])
        else:
            formset = InvoicesDetFormSet()
        customer = Customers.objects.only("idcustomer", "cusname", "address").get(pk=customer_id)
        nxtinvoice = Invoices.objects.latest("idinvoice")
        datetoday = date.today().strftime("%m/%d/%Y")

        return render(request, template,
                      {'form': form, 'formset': formset, 'customer': customer, 'customer_id': customer.idcustomer,
                       'datetoday': datetoday, 'project_id': project_id,
                       'idinvoice': (nxtinvoice.idinvoice) + 1})


@login_required(login_url='Procedure:login')
def edit_invoice(request, idinvoice):
    if request.method == 'GET':
        invoice_header = Invoices.objects.get(idinvoice=idinvoice)
        form = InvoiceForm(instance=invoice_header)
        invoice_details = Invoice_det.objects.filter(idinvoice=invoice_header.idinvoice)
        paid = invoice_header.amount - invoice_header.deu
        return render(request, 'Procedure/Customers/Invoices/edit.html', {
            'form': form, 'customer_id': invoice_header.idcustomer.idcustomer, 'invdate': invoice_header.invdate,
            'paid': paid,
            'customer': invoice_header.idcustomer, 'idinvoice': invoice_header.idinvoice,
            'invoice_details': invoice_details
        })
    if request.method == 'POST':
        idinvoicedet = int(request.POST.get('idinvoicedet'))
        comment = request.POST.get('comment')
        try:
            Invoice_det.objects.filter(pk=idinvoicedet).update(coments=comment)
            result = JsonResponse(
                {'message': {'description': 'Save successful', 'type': 'success'}, 'comment': comment})
            return HttpResponse(result, content_type='application/json', status=200)
        except Exception as e:
            print(e)
            return HttpResponse({'message': 'Error while editing'}, content_type='application/json', status=500)


@login_required(login_url='Procedure:login')
def delete_invoice(request):
    if request.method == "POST":
        try:
            idinvoice = request.POST.get("idinvoice")
            comment = request.POST.get("comment")
            invoices = Invoices.objects.get(pk=idinvoice)
            cancel_invoice = Log_Invoice_cancel(invoice_id=invoices.idinvoice, user_id=request.user.id, motive=comment,
                                                amount=invoices.amount)
            cancel_invoice.save()
            invoices.deleted = True
            invoices.save()
            Invoice_det.objects.filter(idinvoice=idinvoice).update(delete=True)
            invoice_det = Invoice_det.objects.filter(idinvoice=idinvoice)
            for detail in invoice_det:
                idinvoice_det = detail.idinvoicedet
                Projects.objects.filter(idinvoicedet=idinvoice_det).update(deleted=True)
                deleteCommission(idinvoice_det)
            message = {'description': 'Successfully deleted ', 'type': 'success'}
            result = JsonResponse({"message": message})
            return HttpResponse(result, content_type="application/json", status=200)
        except Exception as e:
            print(e)
            message = {'description': 'Error ' + str(e), 'type': 'danger'}
            result = JsonResponse({"message": message})
            return HttpResponse(result, content_type="application/json", status=500)


@login_required(login_url='Procedure:login')
def get_services(request):
    data_from_post = json.load(request)['description']
    if request.method == "POST":
        description = data_from_post
        try:
            service = Services.objects.only("idservice", "rate", "cost").get(description=description)
            data = JsonResponse({"code": service.idservice, "rate": service.rate, "cost": service.cost})
            return HttpResponse(data, content_type="application/json", status=200)
        except Exception as e:
            print(e)
            return HttpResponse({}, content_type="application/json", status=500)


@login_required(login_url='Procedure:login')
def category_road_tax(request):
    if  request.method == 'GET':
        if request.GET.get('id'):
            category = Road_Taxes.objects.get(pk=request.GET.get('id'))
            months = int(request.GET.get('months'))
            value_paid = round((category.tax_value / 12) * months, 2)
            return JsonResponse({'tax_value': value_paid})
        if request.GET.get('gross'):
            try:
                categories = Road_Taxes.objects.filter(max_gross_weight__gte=int(request.GET.get('gross')),
                                                       min_gross_weight__lte=int(request.GET.get('gross')))
                return JsonResponse({'category': categories[0].id})
            except Exception as e:
                pass

    if request.method == 'GET' and request.GET.get('customer_id'):
        form = CategoryRoadTaxForm
        customer_id = int(request.GET.get('customer_id'))
        units = Units.objects.filter(idcustomer=customer_id, delete=False, status='Active')
        return render(request, 'Procedure/Customers/Invoices/category.html',
                      {'form': form, 'units': units, 'customer_id': customer_id})


@login_required(login_url='Procedure:login')
def florida_tag_classification(request):
    if  request.method == 'GET':
        if request.GET.get('id'):
            months = int(request.GET.get('months'))
            fl_tag = Fl_Tag_Price_Month.objects.get(florida_tag_id=request.GET.get('id'), month=months)
            return JsonResponse({'fl_tag': fl_tag.price})

    if request.method == 'GET' and request.GET.get('customer_id'):
        form = FloridaTagTaxForm
        customer_id = int(request.GET.get('customer_id'))
        units = Units.objects.filter(idcustomer=customer_id, delete=False, status='Active')
        return render(request, 'Procedure/Customers/Invoices/floridaTag.html',
                      {'form': form, 'units': units, 'customer_id': customer_id})


@login_required(login_url='Procedure:login')
def paid(request, idinvoice):
    if request.method == "POST":
        user_login = request.user
        paidm = Invoice_paid()
        formpaid = PaidForm(request.POST)
        if formpaid.is_valid():
            try:
                paid_date = datetime.strptime(formpaid.cleaned_data['datepaid'], '%m/%d/%Y').date()
                invoice = Invoices.objects.only("idinvoice", "amount", "deu", "iduser", "idcustomer", "status").get(
                    pk=idinvoice)
                paidm.idinvoice = invoice
                paidm.datepaid = paid_date
                paidm.typepaid = formpaid.cleaned_data['typepaid']
                var_paid = formpaid.cleaned_data['paid']
                paidm.paid = var_paid
                due = formpaid.cleaned_data['due']
                paidm.deu = due
                paidm.comment = formpaid.cleaned_data['comment']
                paidm.iduser = User.objects.get(pk=int(formpaid.cleaned_data['approved']))
                if formpaid.cleaned_data['typepaid'] == "Credit":
                    try:
                        customer = Customers.objects.only("idcustomer", "cusname").get(pk=invoice.idcustomer.idcustomer)
                        credit = Credits()
                        credit.idcustomer = customer
                        credit.cusname = customer.cusname
                        credit.date = paid_date
                        credit.iduser = user_login.id
                        credit.aproved = formpaid.cleaned_data['approved']
                        credit.credit = var_paid
                        credit.comment = formpaid.cleaned_data['comment']
                        credit.idinvoice = invoice
                        credit.status = "Unpaid"
                        # Save Credit
                        credit.save()
                    except Exception as e:
                        print(e)
                        message = {'description': 'Error while saving credit', 'type': 'error'}
                        result = JsonResponse({"message": message})
                        return HttpResponse(result, content_type="application/json", status=500)
                # Save paid
                paidm.save()
                # Update Invoice                
                if due == 0:
                    Invoices.objects.filter(pk=idinvoice).update(status="Paid", deu=0, paid_date=paid_date)
                    saveCommision(idinvoice, request.user)
                else:
                    Invoices.objects.filter(pk=idinvoice).update(deu=due, paid_date=paid_date)
                total_paid = Invoice_paid.objects.filter(idinvoice=idinvoice).aggregate(Sum("paid"))
                message = {'description': 'Paid saved successfully', 'type': 'success'}
                data = {"total_paid": total_paid["paid__sum"], "due": due}
                result = JsonResponse({"message": message, "data": data})
                return HttpResponse(result, content_type="application/json", status=200)
            except Exception as e:
                print(e)
                result = JsonResponse({"message": "Error while saving"})
                return HttpResponse(result, content_type="application/json", status=500)
        else:
            message = {'description': 'Check Fields', 'type': 'warning'}
            print(formpaid.errors)
            result = JsonResponse({"message": message})
            return HttpResponse(result, content_type="application/json", status=500)
    if request.method == "GET":
        invoice = Invoices.objects.only("idinvoice", "amount", "deu", "iduser").get(pk=idinvoice)
        users = User.objects.all().only("id", "first_name", "last_name", 'fullname').filter(is_active=True,
                                                                                            is_superuser=False)
        today = date.today().strftime("%m/%d/%Y")
        choices = ["Cash", "Credit Card", "Check", "Zelle"]
        args = {'today': today, "invoice": invoice, "users": users, "choices": choices}
        return render(request, 'Procedure/Customers/Paid/paid.html', args)


@login_required(login_url='Procedure:login')
def pdf_invoice(request, idinvoice):
    invoice = Invoices()
    customer = Customers()
    msg = ''
    Paid = {"datepaid": '', "total_paid": '0', "check": '0', "cash": '0',
            "credit_card": '0'}
    try:
        details_invoice = Invoice_det.objects.select_related("idinvoice__idcustomer").filter(idinvoice=idinvoice) \
            .only("idinvoice", "code__idservice", "service", "quantity", "rate", "discount", "amount", "coments", "idinvoice",
                  "discountype",
                  "idinvoice__invdate", "idinvoice__amount", "idinvoice__idcustomer", "idinvoice__status",
                  "idinvoice__deu",
                  "idinvoice__idcustomer__cusname", "idinvoice__idcustomer__address", "idinvoice__idcustomer__city",
                  "idinvoice__idcustomer__state", "idinvoice__idcustomer__codepostal", "idinvoice__idcustomer__mobile1"
                  )
        try:
            invoice = details_invoice.first().idinvoice
            invoice.invdate = invoice.invdate.strftime("%m/%d/%Y")
            customer = invoice.idcustomer
        except Exception as e:
            print(e)
        total_paid = Invoice_paid.objects.filter(idinvoice=idinvoice).aggregate(total=Sum("paid"))
        check = Invoice_paid.objects.filter(idinvoice=idinvoice, typepaid="Check").aggregate(check=Sum("paid"))
        cash = Invoice_paid.objects.filter(idinvoice=idinvoice, typepaid="Cash").aggregate(cash=Sum("paid"))
        credit_card = Invoice_paid.objects.filter(idinvoice=idinvoice, typepaid="Credit Card").aggregate(
            credit_card=Sum("paid"))
        zelle = Invoice_paid.objects.filter(idinvoice=idinvoice, typepaid="Zelle").aggregate(
            zelle=Sum("paid"))
        datepaid = Invoice_paid.objects.only("datepaid").filter(idinvoice=idinvoice).latest('datepaid')
        datepaid = datepaid.datepaid.strftime('%m/%d/%Y')
        Paid = {"datepaid": datepaid, "total_paid": total_paid["total"], "check": check["check"], "cash": cash["cash"],
                "credit_card": credit_card["credit_card"], "zelle": zelle["zelle"]}
    except Exception as e:
        print(e)
    if invoice.invdate is None:
        invoice = Invoices.objects.get(pk=idinvoice)
        invoice.invdate = invoice.invdate.strftime("%m/%d/%Y")
        customer = invoice.idcustomer
        msg = 'There are no invoices details'
    return render(request, "PDF/pdf_invoice.html",
                  {"details": details_invoice, "invoice": invoice, "customer": customer,
                   "customer_id": invoice.idcustomer_id, "Paid": Paid, 'message': msg})


@login_required(login_url='Procedure: login')
def list_paids(request, idinvoice):
    content_type = ContentType.objects.get_for_model(Invoice_paid)
    invoice = Invoices.objects.only("idinvoice", "cusname").get(pk=idinvoice)
    paids = Invoice_paid.objects.all().filter(idinvoice=idinvoice).order_by("idpaid")
    return render(request, "Procedure/Customers/Paid/paids.html",
                  {'invoice': invoice, 'paids': paids, 'customer_id': invoice.idcustomer_id,
                   'customer': invoice.idcustomer})


@login_required(login_url='Procedure:login')
def edit_paid(request, idpaid):
    invoice_paid = get_object_or_404(Invoice_paid, idpaid=idpaid)
    typepaid = invoice_paid.typepaid
    user_login = request.user
    if request.method == "POST":
        frmpaid = UpdatePaidFrm(request.POST, instance=invoice_paid)
        if frmpaid.is_valid():
            try:
                svpaid = frmpaid.save(commit=False)
                if typepaid == "Credit" and svpaid.typepaid != "Credit":
                    credit = Credits.objects.get(idinvoice=invoice_paid.idinvoice)
                    credit.delete()
                if svpaid.typepaid == "Credit":
                    invoice = Invoices.objects.get(pk=invoice_paid.idinvoice_id)
                    customer = Customers.objects.only("idcustomer", "cusname").get(pk=invoice.idcustomer.idcustomer)
                    credit = Credits()
                    credit.idcustomer = customer
                    credit.cusname = customer.cusname
                    credit.date = svpaid.datepaid
                    credit.iduser = user_login.id
                    credit.aproved = svpaid.iduser
                    credit.credit = svpaid.paid
                    credit.comment = svpaid.comment
                    credit.idinvoice = invoice
                    credit.status = "Unpaid"
                    # Save Credit
                    credit.save()
                svpaid.save()
                data = {}
                message = {'description': 'Pay updated successfully', 'type': 'success'}
                result = JsonResponse({"message": message, "data": data})
                return HttpResponse(result, content_type="application/json", status=200)
            except Exception as e:
                print(e)
                message = {'description': 'Error ' + str(e), 'type': 'danger'}
                result = JsonResponse({"message": message})
                return HttpResponse(result, content_type="application/json", status=500)
        else:
            message = {'description': 'Check Fields', 'type': 'warning'}
            print(frmpaid.errors)
            result = JsonResponse({"message": message})
            return HttpResponse(result, content_type="application/json", status=500)
    if request.method == "GET":
        users = User.objects.all().filter(is_active=True, is_superuser=False).only("id", "first_name", "last_name")
        choices = ["Cash", "Credit Card", "Check", "Zelle"]
        args = {"paid": invoice_paid, "users": users, "choices": choices}
        return render(request, 'Procedure/Customers/Paid/edit_paid.html', args)


@login_required(login_url='Procedure:login')
def list_fueltaxes(request, customer_id):
    content_type = ContentType.objects.get_for_model(Millages)
    Permission.objects.get_or_create(
        codename='list_millages',
        name='List Millages (Fuel Taxes)',
        content_type=content_type,
    )
    customer = Customers.objects.only("idcustomer", "cusname").get(pk=customer_id)
    millages = Millages.objects.filter(idcustomer=customer_id).order_by("-year", "qtr")
    return render(request, "Procedure/Customers/Fuel_Taxes/list.html",
                  {"millages": millages, "customer": customer, "customer_id": customer.idcustomer})


@login_required(login_url="Procedure:login")
def add_fueltaxes(request, idcustomer):
    if request.method == "GET":
        form = MillagesForm()
        customer = Customers.objects.only("idcustomer", "cusname").get(pk=idcustomer)
        return render(request, "Procedure/Customers/Fuel_Taxes/add.html",
                      {"customer": customer, "customer_id": customer.idcustomer, "form": form})
    if request.method == "POST":
        form = MillagesForm(request.POST)
        if form.is_valid():
            try:
                millage = Millages.objects.filter(idcustomer=idcustomer, year=form.cleaned_data['year'],
                                                  qtr=form.cleaned_data['qtr']).count()
                if millage == 0:
                    form.save()
                    message = {'description': 'Quora added successfully', 'type': 'success'}
                    result = JsonResponse({"message": message, "data": {}})
                    return HttpResponse(result, content_type="application/json", status=200)
                else:
                    return HttpResponse(
                        JsonResponse({'message': {'description': 'This quora already exists', 'type': 'error'}}),
                        content_type='application/json', status=500)
            except Exception as e:
                print(e)
                message = {'description': 'Error while saving Millage', 'type': 'error'}
                result = JsonResponse({"message": message})
                return HttpResponse(result, content_type="application/json", status=500)
        else:
            print(form.errors)
            message = {'description': 'Check Fields', 'type': 'warning'}
            result = JsonResponse({"message": message})
            return HttpResponse(result, content_type="application/json", status=500)


def view_fueltaxes(request, idmillage):
    millages = get_object_or_404(Millages, idmillage=idmillage)
    if request.method == "GET":
        form = MillagesForm(instance=millages)
        return render(request, "Procedure/Customers/Fuel_Taxes/edit.html",
                      {"customer_id": millages.idcustomer_id, "idmillage": millages.idmillage, "form": form,
                       'cusname': millages.idcustomer.cusname})


@login_required(login_url="Procedure:login")
def edit_fueltaxes(request, idmillage):
    millages = get_object_or_404(Millages, idmillage=idmillage)
    if request.method == "POST":
        form = MillagesForm(request.POST, instance=millages)
        if form.is_valid():
            try:
                form.save()
                message = {'description': 'Millage Saved Satisfactorily', 'type': 'success'}
                result = JsonResponse({"message": message, "data": {}})
                return HttpResponse(result, content_type="application/json", status=200)
            except Exception as e:
                print(e)
                message = {'description': 'Error ' + str(e), 'type': 'error'}
                result = JsonResponse({"message": message})
                return HttpResponse(result, content_type="application/json", status=500)
        else:
            print(form.errors)
            message = {'description': 'Check fields', 'type': 'error'}
            result = JsonResponse({"message": message})
            return HttpResponse(result, content_type="application/json", status=500)


@login_required(login_url="Procedure:login")
def list_recive(request):
    idcustomer = request.POST.get("idcustomer")
    idunit = request.POST.get("idunit")
    year = request.POST.get("year")
    quarter = request.POST.get("quarter")
    try:
        if "1" == quarter:
            report = Recive.objects.all().filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month__gte=1,
                                                 date__month__lte=3).order_by('date')
            first_month = serializers.serialize('json', report.filter(date__month=1))
            second_month = serializers.serialize('json', report.filter(date__month=2))
            third_month = serializers.serialize('json', report.filter(date__month=3))
        if "2" == quarter:
            report = Recive.objects.all().filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month__gte=4,
                                                 date__month__lte=6).order_by('date')
            first_month = serializers.serialize('json', report.filter(date__month=4))
            second_month = serializers.serialize('json', report.filter(date__month=5))
            third_month = serializers.serialize('json', report.filter(date__month=6))
        if "3" == quarter:
            report = Recive.objects.all().filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month__gte=7,
                                                 date__month__lte=9).order_by('date')
            first_month = serializers.serialize('json', report.filter(date__month=7))
            second_month = serializers.serialize('json', report.filter(date__month=8))
            third_month = serializers.serialize('json', report.filter(date__month=9))
        if "4" == quarter:
            report = Recive.objects.all().filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month__gte=10,
                                                 date__month__lte=12).order_by('date')
            first_month = serializers.serialize('json', report.filter(date__month=10))
            second_month = serializers.serialize('json', report.filter(date__month=11))
            third_month = serializers.serialize('json', report.filter(date__month=12))
        return JsonResponse([first_month, second_month, third_month], safe=False)
    except Exception as e:
        print(e)
        message = {'description': e, 'type': 'error'}
        result = JsonResponse({"message": message})
        return HttpResponse(result, content_type="application/json", status=500)


@login_required(login_url="Procedure:login")
def list_recive_summary(request):
    idcustomer = request.POST.get("idcustomer")
    idunit = request.POST.get("idunit")
    year = request.POST.get("year")
    quarter = int(request.POST.get("quarter"))
    first_month, second_month, third_month = receive_summary(idcustomer, idunit, year, quarter)
    first_month_json = json.dumps(list(first_month), cls=DjangoJSONEncoder)
    second_month_json = json.dumps(list(second_month), cls=DjangoJSONEncoder)
    third_month_json = json.dumps(list(third_month), cls=DjangoJSONEncoder)
    return JsonResponse([first_month_json, second_month_json, third_month_json], safe=False)


@login_required(login_url="Procedure:login")
def add_recive(request, customer_id):
    if request.method == "GET":
        form = ReciveForm()
        unit = Units.objects.all().filter(idcustomer=customer_id, status='Active', delete=False).only("nounit")
        return render(request, "Procedure/Customers/Fuel_Taxes/recive.html",
                      {"customer_id": customer_id, "form": form, "unit": unit})
    if request.method == "POST":
        form = ReciveForm(request.POST)
        if form.is_valid():
            try:
                recive = form.save(commit=False)
                recive.save()
                recive_return = serializers.serialize('json', Recive.objects.filter(pk=recive.idrecive))
                message = {'description': 'Saved saccessfully', 'type': 'success'}
                result = JsonResponse({"message": message, "data": recive_return}, safe=False)
                status = 200
            except Exception as e:
                print(e)
                status = 500
                message = {'description': 'An error ocurred while saving', 'type': 'error'}
                result = JsonResponse({"message": message})
        else:
            # print(form.errors.as_data())
            print(form.errors.get_json_data(escape_html=True))
            status = 500
            message = {'description': 'An error ocurred while saving', 'type': 'warning'}
            result = JsonResponse({"message": message})
        return HttpResponse(result, content_type="application/json", status=status)


@login_required(login_url="Procedure:login")
def delete_recive(request):
    if request.method == "POST":
        try:
            idrecive = request.POST.get("idrecive")
            recive = get_object_or_404(Recive, idrecive=idrecive)
            recive.delete()
            message = {'description': 'Deleted successfully', 'type': 'success'}
            result = JsonResponse({"message": message})
            status = 200
        except Exception as e:
            print(e)
            message = {'description': 'An error ocurred while saving', 'type': 'warning'}
            result = JsonResponse({"message": message})
            status = 500
        return HttpResponse(result, content_type="application/json", status=status)


@login_required(login_url="Procedure:login")
def cover_page(request, customer_id):
    if request.method == "GET":
        customer = customer = Customers.objects.only("idcustomer", "cusname").get(pk=customer_id)
        return render(request, "Procedure/Customers/Fuel_Taxes/cover.html",
                      {"customer_id": customer_id, "customer": customer})


@login_required(login_url='Procedure:login')
def list_drives(request, customer_id):
    content_type = ContentType.objects.get_for_model(Drivers)
    Permission.objects.get_or_create(
        codename='list_drivers',
        name='List Drivers',
        content_type=content_type,
    )
    customer = Customers.objects.only("idcustomer", "cusname").get(pk=customer_id)
    drivers = Drivers.objects.filter(idcustomer=customer_id).order_by("-iddriver")
    return render(request, "Procedure/Customers/Drivers/list.html",
                  {"drivers": drivers, "customer": customer, "customer_id": customer.idcustomer})


@login_required(login_url="Procedure:login")
def add_driver(request, customer_id):
    if request.method == "GET":
        form = DriverForm()
        customer = Customers.objects.only("idcustomer", "cusname").get(pk=customer_id)
        return render(request, "Procedure/Customers/Drivers/add.html",
                      {"customer_id": customer_id, "form": form, "customer": customer})
    if request.method == "POST":
        form = DriverForm(request.POST)
        if form.is_valid():
            try:
                driver = form.customSave()
                # driver.preemp = 'Yes' if (request.POST.get('preemp')) else 'No'
                message = {'description': 'Saved successfull', 'type': 'success'}
                json = serializers.serialize('json', [driver])
                result = JsonResponse({"message": message, 'data': json}, safe=False)
                status = 200
            except Exception as e:
                print(e)
                status = 500
                message = {'description': 'An error ocurred while saving', 'type': 'error'}
                result = JsonResponse({"message": message})
        else:
            print(form.errors.as_data())
            # print(form.errors.get_json_data(escape_html=True))
            status = 500
            message = {'description': 'An error ocurred while saving', 'type': 'warning'}
            result = JsonResponse({"message": message})
        return HttpResponse(result, content_type="application/json", status=status)


@login_required(login_url="Procedure:login")
def edit_driver(request, iddriver):
    if request.method == "GET":
        try:
            driver = Drivers.objects.select_related('idcustomer').get(pk=iddriver)
            form = DriverForm(instance=driver)
        except Exception as e:
            print(e)
        return render(request, "Procedure/Customers/Drivers/edit.html", {
            "form": form, "cusname": driver.idcustomer.cusname, "customer_id": driver.idcustomer_id,
            "iddriver": driver.iddriver
        })
    if request.method == "POST":
        try:
            driver = get_object_or_404(Drivers, iddriver=iddriver)
            form = DriverForm(request.POST, instance=driver)
            if form.is_valid():
                driver = form.save(commit=False)
                # driver.preemp = 'Yes' if (request.POST.get('preemp')) else 'No'
                driver.save()
                message = {'description': 'Saved successfully', 'type': 'success'}
                result = JsonResponse({"message": message, "data": {}})
                status = 200
            else:
                print(form.errors)
                message = {'description': 'Check Fields:', 'type': 'warning'}
                result = JsonResponse({"message": message})
                status = 500
        except Exception as e:
            print(e)
            message = {'description': 'Error while saving', 'type': 'error'}
            result = JsonResponse({"message": message})
            status = 500
        return HttpResponse(result, content_type="application/json", status=status)


@login_required(login_url="Procedure:login")
def change_status_driver(request):
    content_type = ContentType.objects.get_for_model(Drivers)
    Permission.objects.get_or_create(
        codename="change_status_driver",
        name="Change Status Driver",
        content_type=content_type
    )
    if  request.method == "GET":
        iddriver = int(request.GET.get('iddriver'))
        try:
            driver = Drivers.objects.get(iddriver=iddriver)
            status = 'Inactive' if driver.status == 'Active' else 'Active'
            driver.status = status
            driver.save(update_fields=['status'])
            status = 200
            message = {"description": "Change Success", "type": "success"}
            result = JsonResponse({"message": message, "data": driver.status})
        except Exception as e:
            print(e)
            status = 500
            message = {'description': 'Error while saving', "type": "error"}
            result = JsonResponse({"message": message})
        return HttpResponse(result, content_type='application/json', status=status)


@login_required(login_url="Procedure:login")
def add_exams(request, iddriver):
    if request.method == "GET":
        form = ExamForm()
        driver = Drivers.objects.only('iddriver', 'nombre', 'idcustomer_id', 'idcustomer__cusname').get(
            iddriver=iddriver)
        exams = Exams.objects.filter(iddriver=iddriver)
        return render(request, 'Procedure/Customers/Exams/add.html', {'form': form, 'driver': driver, 'exams': exams})
    if request.method == "POST":
        form = ExamForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                exam = form.save(commit=False)
                exam.filename = request.FILES["path"].name
                exam.path = request.FILES["path"]
                exam.save()
                data = {
                    'idexam': exam.idexam, 'type': exam.type, 'dateexam': exam.dateexam.strftime('%m/%d/%Y'),
                    'result': exam.result,
                    'dateresult': exam.dateresult.strftime('%m/%d/%Y'), 'lote_number': exam.lote_number,
                    'lote_expiration': exam.lote_expiration.strftime(
                        '%m/%d/%Y') if exam.lote_expiration == '0001-01-01' else '', 'path': str(exam.path),
                    'filename': exam.filename
                }
                return MessageResponse(description="Success", data=data).success()
            except Exception as e:
                print(f'Errror al guardar {e}')
                return MessageResponse(description="Error while save").error()
        else:
            errors = form.errors
            return MessageResponse(description='Validation', data=errors).warning()


@login_required(login_url='Procedure:login')
def list_notes(request, customer_id):
    if request.method == 'GET':
        form = NotesForm()
        customer = Customers.objects.only('idcustomer', 'cusname', 'mobile1', 'mobile2').get(
            idcustomer=customer_id)
        datetoday = date.today().strftime("%m/%d/%Y")
        notes = Notes.objects.filter(idcustomer=customer_id, status="Active")
        return render(request, "Procedure/Customers/Notes/notes.html",
                      {'form': form, 'cusname': customer.cusname, 'customer_id': customer.idcustomer, 'notes': notes,
                       'customer': customer, 'today': datetoday})


class CustomerNotesView(View):

    def get(self, request, *args, **kwargs):
        form = NotesForm()
        customer = Customers.objects.get(idcustomer=kwargs['customer_id'])
        return render(request, 'Procedure/Customers/Notes/add.html', {'form': form, 'customer': customer})

    def post(self, request, *args, **kwargs):
        form = NotesForm(request.POST)
        if form.is_valid():
            try:
                notes = form.save()
                status = 200
                message = {'description': 'Note saved successfully', 'type': 'success'}
                note = {'idnote': notes.idnote, 'fullname': notes.fullname,
                        'date': notes.created_at.strftime('%m/%d/%Y'),
                        'note': notes.note}
                result = JsonResponse({'message': message, 'note': note})
            except Exception as e:
                print(e)
                message = {'description': 'Error while saving', 'type': 'error'}
                status = 500
                result = JsonResponse({'message': message})
        else:
            print(form.errors.as_data)
            status = 500
            message = {'description': 'Check Fields', 'type': 'warning'}
            result = JsonResponse({'message': message})
        return HttpResponse(result, content_type='application/json', status=status)


@login_required(login_url='Procedure:login')
def list_projects(request, customer_id, show_all):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname', 'mobile1', 'mobile2').get(
            idcustomer=customer_id)
        if show_all:
            projects = Projects.objects.all().filter(idcustomer=customer_id, deleted=False)
        else:
            projects = Projects.objects.all().filter(idcustomer=customer_id, deleted=False).filter(
                Q(status='Opened') | Q(status='In Process'))
        data = list()
        for json in projects:
            num_notes = NotesProjects.objects.filter(project=json).count()
            data.append({
                'id': json.idproject, 'quantity': json.quantity,
                'services': json.service, 'comments': json.comments,
                'representative': (json.iduser.first_name + " " + json.iduser.last_name),
                'invoice': json.idinvoicedet.idinvoice.status if json.invoice else 'No Invoice',
                'num_notes': num_notes, 'statuslast': json.statuslast,
                'request': json.request, 'status': json.status,
                'userlast': (json.iduserlast.first_name + " " + json.iduserlast.last_name).upper()
            })
        status = ['Opened', 'In Process', 'Closed']
        return render(request, "Procedure/Customers/Projects/list.html",
                      {'cusname': customer.cusname, 'customer_id': customer.idcustomer, 'projects': data,
                       'status_p': status, 'showAll': show_all, 'customer': customer})


@login_required(login_url='Procedure:login')
def edit_projects(request):
    if request.method == 'POST':
        status_project = str(request.POST.get('status'))
        idprojects = request.POST.getlist('idprojects[]')
        iduserlast = request.user.id
        try:
            projects = list()
            user_last = request.user.first_name + ' ' + request.user.last_name
            today = datetime.today()
            message = {'description': 'Project update succesfully', 'type': 'success'}
            for idproject in idprojects:
                project = int(idproject)
                user = User.objects.get(pk=iduserlast)
                Projects.objects.filter(idproject=project).update(status=status_project, iduserlast=user,
                                                                  statuslast=today)
                p = Projects.objects.only('idproject', 'status', 'iduserlast', 'statuslast', 'idcustomer', 'service').get(pk=project)
                projects.append({'id': p.idproject, 'status': p.status, 'userlast': user_last,
                                 'statuslast': p.statuslast.strftime('%m/%d/%Y')})
                if(status_project == 'Closed'):
                    if p.service.idservice == 6 or p.service.idservice == 9:
                        customer = Customers.objects.get(idcustomer=p.idcustomer.idcustomer)
                        year = today.year+1 if today.month >=9 else today.year
                        customer.bitexp = datetime.strptime('%s-12-31'%year, '%Y-%m-%d')
                        customer.dotclient = True
                        customer.save()
                        email_status_message = SendCertificateRandomTestEmail().sendCertificates(request, customer.idcustomer)
                        if email_status_message.status_code != 200:
                            message = {'description': 'Project update succesfully but error sending email', 'type': 'warning'}
                        else:
                            message = {'description': 'Project update succesfully and email sent', 'type': 'success'}
            result = JsonResponse({'message': message, 'data': projects})
            status = 200
        except Exception as e:
            print(e)
            message = {'description': 'Error while updating the project' + str(e), 'type': 'error'}
            status = 500
            result = JsonResponse({'message': message})
        return HttpResponse(result, content_type='application/json', status=status)


@login_required(login_url='Procedure:login')
def edit_project(request):
    if request.method == 'POST':
        try:
            if request.POST.get("idproject"):
                status_project = str(request.POST.get('status'))
                project_id = request.POST.get('idproject')
            else:
                json_data = json.load(request)
                status_project = json_data['status']
                project_id = json_data['idproject']
            
            message = {'description': 'Project update successfully', 'type': 'success'}
            iduserlast = request.user.id
            today = datetime.today()
            user = User.objects.get(pk=iduserlast)
            if(status_project == 'Closed'):
                project = Projects.objects.get(idproject=project_id)
                service_id = project.service.idservice
                
                if service_id == 6 or service_id == 9:
                    customer = Customers.objects.get(idcustomer=project.idcustomer.idcustomer)
                    year = today.year+1 if today.month >=9 else today.year
                    customer.bitexp = datetime.strptime('%s-12-31'%year, '%Y-%m-%d')
                    customer.dotclient = True
                    customer.save()
                    message = SendCertificateRandomTestEmail().sendCertificates(request, customer.idcustomer)
                    
                    if message.status_code != 200:
                        message = {'description': 'Project update succesfully but error sending email', 'type': 'warning'}
                    else:
                        message = {'description': 'Project update succesfully and email sent', 'type': 'success'}          
            Projects.objects.filter(idproject=project_id).update(status=status_project, iduserlast=user,
                                                                 statuslast=today)
            summary = summary_projects(request)
            result = JsonResponse({'message': message, 'data': {
                'id': project_id, 'status': status_project, 'lastuser': (user.first_name + " " + user.last_name).upper()
            }, 'open_projects': summary['open_projects'], 'date_open': summary["date_open"],
                                   'date_inprocess': summary["date_inprocess"],
                                   'inprocess_project': summary["inprocess_project"],
                                   'new_projects': summary["new_projects"], 'invoice_unpaid': summary['num_invoices']})
            status = 200
        except Exception as e:
            print(e)
            message = {'description': 'Error while updating the project' + str(e), 'type': 'error'}
            status = 500
            result = JsonResponse({'message': message})
        return HttpResponse(result, content_type='application/json', status=status)


# Applications
@login_required(login_url='Procedure:login')
def list_applications(request, customer_id):
    customer = Customers.objects.only('cusname', 'mobile1', 'mobile2').get(pk=customer_id)
    return render(request, 'Procedure/Customers/Applications/applications.html',
                  {'customer_id': customer_id, 'customer': customer})


# End Applications

@login_required(login_url='Procedure:login')
def bills_paid(request):
    if request.method == 'GET':
        today = date.today()
        payable = Payable.objects.select_related('idcustomer').values('idpayable', 'datetrans', 'typepayamount',
                                                                      'typepaycost',
                                                                      'typetrans', 'nobill', 'amount', 'cost',
                                                                      'idinvoice', 'idcustomer_id',
                                                                      'idcustomer__cusname').filter(datetrans=today)
        sum_cash = payable.filter(typepaycost='Cash').aggregate(cost_s=Sum('cost'))
        sum_check = payable.filter(typepaycost='Check').aggregate(cost_s=Sum('cost'))
        sum_credit_card = payable.filter(typepaycost='Credit Card').aggregate(cost_s=Sum('cost'))
        total_amount = payable.aggregate(amount_s=Sum('amount'))
        total_cost = payable.aggregate(cost_s=Sum('cost'))
        customers = Customers.objects.all().only('idcustomer', 'cusname')
        return render(request, 'Procedure/Accounting/bills_paid.html',
                      {'data': payable, 'cash': sum_cash['cost_s'], 'check': sum_check['cost_s'],
                       'credit_card': sum_credit_card['cost_s'], 'total_amount': total_amount['amount_s'],
                       'total_cost': total_cost['cost_s'], 'customers': customers
                       })
    if request.method == 'POST':
        sldatetrans = int(request.POST.get('sldate'))
        idcustomer = int(request.POST.get('customers'))
        if idcustomer == 0:
            main_query = Payable.objects.select_related('idcustomer').values('idpayable', 'datetrans', 'typepayamount',
                                                                             'typepaycost',
                                                                             'typetrans', 'nobill', 'amount', 'cost',
                                                                             'idinvoice', 'idcustomer_id',
                                                                             'idcustomer__cusname')
        else:
            main_query = Payable.objects.select_related('idcustomer').values('idpayable', 'datetrans', 'typepayamount',
                                                                             'typepaycost',
                                                                             'typetrans', 'nobill', 'amount', 'cost',
                                                                             'idinvoice', 'idcustomer_id',
                                                                             'idcustomer__cusname').filter(
                idcustomer=idcustomer)
        if 1 == sldatetrans:
            start_date = datetime.strptime(request.POST.get('date'), '%m/%d/%Y').date()
            end_date = datetime.strptime(request.POST.get('second_date'), '%m/%d/%Y').date()
            payable = main_query.filter(datetrans__range=(start_date, end_date))
        if 2 == sldatetrans:
            filter_date = request.POST.get('date').split('/')
            year = filter_date[1]
            month = filter_date[0]
            payable = main_query.filter(datetrans__year__gte=year, datetrans__month=month, datetrans__year__lte=year)
        if 3 == sldatetrans:
            filter_year = request.POST.get('date')
            payable = main_query.filter(datetrans__year=filter_year)
        if 0 == sldatetrans:
            year = date.today().year
            payable = main_query.filter(datetrans__year=year)
        payable_json = json.dumps(list(payable), cls=DjangoJSONEncoder)
        sum_cash = payable.filter(typepaycost='Cash').aggregate(cost_s=Sum('cost'))
        sum_check = payable.filter(typepaycost='Check').aggregate(cost_s=Sum('cost'))
        sum_credit_card = payable.filter(typepaycost='Credit Card').aggregate(cost_s=Sum('cost'))
        total_amount = payable.aggregate(amount_s=Sum('amount'))
        total_cost = payable.aggregate(cost_s=Sum('cost'))
        return JsonResponse({'payable': payable_json, 'cash': sum_cash['cost_s'], 'check': sum_check['cost_s'],
                             'credit_card': sum_credit_card['cost_s'], 'total_amount': total_amount['amount_s'],
                             'total_cost': total_cost['cost_s']}, safe=False)


@login_required(login_url='Procedure:login')
def random(request):
    query = "SELECT c.idcustomer, c.cusname, c.dotclient, c.clientstatus, d.nombre, d.status, d.nombre, d.phone, CONCAT_WS('','***-**-', SUBSTRING(d.ssn, 8, 10)) AS ssn_k FROM customers c LEFT JOIN drivers d ON c.idcustomer=d.idcustomer WHERE (c.clientstatus='Active' AND c.dotclient=True AND d.status='Active' AND d.random_test=true) OR (c.clientstatus='Active' AND c.dotclient=True AND d.random_test IS NULL) ORDER BY c.idcustomer DESC ;"
    drivers = Customers.objects.raw(query)
    count_drivers = len(drivers)
    year = datetime.today().year
    num_alcohol = RandomTest.objects.filter(year=year, type='Alcohol').count()
    percentage_alcohol = (num_alcohol * 100) / count_drivers
    num_substances = RandomTest.objects.filter(year=year, type='Controlled Substances').count()
    percentage_substances = (num_substances * 100) / count_drivers
    if request.method == 'GET':
        return render(request, 'Procedure/Reports/random.html', {'total_drivers': count_drivers,
                                                                 'alcohol': {'num': num_alcohol,
                                                                             'percentage': percentage_alcohol},
                                                                 'substances': {'num': num_substances,
                                                                                'percentage': percentage_substances}})
    if request.method == 'POST':
        year = request.POST.get('year')
        quarter = request.POST.get('quarter')
        random = RandomTest.objects.filter(year=year, quarter=quarter, type='Controlled Substances').annotate(
            customer=Concat('idcustomer_id', V('-'), 'idcustomer__cusname', output_field=CharField())).only(
            'year', 'quarter', 'iddriver', 'idcustomer_id', 'idcustomer__cusname',
            'idcustomer__mobile1', 'iddriver__status', 'idcustomer__clientstatus')
        sustances = list()
        for sustance in random:
            if sustance.iddriver:
                sustances.append({0: sustance.iddriver.nombre, 1: sustance.iddriver.phone, 2: sustance.customer,
                                  3: sustance.idcustomer.mobile1, 4: sustance.iddriver.status,
                                  5: sustance.idcustomer.clientstatus})
            else:
                sustances.append({0: '', 1: '', 2: sustance.customer,
                                  3: sustance.idcustomer.mobile1, 4: '',
                                  5: sustance.idcustomer.clientstatus})
        random_alcohol = RandomTest.objects.filter(year=year, quarter=quarter, type='Alcohol').annotate(
            customer=Concat('idcustomer_id', V('-'), 'idcustomer__cusname', output_field=CharField())).only(
            'year', 'quarter', 'iddriver', 'idcustomer_id', 'idcustomer__cusname',
            'idcustomer__mobile1', 'iddriver__status', 'idcustomer__clientstatus')
        alcohol = list()
        for alcohol_test in random_alcohol:
            if alcohol_test.iddriver:
                alcohol.append(
                    {0: alcohol_test.iddriver.nombre, 1: alcohol_test.iddriver.phone, 2: alcohol_test.customer,
                     3: alcohol_test.idcustomer.mobile1, 4: alcohol_test.iddriver.status,
                     5: sustance.idcustomer.clientstatus})
            else:
                alcohol.append(
                    {0: '', 1: '', 2: alcohol_test.customer,
                     3: alcohol_test.idcustomer.mobile1, 4: '',
                     5: sustance.idcustomer.clientstatus})
        result: JsonResponse = JsonResponse({'sustances': sustances, 'alcohol': alcohol,
                                             'total_alcohol': {'num': num_alcohol, 'percentage': percentage_alcohol},
                                             'total_substances': {'num': num_substances,
                                                                  'percentage': percentage_substances}})
        return result


@login_required(login_url='Procedure:login')
def add_random(request):
    if request.method == 'POST':
        year = request.POST.get('year')
        quarter = int(request.POST.get('quarter'))
        try:
            main_query = "SELECT c.idcustomer, d.iddriver FROM customers c LEFT JOIN drivers d ON c.idcustomer=d.idcustomer WHERE (c.clientstatus='Active' AND c.dotclient=True AND d.status='Active' AND d.random_test=true) OR (c.clientstatus='Active' AND c.dotclient=True AND d.random_test IS NULL)"
            query = main_query + " ORDER BY c.idcustomer DESC ;"
            drivers = Customers.objects.raw(query)
            count_drivers = len(drivers)
            # drivers = Drivers.objects.filter(status='Active', idcustomer__clientstatus='Active', idcustomer__dotclient='Yes').count()
            percentage = (75 / 100)
            tests = round(count_drivers * (percentage / 4))
            if quarter == 4:
                current_number_tests = RandomTest.objects.filter(year=year, type='Controlled Substances').count()
                tests = round(count_drivers * percentage) - current_number_tests
            # Controlled Substances
            query = main_query + "ORDER BY RAND() ASC LIMIT %s" % tests
            drivers = Customers.objects.raw(query)
            for driver in drivers:
                idcustomer = Customers.objects.only('idcustomer').get(pk=driver.idcustomer)
                if driver.iddriver:
                    iddriver = Drivers.objects.only('iddriver').get(pk=driver.iddriver)
                    randomtest = RandomTest(iddriver=iddriver, idcustomer=idcustomer, year=year, quarter=quarter,
                                            type='Controlled Substances', random_drivers=count_drivers)
                else:
                    randomtest = RandomTest(idcustomer=idcustomer, year=year, quarter=quarter,
                                            type='Controlled Substances', random_drivers=count_drivers)
                randomtest.save()
            # Alcohol
            percentage = (30 / 100)
            tests = round(count_drivers * (percentage / 4))
            if quarter == 4:
                current_number_tests = RandomTest.objects.filter(year=year, type='Alcohol').count()
                tests = round(count_drivers * percentage) - current_number_tests
            query = main_query + "ORDER BY RAND() ASC LIMIT %s" % tests
            drivers = Customers.objects.raw(query)
            for driver in drivers:
                idcustomer = Customers.objects.only('idcustomer').get(pk=driver.idcustomer)
                if driver.iddriver:
                    iddriver = Drivers.objects.only('iddriver').get(pk=driver.iddriver)
                    randomtest = RandomTest(iddriver=iddriver, idcustomer=idcustomer, year=year, quarter=quarter,
                                            type='Alcohol', random_drivers=count_drivers)
                else:
                    randomtest = RandomTest(idcustomer=idcustomer, year=year, quarter=quarter, type='Alcohol',
                                            random_drivers=count_drivers)
                randomtest.save()
            message = {'description': 'New Random add', 'type': 'success'}
            result = JsonResponse({'message': message})
            status = 200
        except Exception as e:
            print(e)
            message = {'description': 'Error when generate Random pool', 'type': 'error'}
            result = JsonResponse({'message': message})
            status = 500
        return HttpResponse(result, content_type='application/json', status=status)


class CardView(View):

    def get(self, request, *args, **kwargs):
        form = CardsForm()
        customer = Customers.objects.only('idcustomer', 'cusname', 'mobile1', 'mobile2').get(
            idcustomer=kwargs["customer_id"])
        cards = Cards.objects.filter(idcustomer=kwargs["customer_id"])
        return render(request, "Procedure/Customers/Cards/cards.html",
                      {'form': form, 'cusname': customer.cusname, 'customer_id': customer.idcustomer, 'cards': cards,
                       'customer': customer})

    def post(self, request, *args, **kwargs):
        form = CardsForm(request.POST)
        if form.is_valid():
            try:
                cards = form.save()
                status = 200
                message = {'description': 'Cards saved successfully', 'type': 'success'}
                result = JsonResponse({'message': message, 'card': {'idcard': cards.idcard}})
            except Exception as e:
                print(e)
                message = {'description': 'Error while saving', 'type': 'error'}
                status = 500
                result = JsonResponse({'message': message})
        else:
            errors = form.errors
            result = JsonResponse({'message': 'Validation', 'fields': errors})
            status = 400
        return HttpResponse(result, content_type='application/json', status=status)

    def patch(self, request, *args, **kwargs):
        field = kwargs['field']
        card_id = kwargs['card_id']
        params = json.loads(request.body)
        value = True if params[field] == 'False' else False
        try:
            if ("customer_id" in params.keys()) and value:
                Cards.objects.filter(idcustomer=params['customer_id'], last_used=True).update(last_used=False)
            if "status" in params.keys():
                value = 'Inactive' if params[field] == 'Active' else 'Active'
            card = Cards.objects.filter(idcard=card_id)
            field_update = {field: value}
            card.update(**field_update)
            result = JsonResponse({'message': {'description': 'Field {0} updated'.format(field), 'type': 'success'},
                                   "field": field_update})
            status = 200
        except Exception as e:
            print(e)
            result = JsonResponse({'message': {'description': 'Internal Server error', 'type': 'error'}})
            status = 500
        return HttpResponse(result, content_type='application/json', status=status)

    def put(self, request, *args, **kwargs):
        params = json.loads(request.body)
        card_id = json.load(request)['idcard'];
        cards = Cards.objects.get(pk=card_id)
        form = CardsForm(params, instance=cards)
        try:
            if form.is_valid():
                form.save()
                card = form.cleaned_data
                card["idcard"] = card_id
                result = JsonResponse(
                    {'message': {'description': 'Update Successfully', 'type': 'success'}, "card": card})
                status = 200
            else:
                errors = form.errors
                result = JsonResponse({'message': 'Validation', 'fields': errors})
                status = 400
        except Exception as e:
            print(e)
            result = JsonResponse({'message': {'description': 'Internal Server error', 'type': 'error'}})
            status = 500

        return HttpResponse(result, content_type='application/json', status=status)


@login_required(login_url='Procedure:login')
def list_cards(request, customer_id):
    if request.method == 'GET':
        form = CardsForm()
        customer = Customers.objects.only('idcustomer', 'cusname', 'mobile1', 'mobile2').get(
            idcustomer=customer_id)
        cards = Cards.objects.filter(idcustomer=customer_id, status='Active')
        return render(request, "Procedure/Customers/Cards/cards.html",
                      {'form': form, 'cusname': customer.cusname, 'customer_id': customer.idcustomer, 'cards': cards,
                       'customer': customer})


@login_required(login_url='Procedure:login')
def add_cards(request):
    if request.method == 'POST':
        form = CardsForm(request.POST)
        if form.is_valid():
            try:
                cards = form.save()
                status = 200
                message = {'description': 'Cards saved successfully', 'type': 'success'}
                card = {'idcard': cards.idcard, 'idcustomer': cards.idcustomer, 'type': cards.type,
                        'cardno': cards.cardno, 'expdate': cards.expdate, 'csc': cards.csc, 'zipcode': cards.zipcode}
                result = JsonResponse({'message': message, 'card': card})
            except Exception as e:
                print(e)
                message = {'description': 'Error while saving', 'type': 'error'}
                status = 500
                result = JsonResponse({'message': message})
        else:
            print(form.errors.as_data)
            errors = form.errors.as_json(escape_html=False)
            result = JsonResponse({'errors': errors})
            status = 500
        return HttpResponse(result, content_type='application/json', status=status)


def upgrade_cards(request):
    if request.method == 'GET':
        cards = Cards.objects.all()
        for card in cards:
            cardno = card.cardno
            card.cardno = cardno
            card._cardno_data = cardno
            card.save()
        return HttpResponseRedirect('/Procedure/index/')


@login_required(login_url='Procedure:login')
def edit_cards(request):
    if request.method == 'POST':
        form = CardsForm(request.POST)
        if form.is_valid():
            try:
                idcard = request.POST.get('idcard')
                cards = Cards.objects.get(pk=idcard)
                cards.type = form.cleaned_data['type']
                cards.cardno = form.cleaned_data['cardno']
                cards._cardno_data = form.cleaned_data['_cardno_data']
                cards.expdate = form.cleaned_data['expdate']
                cards.csc = form.cleaned_data['csc']
                cards.zipcode = form.cleaned_data['zipcode']
                cards.save()
                status = 200
                message = {'description': 'Cards saved successfully', 'type': 'success'}
                card = {'idcard': cards.idcard, 'idcustomer': cards.idcustomer, 'type': cards.type,
                        'cardno': cards.cardno, '_cardno_data': cards._cardno_data, 'expdate': cards.expdate,
                        'csc': cards.csc, 'zipcode': cards.zipcode}
                result = JsonResponse({'message': message, 'card': card})
            except Exception as e:
                print(e)
                message = {'description': 'Error while Updating', 'type': 'error'}
                status = 500
                result = JsonResponse({'message': message})
        else:
            print(form.errors.as_data)
            status = 500
            message = {'description': 'Check Fields', 'type': 'warning'}
            result = JsonResponse({'message': message})
        return HttpResponse(result, content_type='application/json', status=status)


@login_required(login_url='Procedure:login')
def delete_cards(request, card_id):
    if request.method == 'POST':
        try:
            status_text = 'Active' if request.POST.get('status') == 'Inactive' else 'Inactive'
            Cards.objects.filter(idcard=card_id).update(status=status_text)
            message = {'description': 'Cards removed successfully', 'type': 'success'}
            result = JsonResponse({'message': message, 'status': status_text})
            status = 200
        except Exception as e:
            print(e)
            message = {'description': 'Error while removing', 'type': 'error'}
            status = 500
            result = JsonResponse({'message': message})
        return HttpResponse(result, content_type='application/json', status=status)


@login_required(login_url='Procedure:login')
def list_credits(request, show_all):
    if request.method == 'GET':
        if show_all:
            credits = Credits.objects.all()
        else:
            credits = Credits.objects.all().filter(status='Unpaid')
        status = ['Paid', 'Unpaid']
        return render(request, "Procedure/Accounting/credits.html",
                      {'credits': credits,
                       'status_p': status, 'showAll': show_all})


@login_required(login_url='Procedure:login')
def paid_credit(request):
    if request.method == 'POST':
        status_credit = str(request.POST.get('status'))
        idcredits = request.POST.getlist('idcredits[]')
        try:
            credits_list = list()
            for idcredit in idcredits:
                credit = int(idcredit)
                Credits.objects.filter(idcredit=credit).update(status=status_credit)
                c = Credits.objects.only('idcredit', 'status').get(pk=credit)
                credits_list.append({'id': c.idcredit, 'status': c.status})

            message = {'description': 'Credit update succesfully', 'type': 'success'}
            result = JsonResponse({'message': message, 'data': credits_list})
            status = 200
        except Exception as e:
            print(e)
            message = {'description': 'Error while updating the credit' + str(e), 'type': 'error'}
            status = 500
            result = JsonResponse({'message': message})
        return HttpResponse(result, content_type='application/json', status=status)


@login_required(login_url='Procedure:login')
def upload_receipts_fuel_taxes(request, idcustomer):
    if request.method == 'GET':
        unit = Units.objects.all().filter(idcustomer=idcustomer, status='Active', delete=False).only('nounit')
        form = UploadReceipts()
        return render(request, 'Procedure/Customers/Fuel_Taxes/upload_receipts.html',
                      {'customer_id': idcustomer, 'unit': unit, 'form': form})
    if request.method == 'POST':
        form = UploadReceipts(request.POST, request.FILES)
        if form.is_valid():
            errors_list = list()
            excel_file = form.cleaned_data['excel_file']
            wb = openpyxl.load_workbook(excel_file)
            worksheet = wb['Quarter']
            for row in worksheet.iter_rows(min_row=2, max_col=4):
                try:
                    receipts = Recive()
                    validate = True
                    field_date = datetime.strptime(str(row[0].value), '%Y-%m-%d %H:%M:%S')
                    quarter = form.cleaned_data['quarter']
                    if quarter == '1' and field_date.month > 3:
                        validate = False
                        errors_list.append('The date {} does not belongs to the select quarter'.format(
                            field_date.strftime('%m/%d/%Y')))
                        print('The date does not belongs to the select quarter')
                    if quarter == '2' and (field_date.month > 6 or field_date.month <= 3):
                        validate = False
                        errors_list.append('The date {} does not belongs to the select quarter'.format(
                            field_date.strftime('%m/%d/%Y')))
                        print('The date does not belongs to the select quarter')
                    if quarter == '3' and (field_date.month > 9 or field_date.month <= 6):
                        validate = False
                        errors_list.append('The date {} does not belongs to the select quarter'.format(
                            field_date.strftime('%m/%d/%Y')))
                        print('The date does not belongs to the select quarter')

                    if quarter == '4' and (field_date.month <= 9):
                        validate = False
                        errors_list.append('The date {} does not belongs to the select quarter'.format(
                            field_date.strftime('%m/%d/%Y')))
                        print('The date does not belongs to the select quarter')
                    try:
                        state = States.objects.only('codestate').get(codestate=row[2].value)
                    except Exception as e:
                        validate = False
                        errors_list.append('State {} not found'.format(row[2].value))
                        print('State not found')
                    if validate:
                        receipts.idcustomer = Customers.objects.only('idcustomer').get(pk=idcustomer)
                        receipts.idunit = form.cleaned_data['idunit']
                        receipts.year = form.cleaned_data['year']
                        receipts.quarter = form.cleaned_data['quarter']
                        receipts.miles = float(row[3].value) * 5
                        receipts.date = datetime.strptime(str(row[0].value), '%Y-%m-%d %H:%M:%S')
                        receipts.state = state.codestate
                        receipts.zip = row[1].value if row[1].value else None
                        receipts.gallons = row[3].value
                        receipts.save()
                except Exception as e:
                    print(e)
                    pass
                # row[0].font = Font(color="00FF0000")
            # wb.save('C:/Users/danny/Downloads/guardado.xlsx')
            status = 200
            result = JsonResponse({'status': True, 'errors': errors_list})
        else:
            errors = form.errors.as_json(escape_html=False)
            result = JsonResponse({'errors': errors})
            status = 500
        return HttpResponse(result, content_type='application/json', status=status)
    return None


@login_required(login_url='Procedure:login')
def get_file(request, name):
    file_name = settings.TEMPLATE_EXCEL + '/{0}'.format(name)
    tmp = open(file_name, 'rb')
    return FileResponse(tmp)


def receive_summary(idcustomer, idunit, year, quarter):
    try:
        first_month = ()
        second_month = ()
        third_month = ()
        if 1 == quarter:
            first_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=1).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
            second_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=2).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
            third_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=3).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
        if 2 == quarter:
            first_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=4).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
            second_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=5).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
            third_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=6).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
        if 3 == quarter:
            first_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=7).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
            second_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=8).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
            third_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=9).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
        if 4 == quarter:
            first_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=10).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
            second_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                 date__month=11).values("state").annotate(mile=Sum("miles")).annotate(
                gallon=Sum("gallons")).order_by('state')
            third_month = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=12).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons")).order_by('state')
    except Exception as e:
        print(e)
    return [first_month, second_month, third_month]


def get_state_zipcode(request):
    if  request.method == 'GET':
        zipcode = request.GET['zipcode']
        try:
            if zipcodes.is_real(zipcode):
                postalcode = zipcodes.matching(zipcode).__getitem__(0)
                return JsonResponse({'postalcode': postalcode, 'status': True})
            else:
                return JsonResponse({'error': 'This zipcode is wrong', 'status': False})
        except Exception as e:
            print(e)
            return JsonResponse({'error': '', 'status': False})


@login_required(login_url='admin:login')
def update_state_customers(request):
    if request.method == 'GET':
        customers = Customers.objects.all()
        for customer in customers:
            zipcode = str(customer.codepostal)
            try:
                zip = zipcodes.matching(zipcode.strip()).__getitem__(0)
                if customer.state != zip['state']:
                    city = str(zip['city'])
                    county = str(zip['county'])
                    state = str(zip['state'])
                    print('{0}-{1}-{2}'.format(city, county, state))
                    Customers.objects.filter(idcustomer=customer.idcustomer).update(county=county, state=state,
                                                                                    city=city)
            except Exception as e:
                print(e)
                pass
        return HttpResponse({'Finished'})


@login_required(login_url='Procedure:login')
def update_dot(request):
    if request.method == 'POST':
        try:
            json_data = json.load(request)
            if not (json_data.get('customer_id') is None):
                customer_id = json_data["customer_id"]
                customer = Customers.objects.only('dotid', 'dotidexp').get(idcustomer=customer_id)
                result = queryDOT(customer.dotid)
                if result['status'] == 'ok':
                    customer.dotidexp = result['expiration']
                    customer.save()
                    return MessageResponse(data={
                        'datedot': datetime.strptime(result['expiration'], '%Y-%m-%d').strftime('%m/%d/%Y')
                    }, description='Data had get successfully').success()
                else:
                    return MessageResponse(description=result['message']).error()
            else:
                dot_id = json_data["dotid"]
                result = queryDOT(dot_id, True)
                if result['status'] == 'ok':
                    company = result['company']
                    data = {
                        'legal_name': company.legal_name, 'physical_address': company.physical_address,
                        'datedot': company.mcs_150_form_date.strftime('%m/%d/%Y'), 'phone': company.phone_number,
                        'mc': company.mc_mx_ff_numbers
                    }
                    return MessageResponse(data=data, description='Data was got successfully').success()
                else:
                    return MessageResponse(description='%s'%result['message']).error()
        except Exception as e:
            print("DOT UPDATE:%s"%e)
            return MessageResponse(description=f'{e}').error()


def update_idinvoice(request):
    projects = Projects.objects.all()
    try:
        for project in projects:
            print("%s - %s" % (project.idinvoicedet.code, project.idinvoicedet.service))
            project.invoice = project.idinvoicedet.idinvoice

            project.service_id = Services.objects.get(idservice=project.idinvoicedet.code)
            project.save()
        return HttpResponse('Finished...')
    except Exception as e:
        print(e)
        return HttpResponse('errors')


class CustomerFilesView(View):
    template = 'Procedure/Customers/Files/list.html'

    def get(self, request, *args, **kwargs):
        if kwargs['idcustomer'] != 0:
            customer = Customers.objects.only('idcustomer', 'cusname', 'mobile1', 'mobile2').get(
                pk=kwargs['idcustomer'])
            data = {'customer_id': kwargs['idcustomer'], 'customer': customer}
        else:
            data = {}
            self.template = 'Procedure/File/file_explorer.html'
        return render(request, self.template, data)

    def post(self, request, *args, **kwargs):
        form = CustomerFilesForm(request.POST, request.FILES)
        if kwargs['customer_id'] == 0:
            try:
                if request.POST['folder']:
                    filename = request.FILES['path'].name
                    file_format = filename.split('-')
                    customer_file = Customer_Files()
                    customer_file.customer = Customers.objects.get(idcustomer=file_format[0])
                    customer_file.folder = request.POST['folder']
                    customer_file.filename = filename
                    customer_file.path = request.FILES['path']
                    customer_file.uploaded_by = request.user
                    validate = Customer_Files.objects.filter(filename=filename, erased=False).count()
                    if validate == 0:
                        customer_file.save()
                        response = JsonResponse({'description': 'Save success', 'type': 'success'})
                        status = 200
                    else:
                        errors = form.errors.as_json(escape_html=False)
                        print(errors)
                        response = JsonResponse({'description': 'File name already exists', 'type': 'error'})
                        status = 500
                else:
                    status = 500
                    response = JsonResponse({'description': {"folder": "This field is required"}, 'type': 'warning'})
                return HttpResponse(response, content_type='application/json', status=status)
            except Exception as ex:
                print(ex)
                response = JsonResponse({'description': '{}'.format(ex), 'type': 'error'})
                return HttpResponse(response, content_type='application/json', status=500)

        if form.is_valid():
            try:
                filename = form.cleaned_data['path']
                customer_files = form.save(commit=False)
                customer_files.filename = filename
                form.cleaned_data['filename'] = filename
                validate = Customer_Files.objects.filter(filename=filename, erased=False).count()
                if validate == 0:
                    customer_files.save()
                    response = JsonResponse({'description': 'Save success', 'type': 'success'})
                    status = 200
                else:
                    response = JsonResponse({'description': 'File name already exists', 'type': 'error'})
                    status = 500
                return HttpResponse(response, content_type='application/json', status=status)
            except Exception as ex:
                print(ex)
                response = JsonResponse({'description': '{}'.format(ex), 'type': 'error'})
                return HttpResponse(response, content_type='application/json', status=500)
        else:
            errors = form.errors.as_json(escape_html=False)
            print(errors)
            return HttpResponse(JsonResponse({'description': errors, 'type': 'warning'}),
                                content_type='application/json', status=500)

    # @permission_required("Procedure.delete_customer_files", login_url="Procedure:index")
    def delete(self, request, *args, **kwargs):
        try:
            files_id = kwargs['id']
            customers_files = Customer_Files.objects.get(pk=files_id)
            customers_files.erased = True
            # filename = customers_files.filename + '.delete'
            # customers_files.filename = filename
            initial_path = customers_files.path.path
            # new_path = '{0}.delete'.format(initial_path)
            new_path = '{0}/.trash/customers/{1}/{2}/'.format(settings.MEDIA_ROOT, customers_files.customer_id,
                                                              customers_files.folder)
            # os.renames(initial_path, new_path)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            shutil.move(initial_path, new_path)
            # customers_files.path.name = customers_files.path.name + '.delete'
            customers_files.erased_file_date = timezone.now()
            customers_files.erased_by = request.user
            customers_files.save()
            status = 200
            data = JsonResponse({'description': 'Successfully removed', 'type': 'success'})
        except Exception as e:
            print(e)
            status = 500
            data = JsonResponse({'description': str(e), 'type': 'error'})
        return HttpResponse(data, content_type='application/json', status=status)


class NewsView(View):
    template = 'Procedure/Configuration/News/list.html'

    def get(self, request, *args, **kwargs):
        news = News.objects.all()
        return render(request, self.template, {'news': news})


@login_required(login_url='Procedure:login')
def certificate_random_test(request):
    path_template = settings.TEMPLATES_PDF + '/CERTIFICADO_DRIVERS_RANDOM.docx'
    doc = DocxTemplate(path_template)


class TaskView(View):
    template = 'Procedure/Tasks/task-modal.html'
    action = ''

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if self.action == 'Add':
                return self.get(request, *args, **kwargs)
            if self.action == 'List':
                return self.list(request, *args, **kwargs)
            if self.action == 'Project':
                return self.project(request, *args, **kwargs)
            if self.action == 'Details':
                return self.details(request, *args, **kwargs)

        elif request.method == 'POST':
            if self.action == 'Add':
                return self.post(request, *args, **kwargs)
            elif self.action == 'is-completed':
                return self.task_completed(request, *args, **kwargs)
            elif self.action == 'archive-task':
                return self.archive_task(request, *args, **kwargs)
        else:
            return super().dispatch(*args, **kwargs)

    # show form
    def get(self, request, *args, **kwargs):
        form = TaskForm()
        users = User.objects.filter(is_active=True).only('id', 'fullname')
        url = "/Procedure/tasks/add/"
        if 'project_id' in kwargs:
            url = "/Procedure/tasks/add/%s" % (kwargs['project_id'])
            return render(request, self.template, {'form': form, 'users': users, 'project_id': kwargs['project_id'], 'url': url})
        return render(request, self.template, {'form': form, 'users': users, 'url': url})

    def project(self, request, *args, **kwargs):
        project_id = int(kwargs["project_id"])
        tasks = Task.objects.filter(project__idproject=project_id, archived=False)
        print('project')
        return render(request, 'Procedure/Tasks/list.html', {'tasks': tasks, 'is_calendar': 0, "project_id": project_id})

    # list tasks
    def list(self, request, *args, **kwargs):
        user_tasks = self.user_tasks(request)
        is_calendar = kwargs['is_calendar']
        request.session['total_tasks'] = user_tasks.count()
        result = {'tasks': user_tasks, 'today': datetime.today().strftime("%m/%d/%Y"), 'is_calendar': is_calendar}
        return render(request, self.template, result)

    def details(self, request, *args, **kwargs):
        if 'task_id' in kwargs:
            task = Task.objects.get(id=kwargs['task_id'])
            return render(request, self.template, {'task': task})

    @staticmethod
    def user_tasks(request):
        return Task.objects.filter( Q(created_by=request.user.id, is_completed=False) | Q(assigned_to=request.user.id, is_completed=False)).filter(archived=False)


    # add task
    def post(self, request, *args, **kwargs):
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                task = Task()
                if 'project_id' in kwargs:
                    project = Projects.objects.get(idproject=kwargs['project_id'])
                    task.project = project
                task.title = form.cleaned_data['title']
                task.description = form.cleaned_data['description']
                task.priority = form.cleaned_data['priority']
                task.due_date = form.cleaned_data['due_date']
                task.created_by = request.user
                task.save()
                if form.cleaned_data['to_assign'] != '0':
                    task.assigned_to.add(User.objects.get(id=form.cleaned_data['to_assign']))
                if 'project_id' not in kwargs:
                    return MessageResponse(data={
                        'id': 'T-%s'%task.id,
                        'title': task.title,
                        'start': task.created_at,
                        'backgroundColor': '#347474',
                        'borderColor': '#347474',
                        'groups': 'group3'
                    }, description="Successfully saved").success()
                tasks = Task.objects.filter(project=project, archived=False)
                number_tasks = tasks.count()
                project.tasks_number = number_tasks
                complete_tasks = tasks.filter(is_completed=True).count()
                project.tasks_completed = complete_tasks
                project.save()
                percentage = round((complete_tasks * 100) / number_tasks, 2)
                data = JsonResponse({'message': {'description': 'Successfully registered', 'type': 'success'},
                                     'percentage': percentage})
                return HttpResponse(data, content_type='application/json', status=200)
            except Exception as e:
                print(e)
        else:
            errors = form.errors.as_json(escape_html=False)
            print(errors)
            result = JsonResponse({'errors': errors})
            return HttpResponse(result, content_type='application/json', status=500)
        return HttpResponse({}, content_type='application/json', status=200)


    # update task completed
    def task_completed(self, request, *args, **kwargs):
        try:
            is_completed = True if request.POST.get('is_completed') == 'true' else False
            task = Task.objects.get(id=kwargs['task_id'])
            task.is_completed = is_completed
            task.completed_by = request.user
            task.completed_at = timezone.now()
            task.save()
            percentage = 0
            if task.project:
                tasks = Task.objects.filter(project=task.project, archived=False)
                tasks_number = tasks.count()
                task_completed = tasks.filter(is_completed=True).count()
                task.project.tasks_number = tasks_number
                task.project.tasks_completed = task_completed
                task.project.save()
                percentage = round((task_completed * 100) / tasks_number, 2)

            if is_completed:
                type = 'success'
                description = 'Task completed'
            else:
                type = 'error'
                description = 'Task no completed'
            return HttpResponse(JsonResponse({"percentage": percentage, "message": {"type": type, "description": description}}), content_type='application/json', status=200)
        except Exception as e:
            print(e)
            return HttpResponse(JsonResponse({"message": {"type": 'error', 'description': 'Internal server error'}}),
                                content_type='application/json', status=500)

    # delete task
    def archive_task(self, request, *args, **kwargs):
        try:
            task = Task.objects.get(id=request.POST.get("id"))
            task.archived = True
            task.archived_by = request.user
            task.archived_at = timezone.now()
            task.save()
            percentage = 0
            if task.project:
                tasks = Task.objects.filter(project=task.project, archived=False)
                tasks_number = tasks.count()
                tasks_completed = tasks.filter(is_completed=True).count()
                task.project.tasks_number = tasks_number
                task.project.tasks_completed = tasks_completed
                task.project.save()
                percentage = round((tasks_completed * 100) / tasks_number, 2) if tasks_number != 0 else 0
            return HttpResponse(JsonResponse({"percentage": percentage, "archived": True, "task_id": task.id, "message": {"description": "Task deleted", "type": "success"}}),
                                content_type="application/json", status=200)
        except Exception as e:
            print(e)
            return HttpResponse(JsonResponse({"message": {"type": 'error', 'description': 'Internal server error'}}),
                                content_type='application/json', status=500)


@login_required(login_url='Procedure:login')
def do_fuel_taxes(request, customer_id):
    if request.method == 'POST':
        try:
            customer = Customers.objects.get(idcustomer=customer_id)
            customer.fuel_taxes = json.load(request)['fuel_taxes']
            customer.save()
            return JsonResponse({'message': 'Success update', 'type': 'success'})
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Internal Server Error', 'type': 'error'})


def add_note(request):
    query = "SELECT c.idcustomer FROM customers c WHERE c.clientstatus='Active' and c.anreport < 2024 and c.anreport not in ('N/A', 'NA', 'FICN', '', 'INAC','INACTIVE')"
    customers = Customers.objects.raw(query)
    html = '<table>'
    for customer in customers:
        cus=Customers.objects.get(idcustomer=customer.idcustomer)
        note = Notes(idcustomer=cus, fullname='Daniel Cuatin', created_at='2023-04-28', note='Se envio mensaje de whatsapp y email notificando annual report', iduser=request.user)
        note.save()
        html += '<tr><td>%s</td></tr>' % customer.idcustomer
    html + '</table>'
    return HttpResponse(html)

class ServicesView(View):
    template = 'Procedure/Configuration/Services/'
    model = Services
    
    def get(self, request, *args, **kwargs):
        
        return render(request, "Procedure/Configuration/Services/list.html", {})