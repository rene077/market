from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from .models import Category

class ListCategoriesView(APIView):
    permission_classes= (permissions.AllowAny, )  #PERMISSIONS NOS PERMITE ACCEDER AL API

    def get(self, request, format=None):
        if Category.objects.all().exists():     #SÍ EXISTE CATEGORIA,PODEMOS HACER REQUEST,TRAEMOS TODOO A VAR CATEGORIES
            categories = Category.objects.all()
   
            result = []

            for category in categories:                      #RECORREMOS TAL VAR 
                if not category.parent:       #BUSCAMOS LOS CATEGORY QUE NO TIENEN PADRES///******
                    item = {}                           #ITEM ES UN DICCIONARIO VACIO
                    item['id']= category.id
                    item['name']= category.name              

                    item['sub_categories'] = [] 
                    for cat in categories:
                        sub_item = {}                     #AQUI LOS CATEGORIES QUE SI TIENEN PADRES SON SUBS
                        if cat.parent and cat.parent.id == category.id:
                            sub_item['id'] = cat.id
                            sub_item['name'] = cat.name
                            sub_item['sub_categories'] = []

                            item['sub_categories'].append(sub_item)
                    result.append(item) 
            return Response({'categories': result}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No categories found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)                               
