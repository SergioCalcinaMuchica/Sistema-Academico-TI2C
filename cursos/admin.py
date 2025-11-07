from django.contrib import admin
from .models import (
    Curso, 
    GrupoCurso, 
    GrupoTeoria, 
    GrupoLaboratorio, 
    BloqueHorario, 
    TemaCurso
)

# ----------------------------------------------------------------------
# INLINES (Para gestionar modelos relacionados desde el padre)
# ----------------------------------------------------------------------

# 1. Inline para Bloques de Horario (Varios Bloques por GrupoCurso)
class BloqueHorarioInline(admin.TabularInline):
    model = BloqueHorario
    extra = 1 # Muestra 1 campo vacío por defecto
    verbose_name_plural = 'Horarios Asignados'
    
# 2. Inline para Grupo Teoría (Relación 1:1 con GrupoCurso)
class GrupoTeoriaInline(admin.StackedInline):
    model = GrupoTeoria
    max_num = 1 # Solo puede haber un GrupoTeoria por GrupoCurso
    can_delete = False
    verbose_name_plural = 'Es Grupo de Teoría'

# 3. Inline para Grupo Laboratorio (Relación 1:1 con GrupoCurso)
class GrupoLaboratorioInline(admin.StackedInline):
    model = GrupoLaboratorio
    max_num = 1 # Solo puede haber un GrupoLaboratorio por GrupoCurso
    can_delete = False
    verbose_name_plural = 'Es Grupo de Laboratorio'

# ----------------------------------------------------------------------
# MODEL ADMINS
# ----------------------------------------------------------------------

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'creditos')
    search_fields = ('id', 'nombre')
    
    # Agrupamos los campos para que la página de edición no sea tan larga
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'nombre', 'creditos', 'silabo_url')
        }),
        ('Porcentajes de Evaluación', {
            'fields': (
                ('porcentajeEC1', 'porcentajeEP1'), 
                ('porcentajeEC2', 'porcentajeEP2'),
                ('porcentajeEC3', 'porcentajeEP3'),
            )
        }),
        ('Evidencia de Acreditación', {
            'fields': (
                ('Fase1notaAlta_url', 'Fase1notaMedia_url', 'Fase1notaBaja_url'),
                ('Fase2notaAlta_url', 'Fase2notaMedia_url', 'Fase2notaBaja_url'),
                ('Fase3notaAlta_url', 'Fase3notaMedia_url', 'Fase3notaBaja_url'),
            ),
            'classes': ('collapse',), # Esto oculta la sección por defecto, haciendo clic la abre
        }),
    )

@admin.register(GrupoCurso)
class GrupoCursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'curso', 'profesor', 'grupo', 'capacidad')
    list_filter = ('curso', 'profesor', 'grupo')
    search_fields = ('curso__nombre', 'profesor__perfil__nombre')
    
    # Inclusión de las entidades relacionadas directamente en el formulario
    inlines = [
        GrupoTeoriaInline, # Para saber si es de teoría
        GrupoLaboratorioInline, # Para saber si es de laboratorio
        BloqueHorarioInline, # Para asignar sus horarios
    ]

@admin.register(TemaCurso)
class TemaCursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'fecha', 'completado', 'grupo_teoria')
    list_filter = ('grupo_teoria__grupo_curso__curso__nombre', 'completado', 'fecha')
    search_fields = ('nombre',)
    # Usamos autocomplete si hay muchos grupos de teoría
    # raw_id_fields = ('grupo_teoria',) 

# NOTA: Los modelos GrupoTeoria y GrupoLaboratorio no necesitan registro explícito 
# porque se manejan a través del GrupoCursoAdmin con inlines.