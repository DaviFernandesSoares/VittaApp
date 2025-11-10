import json
from urllib import request
import requests
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.template.defaultfilters import length
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.urls.base import reverse
from appUsuario.models import Usuario

#salvar codigos redefinição de senha
codes = {}

def verificar_existencia(request):
    email = request.GET.get('email', None)

    resposta = {'email_existe': False}

    if email and Usuario.objects.filter(email=email).exists():
        resposta['email_existe'] = True


    return JsonResponse(resposta)

def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('username')
        email = request.POST.get('email', '').lower()
        senha = request.POST.get('password')

        if Usuario.objects.filter(email=email).exists():
            if request.htmx:
                return HttpResponse('<p class="mensagem erro">E-mail já cadastrado.</p>')
            return render(request, 'cadastro.html', {'erro': 'E-mail já cadastrado.'})

        user = Usuario(username=email, email=email, name=nome)
        user.set_password(senha)
        user.save()

        send_mail(
            'Cadastrado com Sucesso',
            f'Bem-vindo(a) ao BuscaPharma, {nome}!\n\nFaça já seus agendamentos.',
            'buscapharmatcc@gmail.com',
            [email],
            fail_silently=False,
        )

        auth_login(request, user)

        if request.htmx:
            return HttpResponse('<p class="mensagem sucesso">Cadastro realizado com sucesso! Redirecionando...</p><script>setTimeout(()=>window.location.href="/",1500)</script>')

        return redirect('home')

    return render(request, 'cadastro.html')

def login(request):
    if request.user.is_authenticated:
        target = request.GET.get('next', None)
        return redirect(target or 'home')

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        resposta = {'success': False, 'email_existe': False, 'senha': False, 'mensagem': ''}

        if email:
            usuarios = Usuario.objects.filter(email=email)

            if usuarios.exists():
                if usuarios.count() == 1:
                    usuario = usuarios.first()
                    if check_password(senha, usuario.password):
                        auth_login(request,usuario)
                        resposta['success'] = True
                        resposta['mensagem'] = 'Login bem-sucedido.'
                        return JsonResponse(resposta)  # Retorna JSON indicando sucesso
                    else:
                        resposta['senha'] = True
                        resposta['mensagem'] = 'Email ou senha incorretos.'
                else:
                    resposta['email_existe'] = True
                    resposta['mensagem'] = 'Múltiplos usuários encontrados com o mesmo email.'
            else:
                resposta['email_existe'] = True
                resposta['mensagem'] = 'Email não encontrado.'
        else:
            resposta['email_existe'] = True
            resposta['mensagem'] = 'O email é obrigatório.'

        return JsonResponse(resposta)
    return render(request, 'login.html')

def redefinir_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = Usuario.objects.filter(email=email).first()
        if user:
            # Gerar código aleatório
            codigo_verificacao = random.randint(100000, 999999)

            # Armazenar código na variável 'codes' para validar depois
            codes[email] = codigo_verificacao
            # Enviar código por e-mail
            send_mail(
                'Código de Verificação',
                f'Seu código de verificação é: {codigo_verificacao}',
                'buscapharmatcc@gmail.com',  # Remetente
                [email],  # Destinatário
                fail_silently=False,
            )

            # Redirecionar para a página de verificação de código
            return redirect(reverse('verificar_codigo', kwargs={'email': email}))
        else:
            messages.error(request, 'Email não encontrado.')

    return render(request, 'redefinir_senha.html')


def verificar_codigo(request, email):
    if request.method == 'POST':
        codigo_inserido = request.POST.get('codigo')

        # Verificar se o código inserido corresponde ao código enviado
        if codes.get(email) == int(codigo_inserido):
            # Código correto, redirecionar para redefinir senha
            return redirect(reverse('nova_senha', kwargs={'email':email}))
        else:
            messages.error(request, 'Código inválido. Tente novamente')

    return render(request, 'verificar_codigo.html',{'email': email})





def nova_senha(request, email):
    user = Usuario.objects.get(email=email)

    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')

        # Verifica se o campo de nova senha não está vazio
        if not nova_senha:
            messages.error(request, 'O campo nova senha não pode ser vazio.')
            return render(request, 'nova_senha.html', {'email': email})

        # Verifica se a nova senha é igual à senha atual
        if user.check_password(nova_senha):
            messages.error(request, 'A nova senha não pode ser a mesma que a senha antiga.')
            return render(request, 'nova_senha.html', {'email': email})

        # Atualizar a senha
        user.password = make_password(nova_senha)
        user.save()

        return redirect('login')

    return render(request, 'nova_senha.html', {'email': email})
# View de home
def home(request):
    data_atual = timezone.now()


    return render(request, 'home.html')

def logout_usuario(request):
    logout(request)
    return redirect('home')