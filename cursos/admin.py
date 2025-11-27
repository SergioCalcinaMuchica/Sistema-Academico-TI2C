from django.contrib import admin
from usuarios.models import Profesor
from .models import (
    Curso, 
    GrupoCurso, 
    GrupoTeoria, 
    GrupoLaboratorio, 
    BloqueHorario, 
    TemaCurso
)

# ======================================================================
#  FILTRO PERSONALIZADO POR PROFESOR EN BLOQUE HORARIO
# ======================================================================

class ProfesorBloqueHorarioFilter(admin.SimpleListFilter):
    title = 'Profesor Asignado'
    parameter_name = 'profesor_asignado'

    def lookups(self, request, model_admin):
        profesor_ids = model_admin.get_queryset(request).values_list(
            'grupo_curso__profesor__perfil_id',
            flat=True
        ).distinct()

        profesores = Profesor.objects.filter(
            perfil_id__in=profesor_ids
        ).order_by('perfil__nombre')

        return [(str(p.perfil_id), str(p)) for p in profesores]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                grupo_curso__profesor__perfil_id=self.value()
            )
        return queryset


# ======================================================================
#  INLINES
# ======================================================================

class BloqueHorarioInline(admin.TabularInline):
    model = BloqueHorario
    extra = 1
    verbose_name_plural = "Horarios Asignados"


class TemaCursoInline(admin.TabularInline):
    """Permite ver los Temas dentro del GrupoTeoría."""
    model = TemaCurso
    extra = 1
    verbose_name_plural = "Temas del Curso"
    ordering = ("orden",)


class GrupoTeoriaInline(admin.StackedInline):
    model = GrupoTeoria
    max_num = 1
    can_delete = False
    verbose_name_plural = "Es Grupo de Teoría"
    inlines = []  # Django no soporta inlines dentro de inlines


class GrupoLaboratorioInline(admin.StackedInline):
    model = GrupoLaboratorio
    max_num = 1
    can_delete = False
    verbose_name_plural = "Es Grupo de Laboratorio"


# ======================================================================
#  MODEL ADMINS
# ======================================================================

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'creditos')
    search_fields = ('id', 'nombre')

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
            'classes': ('collapse',),
        }),
    )


@admin.register(GrupoCurso)
class GrupoCursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'curso', 'profesor', 'grupo', 'capacidad')
    list_filter = ('curso', 'profesor', 'grupo')
    raw_id_fields = ('curso', 'profesor')
    search_fields = ('curso__nombre', 'profesor__perfil__nombre')

    # Inlines SOLO 1 VEZ — corregido
    inlines = [
        GrupoTeoriaInline,
        GrupoLaboratorioInline,
        BloqueHorarioInline,
    ]


@admin.register(TemaCurso)
class TemaCursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'fecha', 'completado', 'grupo_teoria')
    list_filter = (
        'grupo_teoria__grupo_curso__curso__nombre',
        'completado',
        'fecha'
    )
    search_fields = ('nombre',)
    raw_id_fields = ('grupo_teoria',)
    ordering = ('orden',)


@admin.register(BloqueHorario)
class BloqueHorarioAdmin(admin.ModelAdmin):

    def profesor_asignado(self, obj):
        profesor = obj.grupo_curso.profesor
        return profesor if profesor else 'Sin asignar'

    profesor_asignado.short_description = 'Profesor'

    list_display = (
        'grupo_curso', 'profesor_asignado',
        'dia', 'horaInicio', 'horaFin', 'aula'
    )

    list_filter = (
        'dia',
        'grupo_curso__curso__nombre',
        'aula',
        ProfesorBloqueHorarioFilter,
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('grupo_curso__profesor')

    search_fields = (
        'grupo_curso__id',
        'grupo_curso__curso__nombre',
        'aula__nombre',
        'grupo_curso__profesor__perfil__nombre'
    )

    raw_id_fields = ('grupo_curso', 'aula')
    ordering = ('grupo_curso', 'dia')