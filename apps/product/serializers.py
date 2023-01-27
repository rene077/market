from rest_framework import serializers    #SE SERIALIZA PARA PODER MOSTRAR LA INFO EN FORMATO JSON
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','photo','description','price','compare_price','category','quantify','sold','date_created',
        'get_thumbnail'] 