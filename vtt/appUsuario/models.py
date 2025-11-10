from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class Usuario(AbstractUser):
    # Definindo o related_name para evitar conflitos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups',  # Nome único
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions',  # Nome único
        blank=True
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    username = models.EmailField(max_length=150, unique=True)
    class Meta:
        db_table = 'usuario'
