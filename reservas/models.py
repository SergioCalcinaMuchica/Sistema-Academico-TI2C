from django.db import models
from usuarios.models import Profesor # Necesitamos el modelo Profesor

class Aula(models.Model):
    # 1. Entidad Aula: id VARCHAR(20) NOT NULL PRIMARY KEY
    id = models.CharField(max_length=20, primary_key=True) 
    #capacidad = models.IntegerField()
    
    # tipo ENUM('AULA_NORMAL', 'LABORATORIO')
    TIPO_CHOICES = [
        ('AULA_NORMAL', 'Aula Normal'), 
        ('LABORATORIO', 'Laboratorio')
    ]
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)

    class Meta:
        db_table = 'reservas_aula'
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'

class Reserva(models.Model):
    # 2. Entidad Reserva (id INT AUTO_INCREMENT es automático)
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    # Clave Foránea a la entidad Profesor ON DELETE CASCADE
    profesor = models.ForeignKey(
        Profesor, 
        on_delete=models.CASCADE, 
        db_column='profesor_id'
    )
    
    # Clave Foránea a la entidad Aula ON DELETE CASCADE
    aula = models.ForeignKey(
        Aula, 
        on_delete=models.CASCADE, 
        db_column='aula_id'
    )
    
    class Meta:
        db_table = 'reservas_reservas'
        verbose_name = 'Reserva de Aula'
        verbose_name_plural = 'Reservas de Aulas'