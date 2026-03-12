from ajax_datatable import AjaxDatatableView
from django.template.loader import render_to_string

from ..Procedure.models import Customers, Units, Road_Taxes, Cards, Drivers


class CustomerAuditLogDataView(AjaxDatatableView):
    model = Customers
    code = 'Customers'
    initial_order = [['idcustomer', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    render_row_details_template_name = 'Audit_Logs/history_log.html'

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'pk', 'visible': False, 'searchable': False},
        {'name': 'idcustomer', 'visible': True, 'searchable': True},
        {'name': 'cusname', 'visible': True, 'searchable': True},
        {'name': 'owner', 'visible': True, 'searchable': True},
        {'name': 'owner_surname', 'visible': True, 'searchable': True},
    ]

    def render_row_details(self, pk, request=None):
        audited_model = self.model.objects.get(pk=pk)
        details = log_processing(self, audited_model)
        return render_to_string(self.render_row_details_template_name, {'details': details})


class CardsAuditLogDataView(AjaxDatatableView):
    model = Cards
    code = 'Cards'
    initial_order = [['idcustomer', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    render_row_details_template_name = 'Audit_Logs/history_log.html'

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'pk', 'visible': False, 'searchable': False},
        {'name': 'cardno', 'visible': True, 'searchable': False,},
        {'name': 'idcustomer', 'visible': True, 'searchable': True},
        {'name': 'type', 'visible': True, 'searchable': True},
        {'name': 'status', 'visible': True, 'searchable': True},
        {'name': 'last_used', 'visible': True, 'searchable': True},
    ]

    def render_row_details(self, pk, request=None):
        audited_model = self.model.objects.get(pk=pk)
        details = log_processing(self, audited_model)
        return render_to_string(self.render_row_details_template_name, {'details': details})


class DriversAuditLogDataView(AjaxDatatableView):
    model = Drivers
    code = 'Drivers'
    initial_order = [['idcustomer', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    render_row_details_template_name = 'Audit_Logs/history_log.html'

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'pk', 'visible': False, 'searchable': False},
        {'name': 'idcustomer', 'foreign_field': 'idcustomer__idcustomer'},
        {'name': 'nombre', 'visible': True, 'searchable': True},
        {'name': 'ssn', 'visible': True, 'searchable': True},
        {'name': 'cdl', 'visible': True, 'searchable': True},
    ]

    def customize_row(self, row, obj):
        row['idcustomer'] = "%s-%s" % (obj.idcustomer.idcustomer, obj.idcustomer.cusname)

    def render_row_details(self, pk, request=None):
        audited_model = self.model.objects.get(pk=pk)
        details = log_processing(self, audited_model)
        return render_to_string(self.render_row_details_template_name, {'details': details})


class UnitAuditLogDataView(AjaxDatatableView):
    model = Units
    code = 'Units'
    initial_order = [['idcustomer', 'asc']]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    render_row_details_template_name = 'Audit_Logs/history_log.html'

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'pk', 'visible': False, 'searchable': False},
        {'name': 'idcustomer', 'foreign_field': 'idcustomer__idcustomer'},
        {'name': 'nounit', 'visible': True, 'searchable': True},
        {'name': 'vin', 'visible': True, 'searchable': True},
        {'name': 'title', 'visible': True, 'searchable': True},
    ]

    def customize_row(self, row, obj):
        row['idcustomer'] = "%s-%s" % (obj.idcustomer.idcustomer, obj.idcustomer.cusname)

    def render_row_details(self, pk, request=None):
        unit = self.model.objects.get(pk=pk)
        changes_history = unit.history.all()
        details = list()
        next_item: int = 1
        for change_log in changes_history:
            if len(changes_history) != next_item:
                delta = change_log.diff_against(changes_history[next_item])
                new_value = ""
                old_value = ""
                for change in delta.changes:
                    if change.field == 'road_taxes':
                        if change.old:
                            category_road_old = Road_Taxes.objects.get(id=change.old)
                            old_value = category_road_old.category if change.field == 'road_taxes' and change.old else change.old
                        if change.new:
                            category_road_new = Road_Taxes.objects.get(id=change.new)
                            new_value = category_road_new.category if change.field == 'road_taxes' and change.new else change.new
                    else:
                        old_value = change.old
                        new_value = change.new
                    details.append({
                        'field': change.field, 'old_value': old_value, 'new_value': new_value,
                        'changed_by': change_log.history_user, 'history_date': change_log.history_date,
                        'action': change_log.get_history_type_display
                    })
            next_item = next_item+1
        return render_to_string(self.render_row_details_template_name, {'details': details})


def log_processing(self, audited_model):
    changes_history = audited_model.history.all()
    details = list()
    next_item: int = 1
    for change_log in changes_history:
        if len(changes_history) != next_item:
            delta = change_log.diff_against(changes_history[next_item])
            for change in delta.changes:
                details.append({
                    'field': change.field, 'old_value': change.old, 'new_value': change.new,
                    'changed_by': change_log.history_user, 'history_date': change_log.history_date,
                    'action': change_log.get_history_type_display
                })
        next_item = next_item + 1
    return details