import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import MensagemDM, Sala, Mensagem, SalaPrivada
from django.db.models import Q

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"user_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def nova_dm(self, event):
        await self.send(text_data=json.dumps({
            'type': 'nova_dm',
            'sala_id': event['sala_id'],
            'from_user': event['from_user']
        }))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        sanitized_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', self.room_name)
        self.room_group_name = f'chat_{sanitized_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Função para processar as mensagens do chat
    async def chat_message(self, event):
        # Envia a mensagem para o WebSocket do cliente
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope["user"]

        if user.is_authenticated:
            destinatario_id, sala_id = await self.salvar_mensagem(user, self.room_name, message)

            # Notifica o destinatário se for DM
            if destinatario_id:
                await self.channel_layer.group_send(
                    f"user_{destinatario_id}",  # grupo exclusivo do usuário
                    {
                        'type': 'nova_dm',
                        'sala_id': sala_id,
                        'from_user': user.username,
                    }
                )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username
            }
        )

    async def nova_dm(self, event):
        await self.send(text_data=json.dumps({
            'type': 'nova_dm',
            'sala_id': event['sala_id'],
            'from_user': event['from_user']
        }))

@sync_to_async
def salvar_mensagem(self, usuario, nome_sala, conteudo):
    if '_' in nome_sala:
        id1, id2 = map(int, nome_sala.split('_'))
        sala_dm = SalaPrivada.objects.get(
            Q(usuario1_id=id1, usuario2_id=id2) | Q(usuario1_id=id2, usuario2_id=id1)
        )
        mensagem = MensagemDM.objects.create(usuario=usuario, sala_dm=sala_dm, conteudo=conteudo)

        # Identificar destinatário
        destinatario = sala_dm.usuario2 if sala_dm.usuario1 == usuario else sala_dm.usuario1

        return destinatario.id, sala_dm.id  # retorna quem deve ser notificado e qual sala
    else:
        sala = Sala.objects.get(nome=nome_sala)
        Mensagem.objects.create(usuario=usuario, sala=sala, conteudo=conteudo)
        return None, None

