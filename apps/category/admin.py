from django.contrib import admin
from .models import Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name','parent')         #PARA MOSTRAR EN EL ADMIN DE LA MANERA QUE UNO QUIERE(ORDEN)
    list_display_links = ('id','name','parent')     #POR SI HACES CLICK EN LINK VALLAS A TAL LUGAR
    search_fields = ('name','parent')             #PARA PODER REALIZAR UNA BUSQUEDA POR CATEGORIA
    list_per_page: 25                             #CUANTAS CATEGORIAS QUIERES QUE SE MUESTREN POR PAGINA

admin.site.register(Category, CategoryAdmin)        #ENTONCES REGISTRAMOS TAL CATEGORIA CREADA ARRIBA Y LA TRAIDA    
                                #CON ESTO DECIMOS QUE LA CATEGORIA MODELO PERTENECE A LA CATEGORIA ADMIN CREADA RECIEN ARRIBA            