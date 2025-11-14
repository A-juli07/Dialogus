from django import forms
from .models import Perfil, Sala


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto_perfil', 'status', 'biografia']


class SalaForm(forms.ModelForm):
    descricao = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Descrição',
        help_text='Descreva sobre o que é este grupo (opcional)'
    )
    privada = forms.BooleanField(
        required=False,
        initial=False,
        label='Sala Privada'
    )

    class Meta:
        model = Sala
        fields = ['nome', 'senha']
        widgets = {
            'senha': forms.PasswordInput(render_value=True),
        }

    def clean(self):
        cleaned_data = super().clean()
        privada = cleaned_data.get('privada')
        senha = cleaned_data.get('senha')

        # Se privada for True, publica deve ser False, e vice-versa
        cleaned_data['publica'] = not privada

        if privada and not senha:
            self.add_error('senha', 'Salas privadas precisam de uma senha.')

        return cleaned_data
