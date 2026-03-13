from django import forms
from .models import Perfil, Sala

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
MAX_PHOTO_SIZE_MB = 5


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto_perfil', 'status', 'biografia']

    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        if foto and hasattr(foto, 'size'):
            if foto.size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(f'A foto não pode ter mais de {MAX_PHOTO_SIZE_MB}MB.')
            content_type = getattr(foto, 'content_type', '')
            if content_type and content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError('Apenas imagens JPEG, PNG, GIF e WebP são permitidas.')
        return foto


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
