from django.urls import path
from .views import ProductDetailView, ListBySearchView,ListProductsView,ListSearchView,ListRelatedView

app_name = "product"
urlpatterns = [
    path('product/<productId>', ProductDetailView.as_view()),      #3 TRAER PRODUCT ESPECIFICO POR ID
    path('get-products',ListProductsView.as_view()),     #1     TRAE REGISTROS INDEXADOS
    path('search', ListSearchView.as_view()),            #2     BUSQUEDA POR CATEGORIA Y/O DESCRIPCION
    path('related/<productId>',ListRelatedView.as_view()),     #4
    path('by/search', ListBySearchView.as_view()),      #5 #5
]