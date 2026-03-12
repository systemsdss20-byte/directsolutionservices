from ajax_datatable import AjaxDatatableView
from ..Procedure.models import Invoices

class InvoicesTableView(AjaxDatatableView):
    model = Invoices
    title = "Invoices Table"
    initial_order = [["invdate", "desc"]]
    length_menu = [[10, 25, 50, 100], [10, 25, 50, 100]]
    search_values_separator = " "
    
    column_defs = [
        {"name": "checkbox", "visible": True, "searchable": False, "orderable": False, "width": "20px"},
        {"name": "idinvoice", "title": "Invoice ID", "visible": True},
        {"name": "invdate", "title": "Invoice Date", "visible": True},
        {"name": "cusname", "title": "Customer Name", "visible": True},
        {"name": "amount", "title": "Amount", "visible": True},
        {"name": "status", "title": "Status", "visible": True},
        {"name": "download", "title": "Download", "visible": True, "searchable": False, "orderable": False},
    ]
    
    def customize_row(self, row, obj):
        row['checkbox'] = f'<input type="checkbox" class="invoice-checkbox" data-id="{obj.idinvoice}"/>'
        row['status'] = "<span class='badge badge-success'>Paid</span>" if obj.status == 'Paid' else "<span class='badge badge-warning'>Pending</span>"
        row['download'] = f'<a href="/invoices/download/{obj.idinvoice}/" class="btn btn-sm btn-primary">Download</a>'
        
    # def get_