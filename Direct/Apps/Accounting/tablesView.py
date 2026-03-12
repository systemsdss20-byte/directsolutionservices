import datetime
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from ajax_datatable import AjaxDatatableView
from .serializers import InvoiceSerializer
from .models import Commission
from ..Procedure.models import Invoice_det, Invoice_paid, Invoices

class DailyChartTable(LoginRequiredMixin, generic.View):
    template = "Accounting/dailyCharttable.html"
    login_url = "Procedure:login"

    def get(self, request, *args, **kwargs):
        from_date = datetime.datetime.strptime(str(request.GET.get('from_date')), "%m/%d/%Y") if request.GET.get('from_date') else datetime.datetime.now()
        to_date = datetime.datetime.strptime(str(request.GET.get('to_date')), "%m/%d/%Y") if request.GET.get('to_date') else datetime.datetime.now()
        invoices = self.filter_date(from_date, to_date)
        page_number = request.GET.get('page', 1)
        paginator = Paginator(invoices, 10)

        try:
            invoices_page = paginator.page(page_number)
        except PageNotAnInteger:
            invoices_page = paginator.page(1)
        except EmptyPage:
            invoices_page = paginator.page(paginator.num_pages)
        data = self.summary(from_date, to_date)
        return render(request, self.template, context={"invoices": invoices_page, "total_cost": data['total_cost'], "total_payment": data['total_payment'], "from_date": from_date, "to_date": to_date}) 
    
    def filter_date(self, from_date, to_date):
        try:
            invoices = Invoices.objects.filter(paid_date__range=[from_date, to_date], deleted=False)
        except Invoices.DoesNotExist as e:
            print(e)
        serializer = InvoiceSerializer(invoices, many=True)
        return serializer.data
    
    def summary(self, from_date, to_date):
        try:
          total_cost = Invoice_det.objects.filter(idinvoice__paid_date__range=[from_date, to_date]).aggregate(cost=Sum('cost'))
          total_payment = Invoice_paid.objects.filter(idinvoice__paid_date__range=[from_date, to_date]).aggregate(paid=Sum('paid'))
        except:
          print('An exception occurred')
        return {'total_cost': total_cost['cost'], 'total_payment': total_payment['paid']}
    
class CommissionsTable(AjaxDatatableView):
    model = Commission
    show_date_filters = True
    initial_order = [['pk', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []
        
    def get_column_defs(self, request):
        self.column_defs = [
            {'name': 'checkbox', 'title': '<input type="checkbox" id="select-all">', 'visible': True, 'searchable': False, 'orderable': False, 'className': 'text-center'},
            { 'name': 'pk', 'visible': True, 'searchable': False, 'orderable': True, 'width': '5' },
            {'name': 'created_at', 'title': 'Commission Date', 'visible': True, 'searchable': False},
            {'name': 'details__idinvoice', 'foreign_field': 'details__idinvoice__idinvoice', 'title': 'Invoice Number', 'visible': True, 'searchable': True},
            {'name': 'employee__names', 'foreign_field': 'employee__names', 'title': 'Employee Name', 'visible': True, 'searchable': True},
            {'name': 'employee__surnames', 'foreign_field': 'employee__surnames', 'title': 'Employee Surnames', 'visible': True, 'searchable': True},
            {'name': 'quantity', 'foreign_field': 'details__quantity', 'title': 'Quantity', 'visible': True, 'searchable': True},
            {'name': 'details__service', 'foreign_field': 'details__service', 'title': 'Service', 'visible': True, 'searchable': True},
            {'name': 'amount_commission', 'title': 'Amount', 'visible': True, 'searchable': True},
            {'name': 'status', 'title': 'Status', 'visible': True, 'searchable': True, 'choices': [('PENDING', 'PENDING'), ('PAID', 'PAID'), ('REJECTED', 'REJECTED')], 'className': 'text-center', 'width': 'auto'},
        ]
        return self.column_defs
    
    def customize_row(self, row, obj):
        # select_values = ['PENDING', 'PAID', 'REJECTED']
        # select_control = '<select class="form-select form-select-sm" name="status" id="status">'
        # for value in select_values:
        #     if value == row['status']:
        #         select_control += '<option value="%s" selected="selected">%s</option>' % (value, value)
        #     select_control += '<option value="%s">%s</option>' % (value, value)
        # select_control += '</select>'
        # row['status'] = select_control
        match obj.status:
            case 'PAID':
                row['status'] = '<span class="status-icon bg-success"></span>%s' % obj.status
            case 'REJECTED':
                row['status'] = '<span class="status-icon bg-danger"></span>%s' % obj.status
            case 'PENDING':
                row['status'] = '<span class="status-icon bg-warning"></span>%s' % obj.status
        return super().customize_row(row, obj)
    
    def filter_queryset_by_date_range(self, date_from, date_to, qs):
        if date_from and date_to:
            qs = self.model.objects.filter(created_at__date__range=[date_from, date_to], details__delete=False)
        return qs
    
    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        today = datetime.date.today()
        queryset = self.model.objects.filter(created_at__month=today.month, created_at__year=today.year, details__delete=False)
        return queryset
    
    def render_column(self, row, column):        
        if column == 'checkbox':
            # Aquí renderizamos el checkbox para cada fila.
            return f'<input type="checkbox" class="row-checkbox" name="commissions[]" value="{row.id}">'
        else:
            return super().render_column(row, column)
        
    def footer_message(self, qs, params):
        total_commission = qs.aggregate(total=Sum('amount_commission'))
        return "Total Commission: $" + str(total_commission['total']) 