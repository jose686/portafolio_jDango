from django.urls import path
from . import views

app_name = 'blog' # Define un espacio de nombres para tus URLs

urlpatterns = [
    path('', views.lista_articulos, name='lista_articulos'), 
    path('about/', views.sobre_mi, name='sobre_mi'),
    path('post/<slug:slug>/', views.detalle_articulo, name='detalle_articulo'),
    path('contact/', views.contacto, name='contacto'),
]