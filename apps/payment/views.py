from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.cart.models import Cart, CartItem
from apps.coupons.models import FixedPriceCoupon, PercentageCoupon
from apps.orders.models import Order, OrderItem
from apps.product.models import Product
from apps.shipping.models import Shipping
from django.core.mail import send_mail
import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=settings.BT_ENVIRONMENT,
        merchant_id= settings.BT_MERCHANT_ID,
        public_key= settings.BT_PUBLIC_KEY,
        private_key= settings.BT_PRIVATE_KEY
    )
)


class GenerateTokenView(APIView):
    def get(self, request, format=None):
        try:
            token = gateway.client_token.generate()

            return Response(
                {'braintree_token': token},
                status=status.HTTP_200_OK)
        except:
            return Response(
                {'error': 'Something went wrong when retrieving braintree token'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPaymentTotalView(APIView):
    def get(self, request, format=None):
        user = self.request.user

        tax = 0.18

        shipping_id = request.query_params.get('shipping_id')                        
        shipping_id = str(shipping_id)   

        coupon_name = request.query_params.get('coupon_name')
        coupon_name = str(coupon_name)

        try:
            cart = Cart.objects.get(user=user)

            if not CartItem.objects.filter(cart=cart).exists():           #SÍ NO EXISTEN CART_ITEMS NO PUEDE HABER TOTALES
                return Response(
                    {'error': 'Need to have items in cart'},
                    status=status.HTTP_404_NOT_FOUND)

            cart_items = CartItem.objects.filter(cart=cart)               #PASADO LA VERIFICACION DE ARRIBA TRAEMOS LOS ITEMS   

            for cart_item in cart_items:
                if not Product.objects.filter(id=cart_item.product.id).exists(): #VERIFICACION OZADA SI EL ITEM/PRODUCT EXISTE   
                    return Response(
                        {'error': 'A product with ID provided does not exist'},
                        status=status.HTTP_404_NOT_FOUND)

                if int(cart_item.count) > int(cart_item.product.quantify): #VERIFS LA CANTIDAD A COMPRAR NO PUEDE SUPERAR EL STOCK
                    return Response(
                        {'error':'Not enough items in stock'},
                        status=status.HTTP_200_OK
                    )        

                total_amount = 0.0
                total_compare_amount = 0.0

                for cart_item in cart_items:                                   #AHORA YA PODEMOS REALIZAR EL PROCESO DE TOTAL
                    total_amount += (float(cart_item.product.price)
                                     * float(cart_item.count))
                    total_compare_amount += (float(cart_item.product.compare_price)                                        
                                             * float(cart_item.count))               

                total_compare_amount = round (total_compare_amount, 2)       #REDONDEAMOS                                        
                original_price = round(total_amount, 2)                                             

                #Cupones
                if coupon_name != '':
                    if FixedPriceCoupon.objects.filter(name__iexact=coupon_name).exists():
                        fixed_price_coupon = FixedPriceCoupon.objects.get(name=coupon_name)
                    discount_amount= float(fixed_price_coupon.discount_price)
                    if discount_amount < total_amount:
                        total_amount -= discount_amount
                        total_after_coupon = total_amount
                    elif PercentageCoupon.objects.filter(name__iexact=coupon_name).exists():
                        percentage_coupon = PercentageCoupon.objects.get(name=coupon_name)
                        discount_percentage = float(percentage_coupon.discount_percentage)

                        if discount_percentage > 1 and discount_percentage < 100:
                            total_amount -= (total_amount * (discount_percentage / 100))
                            total_after_coupon = total_amount

                total_after_coupon = round(total_after_coupon, 2)

                #Impúesto estimado
                estimated_tax = round(total_amount * tax, 2)

                total_amount += (total_amount * tax)      #ES PRETOTAL PORQUE FALTA AGREGARLE OTRO IMPUESTO DE SHIPPING AUN

                shipping_cost = 0.0
                #verificar el envio sea valido
                if Shipping.objects.filter(id__iexact=shipping_id).exists():
                     #agregar shipping a total amount
                     shipping = Shipping.objects.get(id=shipping_id)
                     shipping_cost = shipping.price
                     total_amount += float(shipping_cost)   

                total_amount = round(total_amount, 2)     #AHORA ES EL TOTAL FINAL COMPLIT CON TODOS LOS RECARGOS

                return Response(
                    {'original_price': f'{original_price: .2f}',                 #TOTAL DE ORIGEN
                     'total_after_coupon': f'{total_after_coupon: .2f}',
                     'total_amount': f'{total_amount: .2f}',                     #TOTAL CON IMPUESTO Y SHIPPING      
                     'total_compare_amount': f'{total_compare_amount: .2f}',     #TOTAL CON DESCUENTO 
                     'estimated_tax': f'{estimated_tax: .2f}',                   #IMPUESTO ESTIMADO   
                     'shipping_cost': f'{shipping_cost: .2f}',                      
                    },
                    status=status.HTTP_200_OK)    

        except:
            return Response(
                {'error': 'Something went wrong when retrieving payment total information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)        


class ProcessPaymentView(APIView):
    def post(self, request, formart=None):
        user = self.request.user
        data = self.request.data

        tax = 0.18

        nonce = data['nonce']  #SERA PARA VERIFICAR LOS PAGOS
        shipping_id = str(data['shipping_id'])  #AQUI SOLO SE PUEDE RECIBIR STR A SHIPPING_ID POR DEFECTO 
        coupon_name = str(data['coupon_name'])

        #CUPON NAME

        full_name = data['full_name']
        address_line_1 = data['address_line_1']    
        address_line_2 = data['address_line_2']    
        city = data['city']
        state_province_region = data['state_province_region']
        postal_zip_code = data['postal_zip_code']
        country_region = data['country_region']
        telephone_number = data['telephone_number']

        if not Shipping.objects.filter(id__iexact=shipping_id).exists():
            return Response(
                {'error':'Invalid shipping option'},
                status=status.HTTP_404_NOT_FOUND)

        cart = Cart.objects.get(user=user)

        if not CartItem.objects.filter(cart=cart).exists():
            return Response(
                {'error':'Need to have items in cart'},                   #SE SUPONE QUE DEBEMOS FACTURAR ALGO POR ELLO ERROR
                status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)                   #TRAEMOS LOS CART_ITEMS   

        #revizar stock

        for cart_item in cart_items:                                    #ITEM POR ITEM
            if not Product.objects.filter(id=cart_item.product.id).exists():      #VERIF DE EXISTENCIA DEL PRODUCT EN CUESTION
                return Response(
                    {'error': 'Transaction failed, a product ID does not exist'},
                    status=status.HTTP_404_NOT_FOUND) 

            if int(cart_item.count) > int(cart_item.product.quantify):         #VERIF DE STOCK VALIDO PARA SER LLEVADO EL PROCESO
                return Response(
                    {'error': 'Not enough items in stock'},
                    status=status.HTTP_200_OK)

        total_amount = 0.0                                                  

        for cart_item in cart_items:                                   #AHORA QUE PASARON TODAS LAS VERIFICACIONES PROCESAMOS                          
            total_amount += (float(cart_item.product.price)            #PAGO DE CADA ITEM SE SUMANDO AL TOTAL
                            *float(cart_item.count))

        #Cupones
        if coupon_name != '':
            if FixedPriceCoupon.objects.filter(name__iexact= coupon_name).exists():
                fixed_price_coupon = FixedPriceCoupon.objects.get(name=coupon_name)
                discount_amount= float(fixed_price_coupon.discount_price)
                
                if discount_amount < total_amount:
                        total_amount -= discount_amount

            elif PercentageCoupon.objects.filter(name__iexact=coupon_name).exists():
                percentage_coupon = PercentageCoupon.objects.get(name=coupon_name)
                discount_percentage = float(percentage_coupon.discount_percentage)

                if discount_percentage > 1 and discount_percentage < 100:
                    total_amount -= (total_amount * (discount_percentage / 100))
                
                        
        # descuento  

        total_amount += (total_amount*tax)                             #MAS IMPUESTO

        shipping = Shipping.objects.get(id=int(shipping_id))    #ANTES LO RECIBIMOS POR OBLIGACION COMO STR A SHIPPING_ID, AQUI INT

        shipping_name = shipping.name
        shipping_time = shipping.time_to_delibery
        shipping_price = shipping.price

        total_amount += float(shipping_price)                   #SUMAMOS AHORA EL ENVIO AL TOTAL
        total_amount = round(total_amount, 2)                   #REDONDEAMOS EN 2 DECIMALES    

        try:
            #Crear transaction con braintree
            newTransaction = gateway.transaction.sale(        #LE PASAMOS LOS DATOS "TOTAL_PAGAR Y NONCE" A BRAINTREE POR BODY
                {
                  'amount': str(total_amount),
                  'payment_method_nonce': str(nonce['nonce']),
                  'options': {
                    'submit_for_settlement': True    #para que puedan verificar errores de pago
                  }      
                }
            )                
        except:
            return Response(
                {'error':'Error processing the transaction'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

        if newTransaction.is_success or newTransaction.transaction:   #SI TODOO OK ACTUALIZAMOS LA BASE DE DATOS
            for cart_item in cart_items:                              #RECORRIENDO ITEM A ITEM PROCESAMOS
         
                update_product = Product.objects.get(id=cart_item.product.id)
                #cant que queda desp de la compra en stock del producto Resta
                quantity = int(update_product.quantify) - int(cart_item.count)        
                #cant total que se logro vender en total(actualizacion) Suma
                sold = int(update_product.sold) + int(cart_item.count)
                #ACTUALIZACION DEL PRODUCTO
                Product.objects.filter(id=cart_item.product.id).update(quantify=quantity, sold=sold)  #PLASMAMOS CAMBIOS EN LA BD

            #CREAMOS LA ORDEN 
            try:
                order = Order.objects.create(
                    user=user,
                    transaction_id=newTransaction.transaction.id,  #TRANSACCION DONDE FIGURA EL TOTAL ABSOLUTO A PAGAR
                    amount=total_amount,
                    full_name=full_name,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    city=city,
                    state_province_region=state_province_region,
                    postal_zip_code=postal_zip_code,
                    country_region=country_region,
                    telephone_number=telephone_number,
                    shipping_name=shipping_name,
                    shipping_time=shipping_time,
                    shipping_price=float(shipping_price)
                )    
            except:
                return Response(
                    {'error': 'Transaction succeded but failed to create the order'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )   

            for cart_item in cart_items:     #creamos la orden_item para cada producto
                try:
                    product = Product.objects.get(id=cart_item.product.id)

                    OrderItem.objects.create(
                        product=product,
                        order=order,
                        name=product.name,
                        price=cart_item.product.price,
                        count=cart_item.count
                    )
                except:
                    return Response(
                        {'error': 'Transaction succeeded and order created, but failed to create an order item'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )  

                #ENVIAMOS AL CLIENTE MSN POR MAIL DE SU PETICION DE COMPRA E INFORMA QUE SE ESTA PROCENSANDO
            try:
                send_mail(
                    'Your Order Details',
                    'Hey ' + full_name + ','
                    + '\n\nWe recieved your order!'
                    + '\n\nGive us some time to process your order and ship it out to you.'
                    + '\n\nYou can go on your user dashboard to check the status of your order.'
                    + '\n\nSincerely,'
                    + '\nShop Time',
                    'rash@ninerogues.com',
                    [user.email],
                    fail_silently=False
                )
            except:
                return Response(
                    {'error': 'Transaction succeeded and order created, but failed to send email'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            #DEBEMOS VACIAR SU CARRITO AHORA
            try:
                # Vaciar carrito de compras
                CartItem.objects.filter(cart=cart).delete()

                # Actualizar carrito
                Cart.objects.filter(user=user).update(total_items=0)  #ACTUALIZAMOS SU CARRO UNICO LA PROPIEDAD TOTAL_ITEMS=0
            except:
                return Response(
                    {'error': 'Transaction succeded and order successful, but failed to clear cart'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )    

            return Response(
                {'success': 'Transaction successful and order was created'},
                status=status.HTTP_200_OK
            )   
        else:
            return Response(
                {'error': 'Transaction failed'},
                status=status.HTTP_400_BAD_REQUEST
            )