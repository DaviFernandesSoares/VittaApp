from django import forms
from .models import Usuario


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'telefone', 'cpf']  # Inclua os campos que deseja expor no formulário

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        # Personalize os widgets, labels ou adicione validações adicionais se necessário
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefone'].widget.attrs.update({'class': 'form-control'})
        self.fields['cpf'].widget.attrs.update({'class': 'form-control'})
        self.fields['cpf'].widget.attrs.update({'placeholder': 'CPF'})

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        # Adicione validação personalizada para o CPF se necessário
        if not cpf:
            raise forms.ValidationError('O CPF é obrigatório.')
        return cpf
