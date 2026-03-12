import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views import generic
from rest_framework import generics
from decimal import Decimal

from .tablesView import DailyChartTable
from ..helpers.message import MessageResponse
from .serializers import InvoiceSerializer
from ..Procedure.models import Invoices, Invoice_det
from .models import Commission



class DailyChartView(LoginRequiredMixin, generic.View):
    login_url = "Procedure:login"
    template = "Accounting/daily_chart.html"

    def get(self, request, *args, **kwargs):          
        return render(request, self.template, {}) 
    
    def patch(self, request, *args, **kwargs):
        params = json.loads(request.body)
        from_date = datetime.datetime.strptime(str(params['from_date']), "%m/%d/%Y")
        to_date = datetime.datetime.strptime(str(params['to_date']), "%m/%d/%Y")
        
        try:
            Invoice_det.objects.filter(idinvoicedet=params['idinvoicedet']).update(cost=params['cost'])
            data = DailyChartTable().summary(from_date, to_date)
            return MessageResponse(data=data, description="Updated successfully").success()
        except Exception as e:
            print(e)
            return MessageResponse(description="Internal Server Error").error()


class InvoiceDetailView(generics.RetrieveAPIView):
    queryset = Invoices.objects.all()  # Retorna una factura por su ID
    serializer_class = InvoiceSerializer


class CommissionsView(LoginRequiredMixin, generic.View):
    login_url = "Procedure:login"
    template = "Accounting/commissions.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template, {})
    
    def post(self, request, *args, **kwargs):
        try:
            commsission_status = str(request.POST.get('status'))
            if commsission_status != '-- Select --':
                commissions = request.POST.getlist('commissions[]')
                for commission in commissions:
                    Commission.objects.filter(id=commission).update(status=commsission_status)    
                return MessageResponse(description="Commissions status successfully updated").success()
            else:
                return MessageResponse(description="Commission status is required").warning()
        except Exception as e:
            print("Error update commission status", e)
            return MessageResponse(description="Internal Server Error").error()
        except ValueError as e:
            print(f"Invalid value {e}")
            return MessageResponse(description="Invalid value").error()

def saveCommision(invoice_id, user):
    try:
        details_invoice = Invoice_det.objects.filter(idinvoice=invoice_id)
        for detail in details_invoice:
            if hasattr(detail.code, "commission_value"):
                commission = Commission()
                commission.details = detail
                commission.amount_commission = detail.code.commission_value.commission_value * Decimal(detail.quantity)  
                if detail.code.commission_value.employee is not None:
                    commission.employee = detail.code.commission_value.employee
                else:
                    commission.employee = user.employee
                commission.save()           
    except Exception as e:
        print('error saveCommision', e)
        
def deleteCommission(detail_invoice_id):
    try:
        Commission.objects.filter(details=detail_invoice_id).update(status='REJECTED')
    except Exception as e:
        print('error deleteCommission', e)