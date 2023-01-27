from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model    
User = get_user_model()

class UserCreateSerializers(UserCreateSerializer):        #SERIALIZER NOS PERMITE USAR UN MODELO CREADO POR DJ_RESTFRAMEWORK
    class Meta(UserCreateSerializer.Meta):                #TRANSFORMAR EL MODELO EN DATOS QUE PUEDEN SER CONSULTADOS POST, GET
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'get_full_name',
            'get_short_name'            
        )

