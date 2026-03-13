import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import MensagemDM, Sala, Mensagem, SalaPrivada
from django.db.models import Q


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')

        # Rejeita conexões não autenticadas
        if not user or not user.is_authenticated:
            await self.close()
            return

        # Rejeita se o user_id da URL não corresponde ao usuário autenticado
        requested_user_id = self.scope['url_route']['kwargs']['user_id']
        if user.id != requested_user_id:
            await self.close()
            return

        self.user_id = requested_user_id
        self.group_name = f"user_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def nova_dm(self, event):
        await self.send(text_data=json.dumps({
            'type': 'nova_dm',
            'sala_id': event['sala_id'],
            'from_user': event['from_user'],
            'unread_count': event.get('unread_count', 1)
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')

        # Rejeita conexões não autenticadas
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        sanitized_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', self.room_name)
        self.room_group_name = f'chat_{sanitized_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    async def receive(self, text_data):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            return

        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, ValueError):
            return

        message = data.get('message', '').strip()

        # Validação server-side: mensagem não pode ser vazia ou exceder 5000 chars
        if not message or len(message) > 5000:
            return

        destinatario_id, sala_id, unread_count = await self.salvar_mensagem(user, self.room_name, message)

        # Se salvar_mensagem retornou None, None, None significa acesso negado ou erro
        if destinatario_id is None and sala_id is None and unread_count is None:
            # Verifica se é DM (deveria ter retornado algo) — não envia a mensagem
            if '_' in self.room_name:
                return

        # Notifica o destinatário se for DM
        if destinatario_id:
            await self.channel_layer.group_send(
                f"user_{destinatario_id}",
                {
                    'type': 'nova_dm',
                    'sala_id': sala_id,
                    'from_user': user.username,
                    'unread_count': unread_count,
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
            'from_user': event['from_user'],
            'unread_count': event.get('unread_count', 1)
        }))

    @sync_to_async
    def salvar_mensagem(self, usuario, nome_sala, conteudo):
        if '_' in nome_sala:
            # Sala de DM — verifica se o usuário é participante
            try:
                parts = nome_sala.split('_')
                if len(parts) != 2:
                    return None, None, None
                id1, id2 = int(parts[0]), int(parts[1])
            except (ValueError, IndexError):
                return None, None, None

            try:
                sala_dm = SalaPrivada.objects.get(
                    Q(usuario1_id=id1, usuario2_id=id2) | Q(usuario1_id=id2, usuario2_id=id1)
                )
            except SalaPrivada.DoesNotExist:
                return None, None, None

            # Verifica se o usuário autenticado é participante da DM
            if usuario.id not in [sala_dm.usuario1_id, sala_dm.usuario2_id]:
                return None, None, None

            mensagem = MensagemDM.objects.create(usuario=usuario, sala_dm=sala_dm, conteudo=conteudo)

            destinatario = sala_dm.usuario2 if sala_dm.usuario1 == usuario else sala_dm.usuario1

            unread_count = MensagemDM.objects.filter(
                sala_dm=sala_dm,
                lida=False
            ).exclude(usuario=destinatario).count()

            return destinatario.id, sala_dm.id, unread_count

        else:
            # Sala de grupo — verifica se o usuário tem acesso
            try:
                sala = Sala.objects.get(nome=nome_sala)
            except Sala.DoesNotExist:
                return None, None, None

            if not sala.publica and sala.dono != usuario:
                # Verifica autorização via sessão
                session = self.scope.get('session', {})
                if not session.get(f"sala_{sala.id}_autorizado"):
                    return None, None, None

            Mensagem.objects.create(usuario=usuario, sala=sala, conteudo=conteudo)
            return None, None, None
