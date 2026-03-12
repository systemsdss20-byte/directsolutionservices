import datetime

from ajax_datatable import AjaxDatatableView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.template.loader import render_to_string

from ..Accounting.models import Commission_Value
from .models import Invoice_det, Invoices, Customer_Files, News, Services, Units, Drivers, Email_Log, Cards, Customers


class CardsDatatable(AjaxDatatableView):
    model = Cards
    initial_order = [['idcard', 'desc']]
    search_values_separator = '+'
    column_defs = []
    permits = {}

    def get_column_defs(self, request):
        self.permits = {
            'edit': request.user.has_perm('Procedure.change_cards'),
            'delete': request.user.has_perm('Procedure.delete_cards')
        }
        self.column_defs = [
            {'name': 'last_used', 'title': 'Last Used', 'searchable': False, 'orderable': False},
            {'name': 'idcard', 'title': 'No', 'visible': True, 'searchable': True},
            {'name': 'type'},
            {'name': 'cardno'},
            {'name': 'expdate'},
            {'name': 'csc'},
            {'name': 'zipcode'},
            {'name': 'status', 'title': '', 'visible': True, 'searchable': False, 'orderable': True,},
            {'name': 'edit', 'title': '', 'visible': True, 'searchable': False, 'orderable': False,}
        ]
        return self.column_defs

    def customize_row(self, row, obj):
        row['last_used'] = '<button class="btn btn-sm {0}" onclick="btnLastUsed(this, {1});" value="{2}">Las Used</button>'.format('btn-primary' if obj.last_used else 'btn-white', obj.idcard, obj.last_used)
        row['status'] = '<button class="btn remove btn-sm btn-outline-{0}" onclick="btnStatus(this, {1});">{2}</button>'.format('success' if obj.status == 'Active' else 'danger', obj.idcard, obj.status)
        row['edit'] = '<button id="{0}" class="edit btn btn-sm btn-pill btn-warning" onclick="fn_edit_row(this.closest(\'tr\'))"><i class="fa fa-edit"></i>&nbsp;Edit</button>'.format(obj.idcard)


    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request, 'REQUEST', None):
            request.REQUEST = request.GET if request.method == 'GET' else request.POST
        if 'customer_id' in request.REQUEST:
            customer_id = int(request.REQUEST.get('customer_id'))
            queryset = self.model.objects.filter(idcustomer=customer_id)
        return queryset


class UnitsDatatable(AjaxDatatableView):
    model = Units
    code = 'Units'
    initial_order = [['nounit', 'desc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []
    permits = {}

    def get_column_defs(self, request):
        self.permits = {
            'edit': request.user.has_perm('Procedure.change_units'),
            'delete': request.user.has_perm('Procedure.delete_units'),
            'view': request.user.has_perm('Procedure.view_units')
        }
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'pk', 'visible': False, 'searchable': False},
            {
                'name': 'idcustomer', 'foreign_field': 'idcustomer__idcustomer', 'title': 'CUSTOMER ID',
                'visible': True if 'customer_id' not in request.REQUEST else False,
                'searchable': True if 'customer_id' not in request.REQUEST else False
            },
            {
                'name': 'cusname', 'foreign_field': 'idcustomer__cusname', 'title': 'CUSTOMER NAME',
                'visible': True if 'customer_id' not in request.REQUEST else False,
                'searchable': True if 'customer_id' not in request.REQUEST else False
            },
            {'name': 'nounit', 'title': 'No Unit', 'visible': True, 'searchable': True, 'width': 20},
            {'name': 'year', 'title': 'Year', 'visible': True, 'searchable': True, 'width': 20},
            {'name': 'type', 'title': 'Type', 'visible': True, 'searchable': True, 'width': 20},
            {'name': 'make', 'title': 'Make', 'visible': True, 'searchable': True, 'width': 20},
            {'name': 'irp', 'title': 'IRP ID/PLATE'},
            {'name': 'vin', 'title': 'VIN', 'visible': True, 'searchable': True},
            {'name': 'title', 'title': 'Title', 'visible': True, 'searchable': True},
            {'name': 'ifta', 'title': 'IFTA', 'visible': True, 'searchable': True},
            {'name': 'status', 'visible': True, 'searchable': False},
            {'name': 'action', 'title': '', 'visible': True, 'searchable': False, 'orderable': False,
             'className': 'actions-buttons'}
        ]
        return self.column_defs

    def customize_row(self, row, obj):
        action_buttons = ''
        row['idcustomer'] = "<a href='/Procedure/customer_edit/{0}/'>{0}</a>".format(obj.idcustomer.idcustomer)
        row['cusname'] = "<a href='/Procedure/customer_edit/{0}/'>{1}</a>".format(obj.idcustomer.idcustomer, obj.idcustomer.cusname)
        if self.permits['view']:
            action_buttons += '<button class="btn btn-sm btn-pill btn-info view" onclick="unit(\'/Procedure/view_unit/{0}\');"><li class="fas fa-eye"></li>&nbsp;View</button>'.format(
                obj.idunit)
        if self.permits['edit']:
            action_buttons += '<button class="btn btn-sm btn-pill btn-warning editar" onclick="unit(\'/Procedure/unit_edit/{0}\');" {1} id="edit-{2}"><li class="fas fa-edit"></li>&nbsp;Edit</button>'.format(
                obj.idunit, 'disabled' if obj.status == 'Inactive' else '', obj.idunit)
        if self.permits['delete']:
            action_buttons += '<button type="button" class="btn btn-sm btn-pill btn-danger" data-toggle="modal" data-target="#modal-danger" onclick="delete_message({0}, \'{1}\')"><li class="fas fa-trash"></li>&nbsp;Delete</button>'.format(
                obj.idunit, obj.nounit)
        row['status'] = '<button id="{0}" onclick="change_status({0})" class="btn btn-sm {1}">{2}</button>'.format(
            obj.idunit, 'btn-outline-success' if obj.status == 'Active' else 'btn-outline-danger', obj.status)
        row['ifta'] = '<span class="badge badge-pill {0}">{1}</span>'.format("bg-success" if obj.ifta else "bg-red", "Yes" if obj.ifta else "No")
        row['action'] = action_buttons

    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request, 'REQUEST', None):
            request.REQUEST = request.GET if request.method == 'GET' else request.POST
        if 'customer_id' in request.REQUEST:
            customer_id = int(request.REQUEST.get('customer_id'))
            queryset = self.model.objects.filter(idcustomer=customer_id, delete=False).order_by("nounit")
        else:
            queryset = self.model.objects.filter(delete=False)
        return queryset

    def render_row_details(self, pk, request=None):
        detail = Units.objects.get(idunit=pk)
        return render_to_string('Procedure/Customers/Unit/detail.html', {'detail': detail})


class DriversDatatable(AjaxDatatableView):
    model = Drivers
    code = 'Drivers'
    initial_order = [['status', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []
    permits = {}

    def get_column_defs(self, request):
        self.permits = {
            'edit': request.user.has_perm('Procedure.change_drivers'),
            # 'delete': request.user.has_perm('Procedure.delete_drivers'),
            'view': request.user.has_perm('Procedure.view_drivers')
        }
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'pk', 'visible': False, 'searchable': False},
            {'name': 'nombre', 'title': 'Nombre', 'visible': True, 'searchable': True, 'orderable': True},
            {'name': 'phone', 'title': 'Phone', 'visible': True, 'searchable': True, 'width': 20},
            {'name': 'ssn', 'title': 'SSN', 'visible': True, 'searchable': True, 'width': 20},
            {'name': 'cdl', 'title': 'CDL', 'visible': True, 'searchable': True},
            {'name': 'cdl_state', 'title': 'CDL STATE', 'visible': True, 'searchable': True, 'width': 10},
            {'name': 'date_of_birth', 'title': 'DATE OF BIRTH', 'visible': True, 'searchable': True},
            {'name': 'preemp', 'title': 'PRE-EMPLOYMENT', 'visible': True, 'searchable': False},
            {'name': 'random_test', 'title': 'RANDOM TEST', 'visible': True, 'searchable': False},
            {'name': 'status', 'visible': True, 'searchable': False},
            {'name': 'action', 'title': '', 'visible': True, 'searchable': False, 'orderable': False,
             'className': 'actions-buttons'}
        ]
        return self.column_defs

    def customize_row(self, row, obj):
        action_buttons = ''

        if self.permits['edit']:
            action_buttons += '<button class="btn btn-sm btn-pill btn-warning editar" onclick="editDriver({0});"><li class="fas fa-edit"></li>&nbsp;Edit</button>'.format(
                obj.pk)
        if self.permits['view']:
            action_buttons += '<button class="btn btn-sm btn-pill btn-success" onclick="show_exams({0});" id="exams-{0}"><li class="fas fa-eye"></li>&nbsp;Tests</button>'.format(obj.pk)

        row['preemp'] = '<span class="badge badge-pill {0}">{1}</span>'.format("bg-success" if obj.preemp else "bg-red",
                                                                             "Yes" if obj.preemp else "No")
        row['random_test'] = '<span class="badge badge-pill {0}">{1}</span>'.format("bg-success" if obj.random_test else "bg-red",
                                                                               "Yes" if obj.random_test else "No")
        row['status'] = '<button id="{0}" onclick="change_status({0})" class="btn btn-sm {1}">{2}</button>'.format(obj.iddriver, 'btn-outline-success' if obj.status == 'Active' else 'btn-outline-danger', obj.status)
        row['action'] = action_buttons

    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request, 'REQUEST', None):
            request.REQUEST = request.GET if request.method == 'GET' else request.POST
        if 'customer_id' in request.REQUEST:
            customer_id = int(request.REQUEST.get('customer_id'))
            queryset = self.model.objects.filter(idcustomer=customer_id)
        return queryset

    def render_row_details(self, pk, request=None):
        detail = Drivers.objects.get(pk=pk)
        return render_to_string('Procedure/Customers/Drivers/detail.html', {'detail': detail})


class SalesDetails(AjaxDatatableView):
    model = Invoices
    code = 'Invoices'
    initial_order = [['invdate', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'pk', 'visible': False, 'searchable': False},
        {'name': 'invdate', 'title': 'Invoice Date', 'visible': True, },
        {'name': 'amount', 'title': 'Amount', 'visible': True, 'searchable': False},
        {'name': 'coments', 'title': 'Comments', 'visible': True, 'searchable': False},
        {'name': 'status', 'title': 'Status', 'visible': True, 'searchable': False},
        {'name': 'customerid', 'foreign_field': 'idcustomer__idcustomer', 'title': 'CUSTOMER ID', 'visible': True,
         'searchable': True},
        {'name': 'cusname', 'foreign_field': 'idcustomer__cusname', 'title': 'CUSTOMER NAME', 'visible': True,
         'searchable': True},
        {'name': 'paid_date', 'title': 'Paid Date', 'visible': True, 'searchable': False},

    ]

    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request, 'REQUEST', None):
            request.REQUEST = request.GET if request.method == 'GET' else request.POST
        if 'user_id' in request.REQUEST:
            user_id = int(request.REQUEST.get('user_id'))
            from_date = datetime.datetime.strptime(request.REQUEST.get('from_date'), '%m/%d/%Y').date();
            to_date = datetime.datetime.strptime(request.REQUEST.get('to_date'), '%m/%d/%Y').date()

            queryset = self.model.objects.filter(
                Q(invdate__range=(from_date, to_date)) | Q(paid_date__range=(from_date, to_date)), iduser=user_id,
                deu=0, status='Paid', deleted=False)
        return queryset

    def customize_row(self, row, obj):
        row['amount'] = "$ %s" % obj.amount
        row['status'] = "<span class='status-icon bg-%s'></span>%s" % (
            'success' if obj.status == 'Paid' else 'danger', obj.status)

    def render_row_details(self, pk, request=None):
        details = Invoice_det.objects.filter(idinvoice=pk, delete=False)
        return render_to_string('Procedure/Customers/Invoices/invoice_details.html', {'details': details})


class InvoicesDatatable(AjaxDatatableView):
    model = Invoices
    code = 'Invoices'
    initial_order = [['pk', 'desc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []

    def get_column_defs(self, request):
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {'name': 'pk', 'title': '#Invoice', 'visible': True, 'searchable': False},
            {'name': 'invdate', 'title': 'Invoice Date', 'visible': True, 'searchable': True, 'lookup_field': 'invdate'},
            {'name': 'amount', 'title': 'Amount', 'visible': True, 'searchable': True},
            {'name': 'fullname', 'foreign_field': 'iduser__fullname', 'title': 'Representative', 'visible': True,
            'searchable': True},
            {'name': 'coments', 'title': 'Comments', 'visible': True, 'searchable': True},
            {'name': 'status', 'title': 'Status', 'visible': True, 'searchable': False},
            {'name': 'email', 'title': 'email', 'visible': request.user.has_perm('Procedure.view_email_loggh'), 'searchable': False},
            {'name': 'view', 'title': '', 'visible': request.user.has_perm('Procedure.view_invoices'),
             'searchable': False, 'orderable': False},
            {'name': 'payments', 'title': '', 'visible': request.user.has_perm('Procedure.view_invoice_paid'),
             'searchable': False, 'orderable': False},
            {'name': 'download', 'title': 'Download', 'visible': request.user.has_perm('Procedure.view_invoices'), 
             'searchable': False, 'orderable': False},
            {'name': 'edit', 'title': '', 'visible': request.user.has_perm('Procedure.change_invoices'),
             'searchable': False, 'orderable': False},
            {'name': 'deleted', 'title': '', 'visible': request.user.has_perm('Procedure.delete_invoices'),
             'searchable': False, 'orderable': False},
        ]
        return self.column_defs

    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request, 'REQUEST', None):
            request.REQUEST = request.GET if request.method == 'GET' else request.POST
        if 'customer_id' in request.REQUEST:
            customer_id = int(request.REQUEST.get('customer_id'))
            queryset = self.model.objects.filter(idcustomer=customer_id, deleted=False).order_by("idinvoice")
        else:
            queryset = self.model.objects.filter(status='Unpaid', deleted=False).order_by('idinvoice')
        
        if 'from_date' in request.REQUEST and 'to_date' in request.REQUEST and request.REQUEST.get('from_date') and request.REQUEST.get('to_date'):
            from_date = datetime.datetime.strptime(request.REQUEST.get('from_date'), '%m/%d/%Y').date()
            to_date = datetime.datetime.strptime(request.REQUEST.get('to_date'), '%m/%d/%Y').date()
            queryset = queryset.filter(invdate__range=(from_date, to_date))
        if 'by_year' in request.REQUEST and request.REQUEST.get('by_year'):
            year = int(request.REQUEST.get('by_year'))
            queryset = queryset.filter(invdate__year=year)
        
        return queryset

    def customize_row(self, row, obj):
        number_emails = Email_Log.objects.filter(invoice_id=obj.idinvoice, sent=True).count()
        text_sent = 'blue' if number_emails else 'red'
        row['amount'] = "$ %s" % round(obj.amount, 2)
        row['status'] = "<span class='status-icon bg-%s'></span>%s" % (
        'success' if obj.status == 'Paid' else 'danger', obj.status)
        row[
            'email'] = "<button %s class='btn btn-sm badge bg-%s'>%s Sent</button>" % (
        'onclick=sent_emails(\"/Procedure/sent_emails/%s\")' % obj.idinvoice if number_emails else '', text_sent, number_emails)
        row[
            'view'] = "<a class='btn btn-sm btn-pill btn-success' href='/Procedure/pdf_invoice/%s'><li class='fa fa-eye'>&nbsp;View</li></a>" % obj.idinvoice
        row['download'] ="<a class='btn btn-sm btn-pill btn-primary' href='/Procedure/get_invoice/%s?download=True'><li class='fa fa-download'>&nbsp;Download</li></a>" % obj.idinvoice
        row[
            'payments'] = '<a class="btn btn-sm btn-pill btn-warning editar" href="/Procedure/paids/%s"><li class="far fa-credit-card"></li>&nbsp;Paids</a>' % obj.idinvoice
        row[
            'edit'] = '<a class="btn btn-sm btn-pill btn-info" href="/Procedure/edit_invoice/%s"><li class="fa fa-pencil"></li></a>' % obj.idinvoice
        row[
            'deleted'] = '<button type="button" class="btn btn-sm btn-pill btn-danger" data-toggle="modal" data-target="#modal-danger" onclick="delete_message({0}, \'{0}\')"><li class="fas fa-trash"></li></button>'.format(
            obj.idinvoice)
            


    def render_row_details(self, pk, request=None):
        details = Invoice_det.objects.filter(idinvoice=pk, delete=False)
        return render_to_string('Procedure/Customers/Invoices/invoice_details.html', {'details': details})


class InvoicesUnpaidDatatable(InvoicesDatatable):
    def get_column_defs(self, request):
        self.column_defs = [
            AjaxDatatableView.render_row_tools_column_def(),
            {
                'name': 'idcustomer', 'foreign_field': 'idcustomer__idcustomer', 'title': 'CUSTOMER ID',
                'visible': True if 'customer_id' not in request.REQUEST else False,
                'searchable': True if 'customer_id' not in request.REQUEST else False
            },
            {
                'name': 'cusname', 'foreign_field': 'idcustomer__cusname', 'title': 'CUSTOMER NAME',
                'visible': True if 'idcustomer' not in request.REQUEST else False,
                'searchable': True if 'idcustomer' not in request.REQUEST else False
            },
            {'name': 'pk', 'title': '#Invoice', 'visible': True, 'searchable': False},
            {'name': 'invdate', 'title': 'Invoice Date', 'visible': True, },
            {'name': 'amount', 'title': 'Amount', 'visible': True, 'searchable': True},
            {'name': 'fullname', 'foreign_field': 'iduser__fullname', 'title': 'Representative', 'visible': True,
             'searchable': True},
            {'name': 'coments', 'title': 'Comments', 'visible': True, 'searchable': True},
            {'name': 'status', 'title': 'Status', 'visible': True, 'searchable': False},
            {'name': 'view', 'title': '', 'visible': request.user.has_perm('Procedure.view_invoices'),
             'searchable': False, 'orderable': False},
            {'name': 'deleted', 'title': '', 'visible': request.user.has_perm('Procedure.deleted_invoices'),
             'searchable': False, 'orderable': False},
        ]
        return self.column_defs


class CustomerFilesTable(AjaxDatatableView):
    model = Customer_Files
    code = 'CustomerFiles'
    initial_order = [['uploading_date', 'desc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []

    def get_column_defs(self, request):
        self.column_defs = [
            {'name': 'pk', 'visible': False, 'searchable': False},
            {
                'name': 'customerid', 'foreign_field': 'customer__idcustomer', 'title': 'CUSTOMER ID',
                'visible': True if 'customer_id' not in request.REQUEST else False,
                'searchable': True if 'customer_id' not in request.REQUEST else False
            },
            {
                'name': 'cusname', 'foreign_field': 'customer__cusname', 'title': 'CUSTOMER NAME',
                'visible': True if 'customer_id' not in request.REQUEST else False,
                'searchable': True if 'customer_id' not in request.REQUEST else False
            },
            {'name': 'logo', 'visible': True, 'searchable': False},
            {'name': 'filename', 'visible': True, 'searchable': True},
            {'name': 'folder', 'visible': True, 'searchable': True},
            {'name': 'path', 'visible': True, 'searchable': True},
            {'name': 'uploading_date', 'visible': True, 'searchable': True},
            {'name': 'download', 'title': 'Download', 'visible': True, 'searchable': False},
            {'name': 'delete', 'title': 'Delete', 'visible': request.user.has_perm('Procedure.delete_customer_files'),
             'searchable': False}
        ]
        return self.column_defs

    def customize_row(self, row, obj):
        ext = obj.filename.split('.')
        if ext[len(ext) - 1].lower() == 'docx':
            typefile = 'word.png'
        if ext[len(ext) - 1].lower() == 'pdf':
            typefile = 'pdf.png'
        if ext[len(ext) - 1].lower() == 'xlsx':
            typefile = 'excel.png'
        # row['customer'] = '%s - %s' % (obj.customer.idcustomer, obj.customer.cusname)
        row['logo'] = '<img src="/static/assets/img/typefiles/' + typefile + '" width="30px" height="28px">'
        row['path'] = obj.path.name
        row['uploading_date'] = obj.uploading_date.strftime('%m %d, %Y %H:%M')
        row['download'] = "<a href='" + obj.path.url + "' target='_blank'><i class='fa fa-download'></i> Download</a>"
        row[
            'delete'] = "<button type='button' class='btn btn-danger btn-sm' onclick='delete_file(%s);'><i class='fas fa-trash'></i>&nbspDelete</button>" % (
            obj.id)

    def get_initial_queryset(self, request=None):

        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request, 'REQUEST', None):
            request.REQUEST = request.GET if request.method == 'GET' else request.POST
        if 'customer_id' in request.REQUEST:
            customer_id = int(request.REQUEST.get('customer_id'))
            queryset = self.model.objects.filter(customer=customer_id, erased=False)
        else:
            queryset = self.model.objects.filter(erased=False);

        return queryset


class NewsTable(AjaxDatatableView):
    model = News
    code = 'News'
    initial_order = [['created_at', 'desc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []

    def get_column_defs(self, request):
        self.column_defs = [
            {'name': 'pk', 'visible': False, 'searchable': False},
            {'name': 'subject', 'visible': True, 'searchable': True},
            {'name': 'description', 'visible': True, 'searchable': True},
            {'name': 'public', 'visible': True, 'searchable': True},
            {'name': 'repeat', 'visible': True, 'searchable': True},
            {'name': 'created_at', 'visible': True, 'searchable': False},
            {'name': 'last_repeat', 'visible': True, 'searchable': False},
            {'name': 'repeat_since', 'visible': True, 'searchable': False},
            {'name': 'repeat_until', 'visible': True, 'searchable': False},
            {'name': 'is_active', 'title': 'Active', 'visible': True, 'searchable': False},
            {'name': 'delete', 'title': 'Delete', 'searchable': False}
        ]
        return self.column_defs

    def customize_row(self, row, obj):
        row['created_at'] = obj.created_at.strftime('%m %d, %Y %H:%M')
        row['last_repeat'] = obj.last_repeat.strftime('%m %d, %Y %H:%M')
        row['repeat_since'] = obj.repeat_since.strftime('%m %d, %Y %H:%M')
        row['repeat_until'] = obj.repeat_until.strftime('%m %d, %Y %H:%M')
        # row['download'] = "<a href='" + obj.path.url + "' target='_blank'><i class='fa fa-download'></i> Download</a>"
        row[
            'delete'] = "<button type='button' class='btn btn-danger btn-sm' onclick='delete_file(%s);'><i class='fas fa-trash'></i>&nbspDelete</button>" % (
            obj.id)


class CustomersTable(AjaxDatatableView):
    model = Customers
    code = 'Customers'
    initial_order = [['idcustomer', 'desc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []

    def get_column_defs(self, request):
        self.column_defs = [
            {'name': 'pk', 'visible': False, 'searchable': False},
            {'name': 'idcustomer', 'visible': True, 'searchable': True},
            {'name': 'cusname','title': 'Customer Name', 'visible': True, 'searchable': True},
            {'name': 'owner', 'visible': True, 'searchable': True},
            {'name': 'owner_surname', 'visible': True, 'searchable': True},
            {'name': 'email', 'visible': True, 'searchable': True},
            {'name': 'irpid', 'visible': True, 'searchable': True},
            {'name': 'mobile1', 'title':'Mobile','visible': True, 'searchable': True},
            {'name': 'contact2', 'title':'Contact 2','visible': True, 'searchable': True},
            {'name': 'mobile2', 'title':'Mobile 2','visible': True, 'searchable': True},
            {'name': 'clientstatus', 'title':'Status', 'visible': True, 'searchable': False},
            {'name': 'view', 'title': 'View', 'visible': request.user.has_perm('Procedure.delete_customers'), 'searchable': False},
            {'name': 'delete', 'title': 'Delete', 'visible': request.user.has_perm('Procedure.delete_customers'), 'searchable': False}
        ]
        return self.column_defs

    def customize_row(self, row, obj):
        row['view'] = f"<a class='btn btn-warning btn-sm editar' href='/Procedure/customer_view/{obj.idcustomer}' ><i class='fas fa-eye'></i> &nbsp;View</a>"
        row['delete'] = "<button type='button' class='btn btn-danger btn-sm' data-toggle='modal' data-target='#modal-danger' onclick='delete_message(%s, %s);'><i class='fas fa-trash'></i>&nbspDelete</button>" % (
            obj.idcustomer, obj.cusname)

    def get_initial_queryset(self, request=None):

        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request, 'REQUEST', None):
            request.REQUEST = request.GET if request.method == 'GET' else request.POST
        queryset = self.model.objects.filter(clientstatus='Active')
        return queryset
    
class ServicesTable(AjaxDatatableView):
    model = Services
    code = 'services'
    initial_order = [['pk', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []

    def get_column_defs(self, request):
        self.column_defs = [
            {'name': 'pk', 'visible': True, 'searchable': True},
            {'name': 'description', 'visible': True, 'searchable': True},
            {'name': 'rate', 'visible': True, 'searchable': True},
            {'name': 'cost', 'visible': True, 'searchable': True},
            {'name': 'commission_percentage', 'visible': True, 'searchable': False},
            {'name': 'is_project', 'title': 'Project', 'visible': True, 'searchable': False},
            {'name': 'need_invoice', 'title': 'Invoice', 'searchable': False},
            {'name': 'is_active', 'title': 'Active', 'visible': True, 'searchable': False},
        ]
        return self.column_defs
    
    def customize_row(self, row, obj):
        commission = Commission_Value.objects.filter(service=obj.idservice).first()
        row['commission_value'] = "0.00" if commission is None else commission.commission_percentage
    
    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not getattr(request, 'REQUEST', None):
            request.REQUEST = request.GET if request.method == 'GET' else request.POST
        queryset = self.model.objects.filter(is_active=True)
        return queryset