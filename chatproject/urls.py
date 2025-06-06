from django.contrib import admin
from django.urls import path, include
from chat import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('chat/', include('chat.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('convite/', views.enviar_convite, name='enviar_convite'),
    path('convite/aceitar/<int:convite_id>/', views.aceitar_convite_dm, name='aceitar_convite')
]
