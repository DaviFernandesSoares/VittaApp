from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Max
from django.urls import reverse
from .models import Message
from .forms import MessageForm

User = get_user_model()

@login_required
@login_required
def send_message(request, user_id):
    recipient = get_object_or_404(User, pk=user_id)

    if recipient == request.user:
        return render(request, 'cannot_message_self.html', {'recipient': recipient})

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
                return render(request, '_history.html', {'messages': messages, 'user': request.user})
            return redirect(reverse('appChat:send_message', args=[recipient.id]))
    else:
        form = MessageForm()

    # marcar lidas ao exibir (aplica tanto para HTMX quanto para normal)
    messages.filter(recipient=request.user, read=False).update(read=True)

    return render(request, 'send_message.html', {
        'recipient': recipient,
        'messages': messages,
        'form': form
    })


@login_required
def inbox(request):
    """
    Lista as conversas (por remetente) recebidas pelo usuário.
    Mostra último texto e quantidade de não-lidas por conversa.
    """
    # obtém remetentes que já enviaram para o usuário, com último created_at e unread count
    conversations = (
        Message.objects.filter(recipient=request.user)
        .values('sender')
        .annotate(
            last_message=Max('created_at'),
            unread_count=Count('id', filter=Q(read=False))
        )
        .order_by('-last_message')
    )

    # transformar em lista com dados completos do sender e última mensagem
    data = []
    sender_ids = [c['sender'] for c in conversations]
    senders = User.objects.in_bulk(sender_ids)
    for c in conversations:
        sender = senders.get(c['sender'])
        last_msg = (
            Message.objects.filter(sender=sender, recipient=request.user)
            .order_by('-created_at')
            .first()
        )
        data.append({
            'sender': sender,
            'last_message': last_msg,
            'unread_count': c['unread_count']
        })

    return render(request, 'inbox.html', {'conversations': data})


@login_required
def conversation(request, user_id):
    """
    Mostra a conversa entre request.user e user_id (remetente/parte).
    Permite envio (reusa send_message logic) e marca mensagens como lidas.
    """
    other = get_object_or_404(User, pk=user_id)

    # impedir ver conversa de terceiros (quem não seja participante)
    # mas dono do perfil pode ver as conversas onde ele é recipient/sender — a checagem é
    if other == request.user:
        # mostrar inbox ou mensagem de aviso
        return redirect('appChat:inbox')

    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other) |
        Q(sender=other, recipient=request.user)
    ).order_by('created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                sender=request.user,
                recipient=other,
                content=form.cleaned_data['content']
            )
            return redirect(reverse('appChat:conversation', args=[other.id]))
    else:
        form = MessageForm()

    # marcar como lidas as mensagens recebidas pelo usuário nesta conversa
    messages.filter(recipient=request.user, read=False).update(read=True)

    return render(request, 'conversation.html', {
        'other': other,
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

    return render(request, '_history.html', {'messages': messages, 'user': request.user})
