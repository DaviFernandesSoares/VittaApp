"""
URL configuration for vtt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from appUsuario.views import cadastro, login
from appHome.views import home, logout
from appPerfil.views import criar_ou_editar_perfil, perfil_detalhe
from appChat.views import conversation

from appPerfil.views import avaliar

urlpatterns = [
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login, name='login'),
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('logout/', logout, name='logout'),
    path('perfil/', criar_ou_editar_perfil, name='criar_ou_editar_perfil'),
    path('perfil/<int:cod_pp>/', perfil_detalhe, name='perfil_detalhe'),
    path('', include('appAgenda.urls')),
    path('admin/', admin.site.urls),
    path('conversation/<int:user_id>/', conversation, name='conversation'),
    path('', include('appChat.urls')),
    path('avaliar/<int:cod_pp>/', avaliar, name='avaliar'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
