from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from .models import Message
from .forms import MessageForm

User = get_user_model()

@login_required
def send_message(request, user_id):
    recipient = get_object_or_404(User, pk=user_id)

    if recipient == request.user:
        return render(request, 'chat/cannot_message_self.html', {'recipient': recipient})

    messages = Message.objects.filter(
        Q(sender=request.user, recipient=recipient) |
        Q(sender=recipient, recipient=request.user)
    ).order_by('created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=form.cleaned_data['content']
            )
            # se a requisição veio via htmx, retornamos só o fragmento de histórico atualizado
            if request.htmx:
                # recarrega mensagens depois da criação (inclui a nova)
                messages = Message.objects.filter(
                    Q(sender=request.user, recipient=recipient) |
                    Q(sender=recipient, recipient=request.user)
                ).order_by('created_at')
                return render(request, 'chat/_history.html', {'messages': messages, 'user': request.user})
            return redirect(reverse('appChat:send_message', args=[recipient.id]))
    else:
        form = MessageForm()

    # marcar lidas ao exibir (aplica tanto para HTMX quanto para normal)
    messages.filter(recipient=request.user, read=False).update(read=True)

    return render(request, 'chat/send_message.html', {
        'recipient': recipient,
        'messages': messages,
        'form': form
    })


@login_required
def message_history(request, user_id):
    """
    Retorna apenas o fragmento HTML do histórico entre request.user e user_id.
    Usado por HTMX para polling.
    """
    other = get_object_or_404(User, pk=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other) |
        Q(sender=other, recipient=request.user)
    ).order_by('created_at')

    # marcar lidas as mensagens recebidas pelo usuário atual
    messages.filter(recipient=request.user, read=False).update(read=True)

    return render(request, 'chat/_history.html', {'messages': messages, 'user': request.user})