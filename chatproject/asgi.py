import os
from django.urls import path  # Import necessário
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.consumers import ChatConsumer
# 🔁 ESSENCIAL: configurar o Django ANTES de qualquer import que use settings ou modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatproject.settings')

import django
django.setup()  # ⚠️ Isso carrega os apps e configurações

# Agora podemos importar normalmente
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import chat.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
            path("ws/notifications/<int:user_id>/", NotificationConsumer.as_asgi()),
        )
    ),
})
