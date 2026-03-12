from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.generic import View


class IndexView(View):
    template_name = 'Audit_Logs/index.html'

    def get(self, request, *args, **kwargs):
        assert isinstance(request, object)
        return render(request, self.template_name, {})


class CustomerAuditLogView(View):
    template_name = 'Audit_Logs/Customers/list.html'

    def get(self, request, *args, **kwargs):
        assert isinstance(request, object)
        return render(request, self.template_name, {})


class CardsAuditLogView(View):
    template_name = 'Audit_Logs/Cards/list.html'

    def get(self, request, *args, **kwargs):
        assert isinstance(request, object)
        return render(request, self.template_name, {})


class DriversAuditLogView(View):
    template_name = 'Audit_Logs/Drivers/list.html'

    def get(self, request, *args, **kwargs):
        assert isinstance(request, object)
        return render(request, self.template_name, {})


class UnitAuditLogView(View):
    template_name = 'Audit_Logs/Units/list.html'

    def get(self, request, *args, **kwargs):
        assert isinstance(request, object)
        return render(request, self.template_name, {})