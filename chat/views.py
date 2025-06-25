from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Mensagem, MensagemDM, Perfil, Sala, SalaPrivada, Amizade
from .forms import PerfilForm, SalaForm

@login_required
def index(request):
    user = request.user

    # DMs ativas (salas privadas)
    dms = SalaPrivada.objects.filter(Q(usuario1=user) | Q(usuario2=user))

    for dm in dms:
        unread_count = MensagemDM.objects.filter(
            sala_dm=dm,
            lida=False
        ).exclude(usuario=user).count()
        dm.unread_count = unread_count

    # Convites pendentes
    convites_recebidos = Amizade.objects.filter(destinatario=user, aceita=False)
    convites_enviados = Amizade.objects.filter(remetente=user, aceita=False)

    return render(request, 'chat/index.html', {
        'dms': dms,
        'convites_recebidos': convites_recebidos,
        'convites_enviados': convites_enviados,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})

@login_required
def escolher_sala(request):
    # Salas públicas visíveis a todos
    salas_publicas = Sala.objects.filter(publica=True)

    # Salas privadas onde o usuário é dono
    minhas_salas_privadas = Sala.objects.filter(publica=False, dono=request.user)

    # Salas privadas que o usuário acessou via senha
    salas_autorizadas_ids = [
        int(chave.split('_')[1])
        for chave, autorizado in request.session.items()
        if chave.startswith("sala_") and autorizado
    ]

    salas_autorizadas = Sala.objects.filter(id__in=salas_autorizadas_ids, publica=False).exclude(dono=request.user)

    return render(request, 'chat/salas.html', {
        'salas_publicas': salas_publicas,
        'minhas_salas_privadas': minhas_salas_privadas,
        'salas_autorizadas': salas_autorizadas,
    })

@login_required
def criar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            sala = form.save(commit=False)
            sala.dono = request.user
            sala.save()
            return redirect('room', room_name=sala.nome)
    else:
        form = SalaForm()
    return render(request, 'chat/criar_sala.html', {'form': form})

@login_required
def redirecionar_para_sala(request):
    if request.method == 'POST':
        nome = request.POST.get('sala')
        return redirect('room', room_name=nome)

@login_required
def room(request, room_name):
    # Verifica se é uma sala DM pelo formato esperado "id1_id2"
    if '_' in room_name:
        try:
            id1, id2 = map(int, room_name.split('_'))
            # Buscar a sala DM com os dois usuários
            sala_dm = SalaPrivada.objects.get(
                Q(usuario1_id=id1, usuario2_id=id2) | Q(usuario1_id=id2, usuario2_id=id1)
            )
        except (ValueError, SalaPrivada.DoesNotExist):
            raise Http404("Sala privada de DM não encontrada.")

        MensagemDM.objects.filter(sala_dm=sala_dm, lida=False).exclude(usuario=request.user).update(lida=True)
        
        # Usamos MensagemDM para mensagens privadas
        mensagens = MensagemDM.objects.filter(sala_dm=sala_dm).order_by('timestamp')[:50]
        return render(request, 'chat/room.html', {
            'room_name': room_name,
            'mensagens': mensagens
        })

    # Caso contrário, é uma sala de grupo normal (com base no nome da sala)
    sala = get_object_or_404(Sala, nome=room_name)

    if sala.publica or sala.dono == request.user:
        mensagens = Mensagem.objects.filter(sala=sala).order_by('timestamp')[:50]
        return render(request, 'chat/room.html', {
            'room_name': sala.nome,
            'mensagens': mensagens
        })

    if request.method == 'POST':
        senha = request.POST.get('senha')
        if senha == sala.senha:
            request.session[f"sala_{sala.id}_autorizado"] = True
            return redirect('room', room_name=sala.nome)
        else:
            messages.error(request, "Senha incorreta!")

    autorizado = request.session.get(f"sala_{sala.id}_autorizado", False)
    if not autorizado:
        return render(request, 'chat/verificar_senha.html', {'sala': sala})

    mensagens = Mensagem.objects.filter(sala=sala).order_by('timestamp')[:50]
    return render(request, 'chat/room.html', {
        'room_name': sala.nome,
        'mensagens': mensagens
    })

@login_required
def sala_privada_dm(request, user_id):
    try:
        outro_usuario = User.objects.get(id=user_id)
        if outro_usuario == request.user:
            raise Http404("Você não pode conversar com você mesmo.")
        
        u1, u2 = sorted([request.user, outro_usuario], key=lambda x: x.id)
        sala, _ = Sala.objects.get_or_create(is_dm=True, usuario1=u1, usuario2=u2)

        return redirect('room', room_name=sala.get_nome_sala())
    except User.DoesNotExist:
        raise Http404("Usuário não encontrado.")
    
@login_required
def entrar_sala_privada(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        senha = request.POST.get('senha')

        try:
            sala = Sala.objects.get(nome=nome, publica=False)
            if sala.senha == senha:
                request.session[f"sala_{sala.id}_autorizado"] = True
                return redirect('room', room_name=nome)
            else:
                messages.error(request, 'Senha incorreta.')
        except Sala.DoesNotExist:
            messages.error(request, 'Sala privada não encontrada.')

    return render(request, 'chat/entrar_privada.html')

@login_required
def aceitar_convite(request, token):
    try:
        sala = Sala.objects.get(token=token)
        request.session[f"sala_{sala.id}_autorizado"] = True
        messages.success(request, f"Você entrou na sala privada '{sala.nome}' via convite!")
        return redirect('room', room_name=sala.nome)
    except Sala.DoesNotExist:
        messages.error(request, "Convite inválido ou expirado.")
        return redirect('salas')

@login_required
def enviar_convite(request):
    if request.method == 'POST':
        id_destinatario = request.POST.get('id_destinatario')
        try:
            destinatario = User.objects.get(id=id_destinatario)
            if destinatario == request.user:
                messages.error(request, "Você não pode se convidar.")
            elif Amizade.objects.filter(remetente=request.user, destinatario=destinatario).exists():
                messages.info(request, "Convite já enviado.")
            else:
                Amizade.objects.create(remetente=request.user, destinatario=destinatario)
                messages.success(request, "Convite enviado!")
        except User.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
        return redirect('index')
    return render(request, 'chat/enviar_convite.html')

@login_required
def aceitar_convite_dm(request, convite_id):
    convite = get_object_or_404(Amizade, id=convite_id, destinatario=request.user)

    convite.aceita = True
    convite.save()

    u1, u2 = sorted([convite.remetente, convite.destinatario], key=lambda u: u.id)
    SalaPrivada.objects.get_or_create(usuario1=u1, usuario2=u2)

    messages.success(request, f"Você agora está em DM com {convite.remetente.username}.")
    return redirect('index')

@login_required
def cancelar_convite_dm(request, convite_id):
    convite = get_object_or_404(Amizade, id=convite_id, remetente=request.user, aceita=False)
    convite.delete()
    messages.info(request, "Convite cancelado.")
    return redirect('index')

@login_required
def rejeitar_convite_dm(request, convite_id):
    convite = get_object_or_404(Amizade, id=convite_id, destinatario=request.user, aceita=False)
    convite.delete()
    messages.info(request, "Convite rejeitado.")
    return redirect('index')

@login_required
def perfil(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')  # Redireciona de volta para a tela de perfil
    else:
        form = PerfilForm(instance=perfil)
    
    return render(request, 'chat/perfil.html', {'form': form, 'perfil': perfil})
