from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('salas/', views.escolher_sala, name='salas'),
    path('criar-sala/', views.criar_sala, name='criar_sala'),
    path('redirecionar/', views.redirecionar_para_sala, name='redirecionar'),
    path('chat/<str:room_name>/', views.room, name='room'),
    path('entrar-privada/', views.entrar_sala_privada, name='entrar_privada'),
    path('convite/<str:token>/', views.aceitar_convite, name='aceitar_convite'),
    path('dm/cancelar/<int:convite_id>/', views.cancelar_convite_dm, name='cancelar_convite_dm'),
    path('dm/rejeitar/<int:convite_id>/', views.rejeitar_convite_dm, name='rejeitar_convite_dm'),
    path('dm/<int:user_id>/', views.sala_privada_dm, name='sala_privada_dm'),
    path('perfil/', views.perfil, name='perfil'),
]
