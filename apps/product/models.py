from django.db import models
from datetime import datetime
from apps.category.models import Category
            #TRAEMOS ESTAS 2 IMPORTACIONES PARA PODER MOSTRAR LAS PHOTOS#
from django.conf import settings
domain = settings.DOMAIN

class Product(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='photos/%Y/%m')
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    compare_price = models.DecimalField(max_digits=6, decimal_places=2)  #PRECIO CON DESCUENTO
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantify = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=datetime.now)

    def get_thumbnail(self):
        if self.photo:                  #SÍ EXISTE LA FOTO ENTONCES
            return self.photo.url       #TRAER LA URL COMPLIT DE LA PHOTO
        return ''                       #CASO CONTRARIO NO RETORNAR NADA    

    def __str__(self):          
        return self.name           

