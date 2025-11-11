from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PerfilProfissional, ImagemPerfil
from .forms import PerfilProfissionalForm, ImagemPerfilForm
from django.shortcuts import render, get_object_or_404


def perfil_detalhe(request, cod_pp):
    perfil = get_object_or_404(PerfilProfissional, id=cod_pp)
    imagens = perfil.imagens.all()  # pega as imagens relacionadas
    return render(request, 'perfil_detalhe.html', {'perfil': perfil, 'imagens': imagens})

@login_required
def criar_ou_editar_perfil(request):
    perfil, _ = PerfilProfissional.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form_perfil = PerfilProfissionalForm(request.POST, instance=perfil)
        form_imagem = ImagemPerfilForm(request.POST, request.FILES)

        if form_perfil.is_valid():
            form_perfil.save()

            # Upload de múltiplas imagens
            imagens = request.FILES.getlist('imagem')
            for i, img in enumerate(imagens):
                ImagemPerfil.objects.create(perfil=perfil, imagem=img, ordem=i)

            return redirect('home')  # pode mudar depois para o perfil público
    else:
        form_perfil = PerfilProfissionalForm(instance=perfil)
        form_imagem = ImagemPerfilForm()

    imagens_existentes = perfil.imagens.all()

    return render(request, 'perfil_profissional_form.html', {
        'form_perfil': form_perfil,
        'form_imagem': form_imagem,
        'imagens': imagens_existentes
    })

