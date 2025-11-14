from django import forms

class MessageForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Escreva sua mensagem...'
        }),
        max_length=5000,
        label=''
    )