from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.category.models import Category

from django.db.models import Q   #PARA IMPLEMENTAR BUSQUEDA DE PRODUCTOS


##PARA PODER MOSTRAR UN PRODUCTO INDIVIDUAL##

class ProductDetailView(APIView):         #3 TRAEMOS EL PRODUCTO CON EL ID EXACTO 3#
    permission_classes = (permissions.AllowAny, )  #PARA PODER USAR LAS APIS , TODOS PUEDEN VER EL PRODUCTO

    def get(self, request, productId, format=None):
        try:
            product_id = int(productId)  
        except:    
            return Response(
                {'error':'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        if Product.objects.filter(id=product_id).exists():   #SI EXISTE EL OBJ
            product = Product.objects.get(id=product_id)  #TRAEMOS AL OBJETO 

            product = ProductSerializer(product)  #SERIALIZAMOS LA INFO (CONVIERTE A JSON)

            return Response({'product': product.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error':'Product with this ID does not exist'},status=status.HTTP_404_NOT_FOUND)    

##PARA PODER MOSTRAR LISTA DE PRODUCTOS INDIVIDUAL##
 
class ListProductsView(APIView):                     #1 "MOSTRAR LISTA DE PRODUCTOS POR ORDER, ASCE OR DESC CON LIMITE" #1#
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        sortBy = request.query_params.get('sortBy')  #SE TRAE ASI "POR PUNTO", PORQUE VIENE INTRINSECO EN LA REQUEST
                  ##SELECCION DE FILTRO O PREDETERMINADO##
        if not (sortBy == 'date_created' or sortBy == 'price' or sortBy == 'sold' or sortBy == 'name'):
            sortBy = 'date_created'
                  ##SELECCION DE LA FORMA Y CANTIDAD A MOSTRAR##
        order = request.query_params.get('order')    #DE A-Z  , MAS TRAIDAS DE VARIABLES EXTERNAS INTRINSECAS,ej: ?ORDER=DESC
        limit = request.query_params.get('limit')    #CANTIDAD A MOSTRAR

        if not limit:                                #SI NO TIENE LIMIT LE ASIGNAMOS UNO DE 6
            limit = 6

        try:                                         #DE TENER UN LIMIT CORROBORAMOS AQUI QUE SEA DEL TYPE ADMITIDO 
            limit = int(limit)
        except:
            return Response (
                {'error':'Limit must be an integer'},status=status.HTTP_404_NOT_FOUND)        

        #"ES UN NUMERO", AHORA A VER SI COMPRENDE LO POSITIVO, SÍ ES NEGATIVO SE LA ASIGNA 6    
        if limit <= 0:                                                           
            limit = 6

        if order == 'desc':
            sortBy = '-' + sortBy
            products = Product.objects.order_by(sortBy).all()[:int(limit)]  #PRODUCTOS FILTRADOS DESC con limite 
        elif order == 'asc':
            products = Product.objects.order_by(sortBy).all()[:int(limit)]  #PRODUCTOS FILTRADOS ASC con limite 
        else:
            products = Product.objects.order_by(sortBy).all()               #PRODUCTOS FILTRADOS TODOS (Sin Límite) 

        products = ProductSerializer(products, many=True)  #SERIALIZAMOS PARA CONVERTIR A JSON Y MANY "ES TRUE X SER LISTA"     

        if products:                               #PASAMOS EL RESULTADO
            return Response({'products':products.data}, status=status.HTTP_200_OK) 
        else:
            return Response({'error': 'No products to list'},status=status.HTTP_404_NOT_FOUND)    



##VISTA DE BUSQUEDA DE PRODUCTO/S##
            
class ListSearchView(APIView):                     #2 "BUSQUEDA POR CATEGORIA Y/O DESCRIPCION" 2#
    permission_classes = (permissions.AllowAny, )   #TODOS PUEDEN BUSCAR
     
    def post(self, request, format=None):
        data = self.request.data


        try:              #SI O SI DEBE HABER CATEGORIA POR ELLO SE REALIZA EL TRY AQUI DE ENTRADA NOMAS (POS+)
            category_id = int(data['category_id'])
        except:  
            return Response({'error':'Category ID must be an integer'},status=status.HTTP_404_NOT_FOUND)


        search = data['search']          
                        ##SÍ TENEMOS UNA DESCRIPCION,¿QUE CAMINO TOMAR?##
        if len(search) == 0:                        #SI NO EXISTE UNA BUSQUEDA
            search_results = Product.objects.order_by('-date_created').all()    #MOSTRAMOS TODOS LOS PRODUCTOS
        else:
            search_results = Product.objects.filter( #DE EXISTIR PASAMOS LOS DETALLES A "Q"
                Q(description__icontains=search) | Q(name__icontains=search)       
            )    


        #SI LA CATEGORIA ES = "0" MUESTRO SEARCH DE ACUERDO A SI LO HAY O NO
        if category_id == 0:                          
            search_results = ProductSerializer(search_results, many=True)
            return Response({'search_products': search_results.data}, status=status.HTTP_200_OK)    

        #SI NO EXISTE EL NRO DE ID_CATEGORIA "DENTRO DEL RANGO EXISTENTE"
        if not Category.objects.filter(id=category_id).exists():
                return Response({'error':'Category not found'},status=status.HTTP_404_NOT_FOUND)
               

                ##EXISTE CATEGORY_ID Y TRAEMOS SU NOMBRE##
        category = Category.objects.get(id=category_id)        #TRAEMOS EL OBJETO

                    ##DONDE SE ENFATIZA O CAE MEJOR TU BUSQUEA DE ACUERDO A LA CATEGORIA INGRESADA##
                ##FINIKITAMOS LA INDEXACION##  SE BUSCA LA SUBCATEG -> EL PRODUCT ESPECIFICO
        if category.parent:    # C/PADRE, SE FILTRA AL HIJO(BUSQUEDA ESPECIFICA POR ESTAR YA DENTRO DE UNA CATEGORIA[PARENT])
            search_results = search_results.order_by('-date_created').filter(category=category)        
        else:                 #POR SI MISMO,MAS NO HAY ENGLOBE*********                 #**CATEG_PRODUCTOS=CATEG_INGRESADA**#     
            if not Category.objects.filter(parent=category).exists():   #POR DEFAULT,X HIJO,NO EXISTE EN EL RANGO EXISTENCIA
                search_results = search_results.order_by('-date_created').filter(category=category) #NO OBTENGO CATEGS   
            else:                           #NO TIENE PADRE Y LO SERIA PARA LAS DEMAS CATEGORIAS, engloba subcateg-hijos
                categories = Category.objects.filter(parent=category) #BUSQUEDA NO ESPECIFICA ENGLOBA OTRAS SUBCATEGS
                filtered_categories = [category]        #CREAMOS LA VAR-[ARRAY], YA CARGADA CON UNA CATEGORY(LA ORIGIN)
                                                        #Y AQUI OBTENGO OTRAS CATEGS REL Y DEBO HACER UN PROCEDIM MAS
                for cat in categories:                  #POR SI MISMO Y ENGLOBE EXISTENTE**********  
                    filtered_categories.append(cat)  

                filtered_categories = tuple(filtered_categories)
                                                                          #PARA FILTRAR UNA TUPLA ES CATEG__IN                          
                search_results = search_results.order_by('-date_created').filter(category__in = filtered_categories)

        search_results = ProductSerializer(search_results, many=True)
        return Response({'search_products':search_results.data}, status=status.HTTP_200_OK)



class ListRelatedView(APIView):         #4 MUESTRA LOS PRODUCTOS RELACIONADOS POR CATEGORIA EXCLUYENDO EL INGRESADO 4# 
    permission_classes = (permissions.AllowAny, )

    def get(self, request, productId, format=None):
        try:
            product_id = int(productId)                #HAY UN NRO_ID ,PARA VERIFICAR
        except:
            return Response(
                {'error':'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)    


        if not Product.objects.filter(id=product_id).exists():      #NO EXISTE EL ID DENTRO DEL RANGO DE IDs EXISTENTES
            return Response(
                {'error':'Product with this product ID does not exist'},
                status=status.HTTP_404_NOT_FOUND)

         #VERIFICADO EL ID DE TAL PRODUCT EXISTE Y ESTA DENTRO DEL RANGO EXISTENTE#

        category = Product.objects.get(id=product_id).category  #TRAEMOS " LA CATEGORIA " DE ESE PRODUCTO

                #TRABAJAMOS UNICAMENTE CON LA CATEGORIA AHORA
            #ESTO ES SOLO UNA CONDICIONAL NOMAS QUE AFIRMA QUE HAY RELACION ALGUNA ENTRE PRODUCTOS AL FILTRARSE ALGO#                                             
        if Product.objects.filter(category=category).exists():   #BLOCKCHAIN ESTA SOLO CERO RESULT DE FILTRO, NO ENTRA
                        #ADENTRO INICIA EL VERDADERO PROCESO CON EL USO DE LA CATEGORIA INICIAL
                if category.parent:
                    related_products = Product.objects.order_by(               #POR EL HIJO AL SER ESPECIFICO 
                        '-sold'
                        ).filter(category=category)
                else:
                    if not Category.objects.filter(parent=category).exists():  #POR SI MISMO, PORQUE NO HAY ENGLOBES
                        related_products = Product.objects.order_by(
                            '-sold'
                        ).filter(category=category)    

                    else:                #ESTOS PARENTS SON LOS SIGUIENTES A ÉL,QUE NO POSEE Y POR ESO ENGLOBA COMO PADRE
                        categories = Category.objects.filter(parent=category)  #POR SI MISMO Y LOS DEMAS EXISTENTES
                        filtered_categories = [category]     

                        for cat in categories:
                            filtered_categories.append(cat)  #CARGAMOS CON LA CATEGORIAS ENCONTRADAS

                        filtered_categories = tuple(filtered_categories)
                        related_products = Product.objects.order_by('-sold').filter(category__in=filtered_categories)    

                #EXCLUIR PRODUCTO QUE HEMOS INGRESADO DESDE EL INICIO
                related_products = related_products.exclude(id=product_id)        
                related_products = ProductSerializer(related_products, many=True)        

                if len(related_products.data) > 3:  #PRIMERO QUE SI CANTIDAD MAYOR A 3 ESTABLESCO LIMITE DE 3 A MOSTRAR 
                    return Response(
                           {'related_products': related_products.data[:3]},
                           status=status.HTTP_200_OK)   
                elif len(related_products.data) > 0:   #CONTINUAMOS MISMA CADENA ,TIENE QUE SER MAYOR A CERO MIN PARA MOSTRAR
                    return Response(
                           {'related_products': related_products.data},
                           status=status.HTTP_200_OK)
                else:                                  #CASO CONTRARIO A TODOO ELLO DE ARRIBA ,ERROR NO CUMPLE LOS DOS STANDARES 
                    return Response(
                        {'error': 'No related products found'}, 
                        status=status.HTTP_200_OK)        

        else: 
              return Response(
                 {'error':'No related products found'}, 
                 status=status.HTTP_200_OK)



class ListBySearchView(APIView):                 #LISTA DE PRODUCTOS RELACIONADOS Y FILTROS PERSONALIZADOS
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data

        try:
            category_id = int(data['category_id'])
        except:
            return Response({'error':'Category ID must be an integer'}, status=status.HTTP_404_NOT_FOUND)

        price_range = data['price_range']
        sort_by = data['sort_by']

        if not (sort_by == 'date_created' or sort_by == 'price' or sort_by == 'sold' or sort_by == 'name'):            
            sort_by = 'date_created'

        order = data['order']    
                #VERIFICACIONES  PRIMERO ANTES DE INGRESAR AL PROCESO
        if category_id == 0:                                       #SI LA CATEGORIA ES NEUTRA MOSTRAR TODOO
            product_results = Product.objects.all()
        elif not Category.objects.filter(id=category_id).exists(): #Y SI NO FIGURASE DE ENTRE LAS CATEGORIAS EXISTENTES
            return Response({'error':'This category does not exits'}, status=status.HTTP_404_NOT_FOUND)
        else:
            category = Category.objects.get(id=category_id)   #AL EXISTIR TRAEMOS EL NAME_CATEG
            if category.parent:                                                #XXXXX
                product_results = Product.objects.filter(category=category)    #XXXXX 
            else:                                                              #XXXXXX             
                if not Category.objects.filter(parent=category).exists():   
                    product_results = Product.objects.filter(category=category)
                else:                                                        #EL VERDADERO PROCESO COMIENZA AQUI    
                    categories = Category.objects.filter(parent=category)    #NO TENDRÍA PARENT PARA ENGLOBAR OTRAS CATEGS      
                    filtered_categories = [category]

                    for cat in categories:
                        filtered_categories.append(cat)

                    filtered_categories = tuple(filtered_categories)
                    product_results = Product.objects.filter(category__in=filtered_categories) #FILTRA PRODUCTS CON ESAS CATEGS              

                   ##FILTRAR POR PRECIO##                          "CONFIGURATION"
        if price_range == '1 - 19':
            product_results = product_results.filter(price__gte=1)  #MIN
            product_results = product_results.filter(price__lt=20)  #MAX
        elif price_range == '20 - 39':
            product_results = product_results.filter(price__gte=20)
            product_results = product_results.filter(price__lt=40)
        elif price_range == '40 - 59':
            product_results = product_results.filter(price__gte=40)
            product_results = product_results.filter(price__lt=60)
        elif price_range == '60 - 79':
            product_results = product_results.filter(price__gte=60)
            product_results = product_results.filter(price__lt=80)
        elif price_range == 'More than 80':
            product_results = product_results.filter(price__gte=80)

            ##FILTRAR PRODUCTO POR SORT_BY##

        if order == 'desc':
            sort_by = '-' + sort_by
            product_results = product_results.order_by(sort_by)
        elif order == 'asc':
            product_results = product_results.order_by(sort_by)
        else:
            product_results = product_results.order_by(sort_by)  #PREDETERMINADO
        
        product_results = ProductSerializer(product_results, many=True)

        #ULTIMA VERIFICACION DE YAPA    

        if len(product_results.data) > 0:     #AFIRMA QUE HABRIA MAS DE UN PRODUCT, POR ENDE HAY RELACIONES ENTRE PRODUCTS 
            return Response(
                {'filtered_products': product_results.data}, 
                status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'No products found'},
                status=status.HTTP_200_OK)                      
                                        























