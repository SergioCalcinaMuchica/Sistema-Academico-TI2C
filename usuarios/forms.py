from django import forms
from django.core.exceptions import ValidationError
from cursos.models import Curso, GrupoCurso, BloqueHorario
from .models import Profesor
from reservas.models import Aula
from django.db.models import Q

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = [
            'id', 'nombre', 'creditos',
            'porcentajeEC1', 'porcentajeEP1', 'porcentajeEC2', 'porcentajeEP2',
            'porcentajeEC3', 'porcentajeEP3', 'silabo_url'
        ]
    
    def clean_id(self):
        id = self.cleaned_data['id']
        if Curso.objects.filter(id=id).exists():
            raise ValidationError("Ya existe un curso con este ID.")
        return id

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Curso.objects.filter(nombre__iexact=nombre).exists():
            raise ValidationError("Ya existe un curso con este nombre.")
        return nombre


class GrupoCursoForm(forms.ModelForm):
    class Meta:
        model = GrupoCurso
        fields = ['curso', 'grupo', 'capacidad', 'profesor']

    def clean(self):
        cleaned_data = super().clean()
        curso = cleaned_data.get('curso')
        grupo = cleaned_data.get('grupo')

        # Verifica que no exista el mismo grupo para el mismo curso
        if GrupoCurso.objects.filter(curso=curso, grupo=grupo).exists():
            raise ValidationError(f"El grupo {grupo} ya existe para este curso.")

        return cleaned_data


class BloqueHorarioForm(forms.ModelForm):
    class Meta:
        model = BloqueHorario
        fields = ['grupo_curso', 'aula', 'dia', 'horaInicio', 'horaFin']

    def clean(self):
        cleaned_data = super().clean()
        aula = cleaned_data.get('aula')
        dia = cleaned_data.get('dia')
        horaInicio = cleaned_data.get('horaInicio')
        horaFin = cleaned_data.get('horaFin')

        if horaInicio >= horaFin:
            raise ValidationError("La hora de inicio debe ser menor que la hora de fin.")

        # Verifica cruce de horarios en la misma aula
        conflictos = BloqueHorario.objects.filter(
            aula=aula,
            dia=dia
        ).filter(
            Q(horaInicio__lt=horaFin) & Q(horaFin__gt=horaInicio)
        )

        if conflictos.exists():
            raise ValidationError(f"El horario se cruza con otro bloque existente en el aula {aula.id}.")

        return cleaned_data
