from django.db import models
from django.conf import settings

# ===========================
# ÁREA DE ATUAÇÃO
# ===========================
class AreaAtuacao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Área de Atuação"
        verbose_name_plural = "Áreas de Atuação"
        ordering = ['nome']

    def __str__(self):
        return self.nome
class TiposDeAreas(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nome

# ===========================
# PERFIL PROFISSIONAL
# ===========================
class PerfilProfissional(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Relaciona-se com o usuário Django padrão
        on_delete=models.CASCADE,
        related_name='perfil_profissional'
    )
    area_atuacao = models.ForeignKey(
        AreaAtuacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfis'
    )
    titulo = models.CharField(max_length=120, help_text="Ex: Personal Trainer, Fisioterapeuta, Nutricionista")
    descricao = models.TextField(help_text="Fale um pouco sobre seu trabalho e formação.")
    cidade = models.CharField(max_length=100, blank=True, null=True)
    valor_por_sessao = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    avaliacao_media = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Perfil Profissional"
        verbose_name_plural = "Perfis Profissionais"
        ordering = ['usuario__username']

    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"


# ===========================
# IMAGENS DO PERFIL
# ===========================
class ImagemPerfil(models.Model):
    perfil = models.ForeignKey(
        PerfilProfissional,
        on_delete=models.CASCADE,
        related_name='imagens'
    )
    imagem = models.ImageField(upload_to='perfis/')
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Imagem do Perfil"
        verbose_name_plural = "Imagens do Perfil"
        ordering = ['ordem']

    def __str__(self):
        return f"Imagem de {self.perfil.usuario.username} (ordem {self.ordem})"
