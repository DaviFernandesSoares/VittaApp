from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.core.paginator import Paginator
from django.db.models import Count, Q
from appPerfil.models import PerfilProfissional

def home(request):
    qs = PerfilProfissional.objects.select_related('area_atuacao', 'usuario').prefetch_related('imagens').all()

    # busca livre
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(usuario__name__icontains=q) |
            Q(titulo__icontains=q) |
            Q(cidade__icontains=q) |
            Q(area_atuacao__nome__icontains=q)
        )

    # filtro por área
    area = request.GET.get('area', '').strip()
    if area:
        qs = qs.filter(area_atuacao__nome__iexact=area)

    # ordenação simples
    qs = qs.order_by('-avaliacao_media', 'usuario__name')

    # paginação
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    perfis_page = paginator.get_page(page_number)

    # áreas com contagem (para filtros/chips)
    areas_qs = PerfilProfissional.objects.values('area_atuacao__nome') \
                                         .annotate(count=Count('id')) \
                                         .order_by('-count')
    areas = [(a['area_atuacao__nome'] or 'Outros', a['count']) for a in areas_qs]

    context = {
        'perfis': perfis_page,
        'areas': areas,
        'request': request,
    }
    return render(request, 'home.html', context)

def logout(request):
    auth_logout(request)
    return redirect('home')