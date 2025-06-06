import os

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
            chat.routing.websocket_urlpatterns
        )
    ),
})
