from ajax_datatable import AjaxDatatableView
from datetime import datetime
from django.core.exceptions import PermissionDenied
from .models import Detail_RandomList


class DetailListRandomTable(AjaxDatatableView):
    model = Detail_RandomList
    # initial_order = [['id', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    column_defs = []
    permits = {}

    def get_column_defs(self, request):
        self.column_defs = [
            {'name': 'pk', 'visible': False, 'searchable': False},
            {'name': 'customer', 'foreign_field':'customer__idcustomer', 'title': 'Customer', 'visible': True, 'searchable': True},
            {'name': 'company', 'foreign_field':'customer__cusname', 'title': 'Company', 'visible': True, 'searchable': True},
            {'name': 'company_phone', 'foreign_field': 'customer__mobile1', 'title': 'Company Phone', 'visible': True, 'searchable': True},
            {'name': 'fullname', 'foreign_field':'driver__nombre', 'title': 'Driver', 'visible': True, 'searchable': True},
            {'name': 'phone', 'foreign_field':'driver__phone', 'title': 'Phone', 'visible': True, 'searchable': True},
            {'name': 'test', 'title': 'Test', 'visible': True, 'searchable': False, 'orderable': False},
            {'name': 'status', 'title': 'Status', 'visible': True, 'searchable': False, 'orderable': False},
        ]
        return self.column_defs

    def customize_row(self, row, obj):
        if obj.test_substances:
            row['test'] = "Substances"
        if obj.test_alcohol:
            row['test'] = "Alcohol"
        if obj.test_substances and obj.test_alcohol:
            row['test'] = "Substances and Alcohol"
        
    def get_initial_queryset(self, request=None):
        
        if not request.user.is_authenticated:
            raise PermissionDenied
        
        if request.method == 'POST':
            year = request.POST.get('year')  if request.POST.get('year') else datetime.today().year
            quarter = request.POST.get('quarter')
            test = request.POST.get('test')
            queryset = self.model.objects.filter(random_list__year=year, random_list__quarter=quarter).order_by('id')
            
            if test == 'alcohol':
                queryset = queryset.filter(test_alcohol=True)
            if test == 'substances':
                queryset = queryset.filter(test_substances=True)            
        return queryset
    
    