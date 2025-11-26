from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from chat import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.escolher_sala, name='index'),  # Página principal agora é a de salas
    path('convites/', views.convites, name='convites'),  # Página de convites
    path('register/', views.register, name='register'),
    path('chat/', include('chat.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('convite/', views.enviar_convite, name='enviar_convite'),
    path('convite/aceitar/<int:convite_id>/', views.aceitar_convite_dm, name='aceitar_convite')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])