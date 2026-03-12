import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from safer import CompanySnapshot

from ..Procedure.models import Customers


class UpdateDot(View):
    model = Customers

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.model = self.model.objects.filter(clientstatus='Active', dotidexp__lte='2026-01-01').exclude(Q(dotid__isnull=True) | Q(dotid__exact='')).values_list('idcustomer', flat=True)

    def get(self, request):
        total = self.model.count()
        pagination = list(range(0, total, 100))

        if pagination[-1] != total:
            pagination.append(total)
        limits = list()
        for page in pagination:
            index = pagination.index(page)
            if len(pagination) - 1 != index:
                limits.append({'start': page, 'end': pagination[index + 1]})
        data = list()
        for limit in limits:
            customers = list(self.model[limit['start']:limit['end']])
            data.append({'value': f"{limit['start']}-{limit['end']}", 'customers': customers})
        return render(request, 'Helpers/UpdateDOT.html', {'data_list': data})

    def post(self, request):
        customer = json.load(request)["customer"]
        result = ""
        try:
            customer_update = Customers.objects.only('idcustomer', 'dotidexp', 'dotid').get(idcustomer=customer)
            data = queryDOT(customer_update.dotid)
            if data['status'] == 'ok':
                customer_update.dotidexp = data['expiration']
                customer_update.save()
                result = f"DOT: {customer_update.dotid} updated"
            else:
                result = f"CUSTOMER:{customer}, {data['message']}"
        except Customers.DoesNotExist as e:
            result = f'Customer ID: {customer} does not exist'
            print(f'Customer not found: {e}')
        except json.JSONDecodeError as e:
            result = f'Invalid JSON data for Customer ID: {customer}'
            print(f'JSON decode error: {e}')
        except Exception as e:
            result = f'Unexpected error for Customer ID: {customer}'
            print(f'Unexpected error: {e}')
        response = JsonResponse({'data': result})
        return HttpResponse(response, content_type='application/json', status=200)


def queryDOT(dot_id, get_company=False):
    try:
        client_safer = CompanySnapshot()
        dot_id = int(dot_id) if type(dot_id == str) else dot_id
        company = client_safer.get_by_usdot_number(dot_id)
        if get_company:
            return {'status': 'ok', 'company': company}
        else:
            return {'status': 'ok', 'expiration': company.mcs_150_form_date.strftime("%Y-%m-%d")}
    except (ValueError, AttributeError, TypeError) as e:
        message = f'DOT: {dot_id}, ERROR: {e}'
        return {'status': 'error', 'message': message}