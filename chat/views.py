from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages
from django.db.models import Q, Max
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password, is_password_usable

from .models import Mensagem, MensagemDM, Perfil, Sala, SalaPrivada, Amizade
from .forms import PerfilForm, SalaForm


def _verificar_senha_sala(senha_digitada, senha_armazenada):
    """Suporta tanto senhas em hash (novas) quanto texto puro (legado)."""
    if is_password_usable(senha_armazenada):
        return check_password(senha_digitada, senha_armazenada)
    # Compatibilidade com senhas antigas em texto puro
    return senha_digitada == senha_armazenada

@login_required
def convites(request):
    """View de convites - mostra convites recebidos e enviados"""
    user = request.user

    # DMs ativas (salas privadas)
    dms = SalaPrivada.objects.filter(Q(usuario1=user) | Q(usuario2=user)).select_related('usuario1__perfil', 'usuario2__perfil').annotate(ultima_mensagem=Max('mensagemdm__timestamp')).order_by('-ultima_mensagem')

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
    """View principal - mostra salas e conversas"""
    user = request.user

    # DMs ativas (para a sidebar)
    dms = SalaPrivada.objects.filter(Q(usuario1=user) | Q(usuario2=user)).select_related('usuario1__perfil', 'usuario2__perfil').annotate(ultima_mensagem=Max('mensagemdm__timestamp')).order_by('-ultima_mensagem')

    for dm in dms:
        dm.unread_count = MensagemDM.objects.filter(sala_dm=dm, lida=False).exclude(usuario=user).count()

    # Salas públicas visíveis a todos
    salas_publicas = Sala.objects.filter(publica=True)

    # Salas privadas onde o usuário é dono
    minhas_salas_privadas = Sala.objects.filter(publica=False, dono=user)

    # Salas privadas que o usuário acessou via senha
    salas_autorizadas_ids = [
        int(chave.split('_')[1])
        for chave, autorizado in request.session.items()
        if chave.startswith("sala_") and autorizado
    ]

    salas_autorizadas = Sala.objects.filter(id__in=salas_autorizadas_ids, publica=False).exclude(dono=user)

    # Todas as salas para a sidebar
    salas = list(salas_publicas) + list(minhas_salas_privadas) + list(salas_autorizadas)

    for sala in salas:
        sala.unread_count = Mensagem.objects.filter(sala=sala, lida=False).exclude(usuario=user).count()

    return render(request, 'chat/salas_new.html', {
        'dms': dms,
        'salas': salas,
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
            # Armazena a senha com hash (nunca em texto puro)
            if sala.senha:
                sala.senha = make_password(sala.senha)
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
    user = request.user

    # Buscar todas as DMs do usuário para a sidebar
    dms = SalaPrivada.objects.filter(Q(usuario1=user) | Q(usuario2=user)).select_related('usuario1__perfil', 'usuario2__perfil').annotate(ultima_mensagem=Max('mensagemdm__timestamp')).order_by('-ultima_mensagem')

    # Contar mensagens não lidas para cada DM
    for dm in dms:
        dm.unread_count = MensagemDM.objects.filter(sala_dm=dm, lida=False).exclude(usuario=user).count()

    # Buscar todas as salas (grupos) do usuário para a sidebar
    salas_publicas = Sala.objects.filter(publica=True)
    minhas_salas_privadas = Sala.objects.filter(publica=False, dono=user)
    salas_autorizadas_ids = [
        int(chave.split('_')[1])
        for chave, autorizado in request.session.items()
        if chave.startswith("sala_") and autorizado
    ]
    salas_autorizadas = Sala.objects.filter(id__in=salas_autorizadas_ids, publica=False).exclude(dono=user)
    salas = list(salas_publicas) + list(minhas_salas_privadas) + list(salas_autorizadas)

    for sala in salas:
        sala.unread_count = Mensagem.objects.filter(sala=sala, lida=False).exclude(usuario=user).count()

    # Verifica se é uma sala DM pelo formato esperado "id1_id2"
    if '_' in room_name:
        try:
            parts = room_name.split('_')
            if len(parts) != 2:
                raise Http404("Sala não encontrada.")
            id1, id2 = int(parts[0]), int(parts[1])
            sala_dm = SalaPrivada.objects.get(
                Q(usuario1_id=id1, usuario2_id=id2) | Q(usuario1_id=id2, usuario2_id=id1)
            )
        except (ValueError, SalaPrivada.DoesNotExist):
            raise Http404("Sala privada de DM não encontrada.")

        # Verifica se o usuário autenticado é participante da DM
        if user not in [sala_dm.usuario1, sala_dm.usuario2]:
            raise Http404("Você não tem acesso a esta conversa.")

        MensagemDM.objects.filter(sala_dm=sala_dm, lida=False).exclude(usuario=user).update(lida=True)
        for dm in dms:
            if dm.id == sala_dm.id:
                dm.unread_count = 0

        other_user = sala_dm.usuario2 if sala_dm.usuario1 == user else sala_dm.usuario1
        mensagens = list(reversed(list(MensagemDM.objects.filter(sala_dm=sala_dm).order_by('-timestamp')[:50])))
        return render(request, 'chat/room.html', {
            'room_name': room_name,
            'mensagens': mensagens,
            'dms': dms,
            'salas': salas,
            'other_user': other_user,
        })

    # Caso contrário, é uma sala de grupo normal (com base no nome da sala)
    sala = get_object_or_404(Sala, nome=room_name)

    if sala.publica or sala.dono == user:
        Mensagem.objects.filter(sala=sala, lida=False).exclude(usuario=user).update(lida=True)
        for s in salas:
            if s.id == sala.id:
                s.unread_count = 0

        mensagens = list(reversed(list(Mensagem.objects.filter(sala=sala).order_by('-timestamp')[:50])))
        return render(request, 'chat/room.html', {
            'room_name': sala.nome,
            'mensagens': mensagens,
            'dms': dms,
            'salas': salas,
            'other_user': None,
        })

    if request.method == 'POST':
        senha = request.POST.get('senha', '')
        if _verificar_senha_sala(senha, sala.senha):
            request.session[f"sala_{sala.id}_autorizado"] = True
            return redirect('room', room_name=sala.nome)
        else:
            messages.error(request, "Senha incorreta!")

    autorizado = request.session.get(f"sala_{sala.id}_autorizado", False)
    if not autorizado:
        return render(request, 'chat/verificar_senha.html', {'sala': sala})

    Mensagem.objects.filter(sala=sala, lida=False).exclude(usuario=user).update(lida=True)
    for s in salas:
        if s.id == sala.id:
            s.unread_count = 0

    mensagens = list(reversed(list(Mensagem.objects.filter(sala=sala).order_by('-timestamp')[:50])))
    return render(request, 'chat/room.html', {
        'room_name': sala.nome,
        'mensagens': mensagens,
        'dms': dms,
        'salas': salas,
        'other_user': None,
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
            if _verificar_senha_sala(senha, sala.senha):
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

@login_required
def buscar_usuarios(request):
    from django.http import JsonResponse

    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'usuarios': []})

    # Busca usuários por username ou first_name/last_name
    usuarios = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:10]  # Limita a 10 resultados e exclui o próprio usuário

    resultado = []
    for user in usuarios:
        resultado.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username
        })

    return JsonResponse({'usuarios': resultado})

@login_required
def configuracoes(request):
    """View de configurações do usuário"""
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    return render(request, 'chat/configuracoes.html', {
        'perfil': perfil
    })
