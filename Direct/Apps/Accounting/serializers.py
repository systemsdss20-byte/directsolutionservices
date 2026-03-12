from rest_framework import serializers
from ..Procedure.models import Invoices, Invoice_det, Invoice_paid


class InvoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice_det
        fields = ['idinvoicedet', 'idinvoice', 'service', 'quantity', 'rate', 'amount', 'cost', 'delete']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice_paid
        fields =['idpaid', 'idinvoice', 'datepaid', 'typepaid', 'paid']


class InvoiceSerializer(serializers.ModelSerializer):
    details = InvoiceDetailSerializer(many=True, read_only=True)
    details_count = serializers.SerializerMethodField()
    paids = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Invoices
        fields = ['idinvoice', 'invdate', 'amount', 'idcustomer', 'status', 'cusname', 'paid_date', 'details', 'details_count', 'paids', 'deleted']

    def get_details_count(self, obj):
        return obj.details.count() + obj.paids.count()