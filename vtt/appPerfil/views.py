from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PerfilProfissional, ImagemPerfil
from .forms import PerfilProfissionalForm, ImagemPerfilForm
from django.contrib.auth import get_user_model
from django.db.models import Q

# adicione estas importações para o chat
from appChat.models import Message
from django.urls import reverse

User = get_user_model()


def perfil_detalhe(request, cod_pp):
    perfil = get_object_or_404(PerfilProfissional, id=cod_pp)
    imagens = perfil.imagens.all()  # pega as imagens relacionadas

    # --- INÍCIO: lógica de chat embutida na página de perfil ---
    messages = None
    chat_error = None

    # Se for POST tentamos criar a mensagem (form simples com campo 'content')
    if request.method == 'POST' and 'content' in request.POST:
        if not request.user.is_authenticated:
            # redireciona para login mantendo próxima página
            return redirect(f"{reverse('login')}?next={request.path}")

        recipient = perfil.usuario
        if recipient == request.user:
            chat_error = "Você não pode enviar mensagem para você mesmo."
        else:
            content = request.POST.get('content', '').strip()
            if content:
                Message.objects.create(sender=request.user, recipient=recipient, content=content)
                # evitar repost (PRG)
                return redirect(reverse('perfil_detalhe', args=[perfil.id]))

    # carregar histórico (se usuário autenticado)
    if request.user.is_authenticated:
        recipient = perfil.usuario
        messages = Message.objects.filter(
            Q(sender=request.user, recipient=recipient) |
            Q(sender=recipient, recipient=request.user)
        ).order_by('created_at')

        # marcar lidas as mensagens que foram para o usuário atual
        messages.filter(recipient=request.user, read=False).update(read=True)
    # --- FIM: lógica de chat ---

    return render(request, 'perfil_detalhe.html', {
        'perfil': perfil,
        'imagens': imagens,
        'messages': messages,
        'chat_error': chat_error,
    })


@login_required
def criar_ou_editar_perfil(request):

    # 1 - tenta buscar perfil; NÃO cria!
    try:
        perfil = PerfilProfissional.objects.get(usuario=request.user)
    except PerfilProfissional.DoesNotExist:
        perfil = None

    if request.method == 'POST':

        # 2 - se não existe perfil, cria agora (momentum certo)
        if perfil is None:
            perfil = PerfilProfissional(usuario=request.user)

        form_perfil = PerfilProfissionalForm(request.POST, instance=perfil)
        form_imagem = ImagemPerfilForm(request.POST, request.FILES)

        if form_perfil.is_valid():
            perfil = form_perfil.save()

            # Upload de múltiplas imagens
            imagens = request.FILES.getlist('imagem')
            for i, img in enumerate(imagens):
                ImagemPerfil.objects.create(perfil=perfil, imagem=img, ordem=i)

            return redirect('home')

    else:
        # GET — não cria nada
        form_perfil = PerfilProfissionalForm(instance=perfil)
        form_imagem = ImagemPerfilForm()

    imagens_existentes = perfil.imagens.all() if perfil else []

    return render(request, 'perfil_profissional_form.html', {
        'form_perfil': form_perfil,
        'form_imagem': form_imagem,
        'imagens': imagens_existentes
    })
