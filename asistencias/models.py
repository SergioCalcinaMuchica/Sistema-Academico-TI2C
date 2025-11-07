from django.db import models
from usuarios.models import Estudiante
from cursos.models import GrupoCurso

class RegistroAsistencia(models.Model):
    # 1. Registro Asistencia (id INT AUTO_INCREMENT es automático)
    
    # FK a GrupoCurso ON DELETE CASCADE
    grupo_curso = models.ForeignKey(
        GrupoCurso, 
        on_delete=models.CASCADE, 
        db_column='grupo_curso_id'
    )
    
    ipProfesor = models.CharField(max_length=255)
    fechaClase = models.DateField()
    horaInicioVentana = models.TimeField()

    class Meta:
        db_table = 'RegistroAsistencia'
        verbose_name = 'Registro de Asistencia'
        verbose_name_plural = 'Registros de Asistencia'

class RegistroAsistenciaDetalle(models.Model):
    # 2. Registro Asistencia Detalle (id INT AUTO_INCREMENT es automático)
    
    # FK a RegistroAsistencia ON DELETE RESTRICT (Protege el registro)
    registro_asistencia = models.ForeignKey(
        RegistroAsistencia, 
        on_delete=models.RESTRICT, 
        db_column='id_RegistroAsistencia'
    )
    
    # FK a Estudiante ON DELETE CASCADE
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE, 
        db_column='id_Estudiante'
    )
    
    # estado ENUM
    ESTADO_CHOICES = [
        ('PRESENTE', 'Presente'), 
        ('FALTA', 'Falta')
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)

    class Meta:
        db_table = 'RegistroAsistencia_Detalle'
        verbose_name = 'Detalle de Asistencia'
        verbose_name_plural = 'Detalles de Asistencia'