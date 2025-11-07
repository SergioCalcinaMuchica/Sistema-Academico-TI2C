# usuarios/models.py
from django.db import models
# Ya no necesitamos from django.contrib.auth.hashers import make_password

# =========================================================================================
# 1. MODELO PERFIL (Tabla usuarios_perfil, PK VARCHAR(50) - SIN AbstractUser)
# =========================================================================================

class Perfil(models.Model):
    # Definición de Roles (ENUM en SQL)
    ROL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('SECRETARIA', 'Secretaria'),
        ('PROFESOR', 'Profesor'),
        ('ESTUDIANTE', 'Estudiante'),
    ]

    # Campos requeridos por tu SQL
    id = models.CharField(max_length=50, primary_key=True) 
    nombre = models.CharField(max_length=255)
    
    # Almacenamiento de contraseña SIN hasheo
    password = models.CharField(max_length=255) 
    
    email = models.EmailField(unique=True, blank=True, null=True)
    estadoCuenta = models.BooleanField(default=True) 
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)

    class Meta:
        db_table = 'usuarios_perfil'
        verbose_name = 'Perfil Usuario'
        verbose_name_plural = 'Perfiles Usuarios'
        
    def __str__(self):
        return f'{self.id} - {self.nombre} ({self.rol})'

# =========================================================================================
# 2. SUBTABLAS DE ESPECIALIZACIÓN (Usan FK a Perfil) - Sin cambios
# =========================================================================================

class Estudiante(models.Model):
    perfil = models.OneToOneField(
        Perfil, 
        on_delete=models.CASCADE, 
        primary_key=True,
        db_column='perfil_id',
        related_name='estudiante' 
    )
    class Meta:
        db_table = 'usuarios_estudiante'
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
    
    def __str__(self):
        return self.perfil.nombre
        
class Profesor(models.Model):
    perfil = models.OneToOneField(
        Perfil, 
        on_delete=models.CASCADE, 
        primary_key=True,
        db_column='perfil_id',
        related_name='profesor'
    )
    es_teoria = models.BooleanField(default=False)
    es_lab = models.BooleanField(default=False)
    class Meta:
        db_table = 'usuarios_profesor'
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
    
    def __str__(self):
        return self.perfil.nombre

class Secretaria(models.Model):
    perfil = models.OneToOneField(
        Perfil, 
        on_delete=models.CASCADE, 
        primary_key=True,
        db_column='perfil_id',
        related_name='secretaria'
    )
    class Meta:
        db_table = 'usuarios_secretaria'
        verbose_name = 'Secretaria'
        verbose_name_plural = 'Secretarias'
    
    def __str__(self):
        return self.perfil.nombre

class Administrador(models.Model):
    perfil = models.OneToOneField(
        Perfil, 
        on_delete=models.CASCADE, 
        primary_key=True,
        db_column='perfil_id',
        related_name='administrador'
    )
    class Meta:
        db_table = 'usuarios_administrador'
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
    
    def __str__(self):
        return self.perfil.nombre