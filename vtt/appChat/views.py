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

    # opcional: impedir envio para si mesmo
    if recipient == request.user:
        return render(request, 'chat/cannot_message_self.html', {'recipient': recipient})

    # histórico entre os dois
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
            return redirect(reverse('appChat:send_message', args=[recipient.id]))
    else:
        form = MessageForm()

    # marcar lidas as mensagens recebidas ao exibir a conversa
    messages.filter(recipient=request.user, read=False).update(read=True)

    return render(request, 'chat/send_message.html', {
        'recipient': recipient,
        'messages': messages,
        'form': form
    })