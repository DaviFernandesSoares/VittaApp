from django import forms
from .models import PerfilProfissional, ImagemPerfil

# ---- widget customizado ----
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


# ---- formulário do perfil ----
class PerfilProfissionalForm(forms.ModelForm):
    class Meta:
        model = PerfilProfissional
        fields = ['titulo', 'descricao', 'area_atuacao', 'cidade', 'valor_por_sessao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }


# ---- formulário de imagem ----
class ImagemPerfilForm(forms.ModelForm):
    imagem = forms.ImageField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        required=False
    )

    class Meta:
        model = ImagemPerfil
        fields = ['imagem']
