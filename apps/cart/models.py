from django.db import models
from apps.product.models import Product
from django.conf import settings
User = settings.AUTH_USER_MODEL

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_items = models.IntegerField(default=0)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)   #ASOCIACION 1 CON EL CARRITO QUE LO CONTIENE
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  #ASOCIACION 2 CON EL CONTENIDO PROPIO OSEA EL PRODUCTO
    count = models.IntegerField()     
                    