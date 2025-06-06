import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import MensagemDM, Sala, Mensagem, SalaPrivada
from django.db.models import Q

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
            await self.salvar_mensagem(user, self.room_name, message)

        # Envia a mensagem para todos os conectados ao grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # Tipo da mensagem a ser tratada pelo handler
                'message': message,
                'username': user.username  # Envia o nome do usuário junto com a mensagem
            }
        )

    @sync_to_async
    def salvar_mensagem(self, usuario, nome_sala, conteudo):
        if '_' in nome_sala:
            id1, id2 = map(int, nome_sala.split('_'))
            sala_dm = SalaPrivada.objects.get(
                Q(usuario1_id=id1, usuario2_id=id2) | Q(usuario1_id=id2, usuario2_id=id1)
            )
            return MensagemDM.objects.create(usuario=usuario, sala_dm=sala_dm, conteudo=conteudo)
        else:
            sala = Sala.objects.get(nome=nome_sala)
            return Mensagem.objects.create(usuario=usuario, sala=sala, conteudo=conteudo)
