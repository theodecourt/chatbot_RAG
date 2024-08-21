from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('apagar/', views.apagar_banco, name='apagar_banco'),
]
