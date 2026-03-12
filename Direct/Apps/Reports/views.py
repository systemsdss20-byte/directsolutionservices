import csv
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.views import View
from django.middleware.csrf import get_token
from ..Procedure.models import Customers
from .query_config import FILTER_FIELDS, OPERATORS
from ajax_datatable.views import AjaxDatatableView
from .utils import build_query
from .validators import validate_filters, InvalidFilter

# Create your views here.
def customers_page(request): 
    return render(request, "Reports/customers_datatable.html", {
        "filter_fields": json.dumps(FILTER_FIELDS),
        "operators": json.dumps(OPERATORS),
        "csrf_token": get_token(request),
    })

class CustomersAjaxDatatableView(AjaxDatatableView):
    model = Customers
    title = "Customers"
    length_menu = [[25,50,100,-1], [25,50,100,"All"]]

    column_defs = [
        {"name": "pk", "title": "ID"},
        {"name": "cusname", "title": "Name"}, 
        {"name": "contact1", "title": "Contact"},
        {"name": "mobile1", "title": "Mobile"},
        {"name": "email", "title": "Email"},
        {"name": "state", "title": "State"},
        {"name": "clientstatus", "title": "Client Status"},
        {"name": "since", "title": "Client Since"},
        {"name": "credithold", "title": "Credit Hold"},
    ]

    def get_initial_queryset(self, request=None):
        qs = super().get_initial_queryset(request)

        filters_json  = request.POST.get("filters")
        print(filters_json)
        if not filters_json:
            return qs.none()

        try:
            groups = json.loads(filters_json)
            validate_filters(groups)
            return qs.filter(build_query(groups))
        except InvalidFilter as e:
            self.error = str(e)
            return qs.none()
        except Exception:
            self.error = "IInvalid filters format"
            return qs.none()

    def render_column(self, row, column):
        return super().render_column(row, column)
    
    def customize_row(self, row, obj):
        if hasattr(self, "error"):
            row["_error"] = self.error
  
    
def customers_export(request):
    groups = json.loads(request.POST.get("filters", "[]"))
    qs = Customers.objects.filter(build_query(groups))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=customers.csv"
    writer = csv.writer(response)
    writer.writerow(["Name", "State", "Client Status", "Client Since", "Credit Hold"])

    for c in qs:
        writer.writerow([c.cusname, c.state, c.clientstatus, c.since, c.credithold])
    
    return response