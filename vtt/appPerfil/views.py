from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import PerfilProfissional, ImagemPerfil, Avaliacao
from .forms import PerfilProfissionalForm, ImagemPerfilForm
from django.contrib.auth import get_user_model
from django.db.models import Q

# adicione estas importações para o chat
from appChat.models import Message
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from .models import PerfilProfissional, Avaliacao
from django.contrib.auth.decorators import login_required


User = get_user_model
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
@require_POST
def avaliar(request, cod_pp):
    """
    Recebe POST com 'nota' (1-5). Se for HTMX, retorna snippet HTML para #ratingResult.
    """
    # exige autenticação
    if not request.user.is_authenticated:
        if request.htmx:
            return HttpResponse('<div id="ratingResult" style="color:#c00;">Faça login para avaliar.</div>', status=403)
        return JsonResponse({'error': 'auth'}, status=403)

    perfil = get_object_or_404(PerfilProfissional, id=cod_pp)

    # pega nota — prioridade para request.POST (form encoded). hx-vals/htmx normalmente envia form params.
    try:
        nota = int(request.POST.get('nota', 0))
    except (TypeError, ValueError):
        nota = 0

    if nota < 1 or nota > 5:
        if request.htmx:
            return HttpResponse('<div id="ratingResult" style="color:#c00;">Nota inválida.</div>', status=400)
        return JsonResponse({'error': 'nota inválida'}, status=400)

    # evita que o próprio profissional avalie a si mesmo
    if perfil.usuario == request.user:
        if request.htmx:
            return HttpResponse('<div id="ratingResult" style="color:#c00;">Você não pode avaliar seu próprio perfil.</div>', status=403)
        return JsonResponse({'error': 'self'}, status=403)

    # cria ou atualiza a avaliação do usuário
    avaliacao, created = Avaliacao.objects.update_or_create(
        usuario=request.user,
        perfil=perfil,
        defaults={'nota': nota}
    )

    # recalcula média e total de avaliações
    agg = perfil.avaliacoes.aggregate(avg=models.Avg('nota'), total=models.Count('id'))
    media = agg['avg'] or 0
    total = agg['total'] or 0

    # salve nos campos existentes (avaliacao_media, numero_avaliacoes)
    perfil.avaliacao_media = round(float(media), 2)
    perfil.numero_avaliacoes = total
    perfil.save(update_fields=['avaliacao_media', 'numero_avaliacoes'])

    # resposta para HTMX -> devolve snippet HTML que substitui #ratingResult
    if request.htmx:
        html = f'''
            <div id="ratingResult" style="color:#444; margin-bottom:15px;">
                Média atual: <strong>{perfil.avaliacao_media:.2f}</strong> ({perfil.numero_avaliacoes} avaliação{"es" if perfil.numero_avaliacoes != 1 else ""})
            </div>
        '''
        return HttpResponse(html)

    # fallback JSON
    return JsonResponse({'ok': True, 'media': perfil.avaliacao_media, 'total': perfil.numero_avaliacoes})