from django.contrib import admin
from .models import Matricula, MatriculaLaboratorio

# ----------------------------------------------------------------------
# 1. Administración del modelo Matricula
# ----------------------------------------------------------------------

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'estudiante_display', 
        'grupo_curso_display', 
        'estado', 
        'EC1', 
        'EP3', 
        'calcular_promedio' # Mostrar una columna de promedio si se define el método
    )
    list_filter = ('grupo_curso__curso__nombre', 'estado')
    search_fields = (
        'estudiante__perfil__nombre', 
        'estudiante__perfil__id', 
        'grupo_curso__curso__nombre'
    )
    
    # Agrupamos los campos para una mejor presentación en el formulario de edición
    fieldsets = (
        (None, {
            'fields': (('estudiante', 'grupo_curso', 'estado'),)
        }),
        ('Notas de Evaluación Continua (EC) y Exámenes Parciales (EP)', {
            'fields': (
                ('EC1', 'EP1'),
                ('EC2', 'EP2'),
                ('EC3', 'EP3'),
            )
        }),
    )

    # Métodos personalizados para mostrar información más legible en list_display
    def estudiante_display(self, obj):
        return f"{obj.estudiante.perfil.nombre} ({obj.estudiante.perfil.id})"
    estudiante_display.short_description = 'Estudiante'

    def grupo_curso_display(self, obj):
        # Muestra el nombre del curso y el grupo (ej: 'COMP101 - G3')
        return f"{obj.grupo_curso.curso.id} - {obj.grupo_curso.grupo}"
    grupo_curso_display.short_description = 'Grupo Curso'
    
    def calcular_promedio(self, obj):
        """Calcula el promedio simple de las notas (solo fines de visualización)."""
        
        # 🚨 CORRECCIÓN CLAVE: Reemplazar None con 0.0 en todas las notas
        # Esto previene el TypeError al sumar None + float.
        notas_con_cero = [
            obj.EC1 or 0.0, 
            obj.EP1 or 0.0, 
            obj.EC2 or 0.0, 
            obj.EP2 or 0.0, 
            obj.EC3 or 0.0, 
            obj.EP3 or 0.0
        ]
        
        num_notas = len(notas_con_cero)
        
        if num_notas == 0:
            return "N/A" # En caso improbable de que no haya notas, aunque siempre serán 6
        
        promedio = sum(notas_con_cero) / num_notas
        return f"{promedio:.2f}"
    calcular_promedio.short_description = 'Promedio'


# ----------------------------------------------------------------------
# 2. Administración del modelo MatriculaLaboratorio
# ----------------------------------------------------------------------

@admin.register(MatriculaLaboratorio)
class MatriculaLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante_display', 'laboratorio_display')
    list_filter = ('laboratorio__grupo_curso__curso__nombre',)
    search_fields = (
        'estudiante__perfil__nombre', 
        'estudiante__perfil__id',
        'laboratorio__grupo_curso__curso__nombre'
    )

    # Métodos personalizados
    def estudiante_display(self, obj):
        return f"{obj.estudiante.perfil.nombre} ({obj.estudiante.perfil.id})"
    estudiante_display.short_description = 'Estudiante'

    def laboratorio_display(self, obj):
        # Muestra el curso y el grupo de laboratorio
        return f"{obj.laboratorio.grupo_curso.curso.id} - {obj.laboratorio.grupo_curso.grupo}"
    laboratorio_display.short_description = 'Laboratorio'