# usuarios/admin.py
from django.contrib import admin
from .models import Perfil, Estudiante, Profesor, Secretaria, Administrador

# -------------------------------------------------------------------------
# INLINES (Para la vista de edición/creación del Perfil)
# -------------------------------------------------------------------------

class EstudianteInline(admin.StackedInline):
    # La clase inline debe heredar de TabularInline o StackedInline, no de ModelAdmin
    model = Estudiante
    can_delete = False
    verbose_name_plural = 'Datos de Estudiante'
    fk_name = 'perfil' # Campo de clave foránea en el modelo inline

class ProfesorInline(admin.StackedInline):
    model = Profesor
    can_delete = False
    verbose_name_plural = 'Datos de Profesor'
    fk_name = 'perfil'
    fields = ('es_teoria', 'es_lab')

class SecretariaInline(admin.StackedInline):
    model = Secretaria
    can_delete = False
    verbose_name_plural = 'Datos de Secretaria'
    fk_name = 'perfil'

class AdministradorInline(admin.StackedInline):
    model = Administrador
    can_delete = False
    verbose_name_plural = 'Datos de Administrador'
    fk_name = 'perfil'

# -------------------------------------------------------------------------
# 1. ADMINISTRACIÓN DEL MODELO PERFIL (El modelo principal)
# -------------------------------------------------------------------------

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    # Campos que aparecen en la lista (ajustados a tu modelo)
    list_display = ('id', 'nombre', 'email', 'rol', 'estadoCuenta')
    list_filter = ('rol', 'estadoCuenta') # Solo usamos campos que existen en Perfil

    search_fields = ('id', 'nombre', 'email')

    # No hay campos de solo lectura, ya que no definiste 'date_joined' en el modelo final que me pasaste
    # Si quieres añadir 'date_joined', debes incluirlo en tu models.py y en readonly_fields
    # readonly_fields = ('date_joined',) 

    # Fieldsets para la vista de agregar/editar Perfil
    fieldsets = (
        (None, {'fields': ('id', 'nombre', 'password', 'email')}),
        ('Configuración del Perfil', {'fields': ('rol', 'estadoCuenta')}),
        # Quitamos is_active, is_staff, is_superuser, ya que no están en el modelo final que me enviaste.
    )
    
    # Inlines que se mostrarán en la vista de edición/creación
    inlines = [
        EstudianteInline,
        ProfesorInline,
        SecretariaInline,
        AdministradorInline,
    ]

# -------------------------------------------------------------------------
# 2. MODELO EstudianteAdmin (NECESARIO PARA AUTOCOMPLETE) 🔑
# -------------------------------------------------------------------------
# Registro obligatorio para que los 'autocomplete_fields' de asistencias funcionen.

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('perfil_id', 'nombre_perfil', 'rol_perfil')
    
    # ¡LA CLAVE! Definimos campos de búsqueda en el modelo PERFIL relacionado
    search_fields = ('perfil__id', 'perfil__nombre', 'perfil__email')
    
    def nombre_perfil(self, obj):
        return obj.perfil.nombre
    nombre_perfil.short_description = 'Nombre'

    def rol_perfil(self, obj):
        return obj.perfil.rol
    rol_perfil.short_description = 'Rol'

# -------------------------------------------------------------------------
# 3. ADMINISTRACIÓN DE OTROS MODELOS DE ROL (Para visibilidad y búsqueda)
# -------------------------------------------------------------------------

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('perfil_id', 'es_teoria', 'es_lab')
    search_fields = ('perfil__id', 'perfil__nombre')

@admin.register(Secretaria)
class SecretariaAdmin(admin.ModelAdmin):
    list_display = ('perfil_id',)
    search_fields = ('perfil__id', 'perfil__nombre')

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('perfil_id',)
    search_fields = ('perfil__id', 'perfil__nombre')