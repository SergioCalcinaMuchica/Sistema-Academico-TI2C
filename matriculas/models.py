from django.db import models
from usuarios.models import Estudiante
from cursos.models import GrupoCurso, GrupoLaboratorio

class Matricula(models.Model):
    # 1. Matricula (id INT AUTO_INCREMENT es automático)
    
    # FK a Estudiante ON DELETE CASCADE
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE, 
        db_column='estudiante_id'
    )
    
    # FK a GrupoCurso ON DELETE CASCADE
    grupo_curso = models.ForeignKey(
        GrupoCurso, 
        on_delete=models.CASCADE, 
        db_column='grupo_curso_id'
    )
    
    estado = models.BooleanField()
    # Campos de notas FLOAT (se mantienen)
    EC1 = models.FloatField(null=True, blank=True)
    EP1 = models.FloatField(null=True, blank=True)
    EC2 = models.FloatField(null=True, blank=True)
    EP2 = models.FloatField(null=True, blank=True)
    EC3 = models.FloatField(null=True, blank=True)
    EP3 = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'matricula_matricula'
        verbose_name = 'Matricula'
        verbose_name_plural = 'Matriculas'
        # UNIQUE KEY (estudiante_id, grupo_curso_id)
        unique_together = ('estudiante', 'grupo_curso')

class MatriculaLaboratorio(models.Model):
    # 1. Matricula Laboratorio (id INT AUTO_INCREMENT es automático)
    
    # FK a Estudiante ON DELETE CASCADE
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE, 
        db_column='estudiante_id'
    )
    
    # FK a GrupoLaboratorio ON DELETE CASCADE
    laboratorio = models.ForeignKey(
        GrupoLaboratorio, 
        on_delete=models.CASCADE, 
        db_column='laboratorio_id'
    )
    
    class Meta:
        db_table = 'matricula_laboratorio'
        verbose_name = 'Matrícula de Laboratorio'
        verbose_name_plural = 'Matrículas de Laboratorio'
        # UNIQUE KEY (estudiante_id, laboratorio_id)
        unique_together = ('estudiante', 'laboratorio')