from rest_framework import serializers
from .models import Detail_RandomList, RandomList

class RandomListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RandomList
        fields = '__all__'
        
class Detail_RandomListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Detail_RandomList
        # fields = ('id', 'random_list', 'customer_id', 'driver_id', 'test_substances', 'test_alcohol')
        fields = '__all__'