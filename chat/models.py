from django.db import models
from django.contrib.auth.models import User
import uuid

class Sala(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    publica = models.BooleanField(default=True)
    senha = models.CharField(max_length=128, blank=True)
    dono = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salas_criadas')
    is_dm = models.BooleanField(default=False)  # Adiciona a flag para DM
    token = models.CharField(max_length=36, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())  # Gera um token único automaticamente
        super().save(*args, **kwargs)

    def __str__(self):
        tipo = 'Pública' if self.publica else 'Privada'
        return f"{self.nome} ({tipo})"
    
    def get_nome_sala(self):
        if self.is_dm:
            return f"{min(self.usuario1.id, self.usuario2.id)}_{max(self.usuario1.id, self.usuario2.id)}"
        return self.nome

class Mensagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)  # Agora se refere ao modelo Sala
    conteudo = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp:%H:%M}] {self.usuario.username}: {self.conteudo}"

class Amizade(models.Model):
    remetente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amizades_enviadas')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='amizades_recebidas')
    aceita = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('remetente', 'destinatario')

    def __str__(self):
        status = "Aceita" if self.aceita else "Pendente"
        return f"{self.remetente} → {self.destinatario} ({status})"

class SalaPrivada(models.Model):
    usuario1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salas_usuario1')
    usuario2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salas_usuario2')
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario1', 'usuario2')

    def __str__(self):
        return f"DM: {self.usuario1.username} & {self.usuario2.username}"

    def get_nome_sala(self):
        return f"{min(self.usuario1.id, self.usuario2.id)}_{max(self.usuario1.id, self.usuario2.id)}"
    
class MensagemDM(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    sala_dm = models.ForeignKey(SalaPrivada, on_delete=models.CASCADE)
    conteudo = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp:%H:%M}] {self.usuario.username}: {self.conteudo}"


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='perfil/', blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
