from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Cart,CartItem

from apps.product.models import Product
from apps.product.serializers import ProductSerializer


     #MOSTRAR ITEMS ASOCIADOS AL USUARIO : ID_ITEM, PRODUCT Y CANTIDAD DEL MISMO
class GetItemsView(APIView):
    def get(self, request, format=None):
        user = self.request.user                  #PUEDE TOMAR AL USUARIO POR ESTAR LOGUEADO
        try:
            cart = Cart.objects.get(user=user)     #TRAEMOS EL CART CON "user/ID" QUE SEA IGUAL AL "user/id" DE LA REQUEST LLEGADA
            cart_items = CartItem.objects.order_by('product').filter(cart=cart)#TRAEMOS EL CartItem ASOCIADO AL Usuario>cart_arriba

            result = []
                                    #CartItem es un grupo de productos que estan ligados a un CART distinto                    
            if CartItem.objects.filter(cart=cart).exists():  #SI SE PUDO FILTRAR LOS carts ACORDE AL "CART llegado" ES VALIDO:   
                for cart_item in cart_items:                 #DE ESE CONJUNTO OBTENIDO ARRIBA RECORRERLO UNO A UNO
                    item = {}                                

                    item['id'] = cart_item.id                           
                    item['count'] = cart_item.count
                    product = Product.objects.get(id=cart_item.product.id) #DE LOS VARIOS PRODUCTOS TRAER DEL DE EL ID_PRODUCT DE- 
                    product = ProductSerializer(product)                    #-CART_ITEM EN PARTICULAR  

                    item['product'] = product.data            #PASAJE DE VAR CARGADAS

                    result.append(item)                       #RESULT RECIBE TODOO ,ITEM_ID PRODUCT Y CANTIDAD DEL MISMO       
            return Response({'cart': result}, status=status.HTTP_200_OK)        
        except:
            return Response(
                {'error':'Something went wrong when retrieving cart items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


     #AGREGAR UN CART_ITEM(PRODUCTO) AL CARRITO 
class AddItemView(APIView):
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data            #ES "DATA" LA MANERA DE RECIBIR EL BODY AQUI CART.JS(ACTIONS)>ADD-ITEM(BODY:PRODUCT_ID)

        try:
            product_id = int(data['product_id'])
        except:
            return Response(
                {'error':'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND)

        count = 1           #VAR CARGADA CON UNA UNIDAD QUE USAREMOS LUEGO PARA AUMENTAR PRODUCT

        try:
            if not Product.objects.filter(id=product_id).exists():  #PRIMERO EL PRODUCTO DEBERÍA EXÍSTIR 
                return Response(
                    {'error':'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND)

            product = Product.objects.get(id=product_id)   #TRAEMOS EL "OBJETO PRODUCT" POR EL PRODUCT_ID
            cart = Cart.objects.get(user=user)             #TRAEMOS SU "CARRO" CON EL DATO EN SU REQUEST DE USER
        
            if CartItem.objects.filter(cart=cart, product=product).exists():  #SEGUNDO EL PRODUCT NO DEBE ESTAR EN SU CARRO P/+                  
                return Response({
                    'error':'Item is already in cart'}, #SI PODEMOS FILTRARLO ES QUE YA EXISTE EL ITEM ,NO SE PUEDE CREAR CART_ITEM
                    status=status.HTTP_409_CONFLICT)
                       
                #TERCERO, PERO OTRO DATO FUNDAMENTAL ES QUE EXISTA STOCK DE TAL PRODUCTO PARA PODER CREAR EL CART_ITEM
            if int(product.quantify) > 0 :                      #SE CHECKEA EL STOCK 
                CartItem.objects.create(                        #SE LE CREA UN CART_ITEM
                    product=product, cart=cart, count=count
                )        
                    #AHORA VERIFICAMOS QUE YA EXISTA LO CREADO,ENTONCES PODEMOS AGREGARLE 1 UNIDAD AL CONTENEDOR DEL PRODUCTO       
                if CartItem.objects.filter(cart=cart, product=product).exists():  #ACLARACION, NO ES PARA ITERAR
                    total_items = int(cart.total_items) + 1
                    Cart.objects.filter(user=user).update(                       #ACTUALIZA LA CANTIDAD EN LA BASE DE DATOS
                        total_items=total_items 
                    )
                        #COMO PARA MOSTRAR NUEVAMENTE LOS DATOS ,PERO YA ACTUALIZADOS
                    cart_items = CartItem.objects.order_by('product').filter(cart=cart)

                    result = [] 

                    for cart_item in cart_items:

                        item = {}
                        item['id'] = cart_item.id          #ESTE ID SE REFIERE AL USUARIO ,ESTA LIGADO, FIJO FOREIGNKEY
                        item['count'] = cart_item.count
                        product = Product.objects.get(id=cart_item.product.id)
                        product = ProductSerializer(product)

                        item['product'] = product.data

                        result.append(item)                #COMO PARA MOSTRAR NUEVAMENTE LOS DATOS PERO YA ACTUALIZADOS DE LOS ITEMS

                    return Response({'cart': result}, status=status.HTTP_201_CREATED) 
            else:
                return Response({'error':'Not enough of this item in stock'},
                status=status.HTTP_200_OK)
        except:
            return Response({'error':'Something went wrong when adding item to cart'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        #TRAEMOS PRECIO_TOTAL Y PRECIO_TOTAL_DESC A PAGAR
class GetTotalView(APIView):

    def get(self, request, format=None):
        user = self.request.user

        try:
            cart = Cart.objects.get(user=user)              #TRAEMOS EL "CARRITO"
            cart_items = CartItem.objects.filter(cart=cart) #TRAEMOS LOS "CART_ITEMS" DENTRO DEL CARRITO

            total_cost = 0.0
            total_compare_cost = 0.0 

            if cart_items.exists():            
                for cart_item in cart_items:              
                    total_cost += (float(cart_item.product.price)                 #PRECIO_PRODUCT * SU CANTIDAD 
                                    * float(cart_item.count))
                    total_compare_cost += (float(cart_item.product.compare_price) #PRECIO_PRODUCT_DESC * SU CANTIDAD 
                                            * float(cart_item.count))
                total_cost = round(total_cost, 2)                                 #SE REDONDEAN LOS TOTALES
                total_compare_cost = round(total_compare_cost, 2)
            return Response(                                                      #SE ENVIAN LOS RESULTADOS CON STATUS OK 200  
                {'total_cost': total_cost, 'total_compare_cost': total_compare_cost},
                status=status.HTTP_200_OK
            )        
        except:
            return Response(
                {'error':'Something went wrong when retrieving total costs'}
            )                        


        #TRAEMOS UNICAMENTE TOTAL_ITEMS DEL CARRO DEL USUARIO  
class GetItemTotalView(APIView):
    def get(self, request, format=None):
        user = self.request.user                            

        try:
            cart = Cart.objects.get(user=user)
            total_items = cart.total_items                  #TRAEMOS EL TOTAL INDIVIDUAL DE UN ITEM

            return Response(
                {'total_items':total_items},
                status=status.HTTP_200_OK)
        except:    
            return Response(
                {'error':'Something went wrong when getting total number of items'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        #ACTUALIZAR LA CANTIDAD ITEMS(PRODUCTOS A COMPRAR)
class UpdateItemView(APIView):
      def put(self, request, format=None):
        user = self.request.user
        data = self.request.data
        try:
            product_id = int(data['product_id']) 
        except:  
            return Response(
              {'error':'Product Id must be an integer'},
              status=status.HTTP_404_NOT_FOUND
            )  
        try:
            count = int(data['count']) 
        except:  
            return Response(
              {'error':'Count value must be an integer'},
              status=status.HTTP_404_NOT_FOUND
            )    

        try:
            if not Product.objects.filter(id=product_id).exists():  #SI NO EXISTE EL PRODUCTO
                return Response(
                    {'error': 'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )    

            product = Product.objects.get(id=product_id)         #TRAEMOS EL "PRODUCTO" ENTONCES   
            cart = Cart.objects.get(user=user)                   #TRAEMOS EL "CARRITO" QUE LE PERTENECE

            if not CartItem.objects.filter(cart=cart, product=product).exists():  #SI TAL PRODUCTO NO ESTA EN EL GRUPO ITEMS
                return Response(
                    {'error':'This product is not in your cart'}        #SE SUPONE QUE DEBE EXISTIR PARA ACTUALIZARLO
                )                                                       #OSEA UNA VERIFICACION MAS PARA EL CORRECTO RESULTADO            

            quantity = product.quantify             #SE LA TRAE PARA SABER EL STOCK 

            if count <= quantity:                   #SI LA CANTIDAD A OSTENTAR NO SUPERA EL STOCK_PRODUCT ENTONCES: PROCESAMOS      
                CartItem.objects.filter(
                    product=product, cart=cart
                ).update(count=count)            #ACTUALIZAR ES COMO CREAR PUES EL COMPRADOR ELIGE SI MENOS, MAS O NULO PRODUCTS

                cart_items = CartItem.objects.order_by(      #NUEVA FILTRACION POR RENOVACION                            
                    'product').filter(cart=cart)         

                result = []

                for cart_item in cart_items:
                    item = {}

                    item['id'] = cart_item.id
                    item['count'] = cart_item.count
                    product = Product.objects.get(id=cart_item.product.id)
                    product = ProductSerializer(product)

                    item['product'] = product.data

                    result.append(item)

                return Response({'cart': result}, status=status.HTTP_200_OK)  #MOSTRAMOS LOS RESULTADOS YA ACTUALIZADOS
            else:
                return Response(
                    {'error':'Not Enough of this item in stock'},
                    status=status.HTTP_200_OK
                )    
        except:
            return Response(
                {'error':'Something went wrong when updating cart item'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    #PARA ELIMINAR UN ITEM(PRODUCT DE TU CARRITO)
class RemoveItemView(APIView):
    def delete(self, request, format=None):
        user = self.request.user
        data = self.request.data

        try:
            product_id = int(data['product_id'])
        except:
            return Response(
                {'error':'Product ID must be an integer'},
                status=status.HTTP_404_NOT_FOUND
            )                                

        try:
            if not Product.objects.filter(id=product_id).exists():     #ES UNA VERIFICACION PARA IR VIENDO SI EXISTE EL PROD 1RO
                return Response(
                    {'error':'This product does not exist'},
                    status=status.HTTP_404_NOT_FOUND)

            product = Product.objects.get(id=product_id)
            cart = Cart.objects.get(user=user)

            if not CartItem.objects.filter(cart=cart ,product=product).exists(): #PUES, NO SE PUEDE ELIMINAR ALGO QUE NO EXÍSTE
                return Response(
                    {'error':'This productis not in your cart'},
                    status=status.HTTP_404_NOT_FOUND)            

            CartItem.objects.filter(cart=cart, product=product).delete()

            if not CartItem.objects.filter(cart=cart, product=product).exists():  #COMPROBAMOS QUE SE ELIMINO AL NO ENCONTRARSE

                total_items = int(cart.total_items) - 1  #PARA ACTUALIZAR LA CARRITO
                Cart.objects.filter(user=user).update(total_items=total_items)    

            cart_items = CartItem.objects.order_by('product').filter(cart=cart)

            result = []

            if CartItem.objects.filter(cart=cart).exists():    
                for cart_item in cart_items:
                    item = {}

                    item['id']=cart_item.id
                    item['count']=cart_item.count
                    product = Product.objects.get(id=cart_item.product.id)
                    product = ProductSerializer(product)

                    item['product'] = product.data

                    result.append(item)

            return Response({'cart': result}, status=status.HTTP_200_OK)  #PARA MOSTRAR LOS DATOS YA RENOVADOS 
        except:
            return Response(
                {'error':'Something went wrong when removing item'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )                 


    #VACIAR DE LLENO TODOO DENTRO DE UN CARRO
class EmptyCartView(APIView):
    def delete(self, request, format=None):
        user = self.request.user

        try:
            cart = Cart.objects.get(user=user)

            if not CartItem.objects.filter(cart=cart).exists():   #SE CORROBORA QUE NO TIENE ITEMS EST VACIO Y NO PODEMOS VACIAR
                return Response(
                    {'success':'Cart is already empty'},
                    status=status.HTTP_200_OK)

            CartItem.objects.filter(cart=cart).delete()               #ENTONCES A ELIMINAR LOS ITEMS DEL CARRITO
    
            Cart.objects.filter(user=user).update(total_items=0)      #SETEAMOS DE CART SU CAMPO TOTAL_ITEMS COMO = 0  
    
            return Response(                                          #MOSTRAMOS UN CARTEL DE EXITO EN VACIACION DEL CARRO  
                {'success':'Cart emptied successfully'},
                status=status.HTTP_200_OK)

        except:
            return Response(
                {'error':'Something went wrong emptying cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    #SINCRONIZAR INFORMATION - ACTUALIZACION DE UN GRUPO DE ITEMS 1 A 1 DE LLENO
class SynchCartView(APIView):
    def put(self, request, format=None):
        user = self.request.user
        data = self.request.data

        try:
            cart_items = data['cart_items']

            for cart_item in cart_items:
                cart = Cart.objects.get(user=user)                     #DATO "CART" QUE SE REQUIERE

                try:    
                    product_id = int(cart_item['product_id'])        #DATO ADQUIRIDO POR CART_ITEM "PRODUCT_ID" QUE SE REQUIERE
                except:
                    return Response(
                        {'error':'Product ID must be an integer'},   
                        status=status.HTTP_404_NOT_FOUND)       

                if not Product.objects.filter(id=product_id).exists():
                    return Response(
                        {'error', 'Product with this ID does not exist'},
                        status=status.HTTP_404_NOT_FOUND)

                product = Product.objects.get(id=product_id)
                quantity= product.quantify                               #DATO "STOCK_PRODUCT" QUE SE REQUIERE

                if CartItem.objects.filter(cart=cart, product=product).exists():  #VERIFICACION DE EXISTENCIA

                    item = CartItem.objects.get(cart=cart, product=product)       #ENTONCES LO TRAEMOS A LA VAR "ITEM"
                    count = item.count

                    try:                                                  
                        cart_item_count = int(cart_item['count'])     #VALOR DEL CART_ITEM DEL MAPEO, "LA CANT YA EXISTENTE" 
                    except:
                        cart_item_count = 1                              #DE LO CONTRARIO SE LE ASIGNA 1 UNIDAD 

                    if (cart_item_count + int(count)) <= int(quantity):  #ES PARA SABER SI PODEMOS SUMAR MAS PRODUCTS DEL MISMO
                        updated_count = cart_item_count + int(count)         #POR CUESTIONES DE STOCK
                        CartItem.objects.filter(cart=cart, product=product).update(count=updated_count)    
                else:
                    try:
                        cart_item_count = int(cart_item['count'])
                    except:
                        cart_item_count = 1 #AL NO EXISTIR CARRITO ENDE NO COUNT, SE LE ASIGNA A LA VAR 1 UNIDAD PARA AGREGARLE NEXT

                    if  cart_item_count <= quantity:
                        CartItem.objects.create(product=product, cart=cart, count=cart_item_count)            

                        if CartItem.objects.filter(cart=cart, product=product).exists():          #VERIFICAMOS LA EXISTENCIA   

                            total_items = int(cart.total_items) + 1                         
                            Cart.objects.filter(user=user).update(total_items=total_items)

                return Response(
                    {'success': 'Cart Synchronized'},
                    status=status.HTTP_201_CREATED
                )                
        except:
            return Response(
                {'error': 'Something went wrong when synching cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)







