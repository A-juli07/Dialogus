from django import forms
from .models import Perfil, Sala


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto_perfil', 'status', 'biografia']


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'publica', 'senha']
        widgets = {
            'senha': forms.PasswordInput(render_value=True),
        }

    publica = forms.BooleanField(required=False)  # <-- ESSENCIAL

    def clean(self):
        cleaned_data = super().clean()
        publica = cleaned_data.get('publica')
        senha = cleaned_data.get('senha')

        if not publica and not senha:
            self.add_error('senha', 'Salas privadas precisam de uma senha.')
