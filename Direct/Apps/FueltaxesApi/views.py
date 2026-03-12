from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..Procedure.models import Customers, Units, Recive
from .serializers import CustomerSerializer, UnitSerializer, ReciveSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customers_list(request, pk):
    try:
        customer = Customers.objects.only('idcustomer', 'cusname', 'clientstatus').get(idcustomer=pk)
    except Customers.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = CustomerSerializer(customer)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def units_list(request, customer_id):
    try:
        units = Units.objects.filter(status='Active', idcustomer=customer_id) # pylint: disable=no-member
    except Units.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = UnitSerializer(units, many=True) #many=True if you have more than one object to serialize 
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def created_recive(request):
    serializer = ReciveSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)