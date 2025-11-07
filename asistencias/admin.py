from django.contrib import admin
from .models import RegistroAsistencia, RegistroAsistenciaDetalle

# ----------------------------------------------------------------------
# INLINE (Para mostrar los detalles de la asistencia dentro del registro)
# ----------------------------------------------------------------------

class RegistroAsistenciaDetalleInline(admin.TabularInline):
    model = RegistroAsistenciaDetalle
    extra = 0 # No añade campos vacíos por defecto
    
    # Campos que se muestran y se pueden editar
    fields = ('estudiante', 'estado')
    
    # Campo para búsqueda rápida
    autocomplete_fields = ['estudiante'] 
    
    verbose_name = 'Estado del Estudiante'
    verbose_name_plural = 'Lista de Asistencia'


# ----------------------------------------------------------------------
# 1. Administración del modelo RegistroAsistencia
# ----------------------------------------------------------------------

@admin.register(RegistroAsistencia)
class RegistroAsistenciaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'fechaClase', 
        'grupo_curso_display', 
        'horaInicioVentana',
        'ipProfesor'
    )
    list_filter = ('fechaClase', 'grupo_curso__curso__nombre')
    search_fields = (
        'grupo_curso__curso__nombre', 
        'ipProfesor'
    )
    date_hierarchy = 'fechaClase'
    
    fieldsets = (
        (None, {
            'fields': ('grupo_curso', 'fechaClase')
        }),
        ('Detalles de la Ventana de Registro', {
            'fields': ('horaInicioVentana', 'ipProfesor')
        }),
    )
    
    # Incluimos los detalles de asistencia
    inlines = [
        RegistroAsistenciaDetalleInline,
    ]

    def grupo_curso_display(self, obj):
        """Muestra el nombre del curso y el grupo (ej: 'COMP101 - G3')."""
        return f"{obj.grupo_curso.curso.id} - {obj.grupo_curso.grupo}"
    grupo_curso_display.short_description = 'Grupo Curso'


# ----------------------------------------------------------------------
# 2. Administración del modelo RegistroAsistenciaDetalle (Opcional, si no se usa Inline)
# ----------------------------------------------------------------------

# Se registra por si necesitas gestionarlo de forma independiente, aunque el Inline es preferido.
@admin.register(RegistroAsistenciaDetalle)
class RegistroAsistenciaDetalleAdmin(admin.ModelAdmin):
    list_display = ('id', 'registro_asistencia', 'estudiante_display', 'estado')
    list_filter = ('estado', 'registro_asistencia__fechaClase')
    search_fields = ('estudiante__perfil__nombre', 'registro_asistencia__id')

    def estudiante_display(self, obj):
        """Muestra el nombre del estudiante."""
        return obj.estudiante.perfil.nombre
    estudiante_display.short_description = 'Estudiante'