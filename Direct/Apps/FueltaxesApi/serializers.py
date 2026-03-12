from rest_framework import serializers
from ..Procedure.models import Customers, Units, Recive

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['idcustomer', 'cusname']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Units
        fields = ['idunit', 'nounit', 'status', 'idcustomer']
        
class ReciveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recive
        fields = '__all__'