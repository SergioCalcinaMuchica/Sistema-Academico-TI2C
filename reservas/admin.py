from django.contrib import admin
from .models import Aula, Reserva

# ----------------------------------------------------------------------
# 1. Administración del modelo Aula
# ----------------------------------------------------------------------

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('id',)


# ----------------------------------------------------------------------
# 2. Administración del modelo Reserva
# ----------------------------------------------------------------------

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'fecha_reserva', 
        'hora_inicio', 
        'hora_fin', 
        'aula_display', 
        'profesor_display'
    )
    list_filter = ('fecha_reserva', 'aula__tipo', 'aula')
    search_fields = (
        'aula__id', 
        'profesor__perfil__nombre', 
        'profesor__perfil__id'
    )
    date_hierarchy = 'fecha_reserva' # Navegación por jerarquía de fechas
    
    # Agrupamos los campos para una mejor presentación
    fieldsets = (
        (None, {
            'fields': ('profesor', 'aula')
        }),
        ('Detalles de la Reserva', {
            'fields': ('fecha_reserva', ('hora_inicio', 'hora_fin'))
        }),
    )

    # Métodos personalizados para mostrar información más legible
    
    def aula_display(self, obj):
        """Muestra el código del aula y su tipo."""
        return f"{obj.aula.id} ({obj.aula.get_tipo_display()})"
    aula_display.short_description = 'Aula'

    def profesor_display(self, obj):
        """Muestra el nombre del profesor que hizo la reserva."""
        return obj.profesor.perfil.nombre
    profesor_display.short_description = 'Profesor'