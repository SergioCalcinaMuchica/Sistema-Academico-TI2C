from django.db import models
from usuarios.models import Profesor # Necesitamos el modelo Profesor
from reservas.models import Aula # Necesitamos el modelo Aula

class Curso(models.Model):
    # 2. Entidad Curso: id VARCHAR(50) NOT NULL PRIMARY KEY
    id = models.CharField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=255)
    creditos = models.IntegerField()
    
    # Porcentajes de Evaluación
    porcentajeEC1 = models.IntegerField()
    porcentajeEP1 = models.IntegerField()
    porcentajeEC2 = models.IntegerField()
    porcentajeEP2 = models.IntegerField()
    porcentajeEC3 = models.IntegerField()
    porcentajeEP3 = models.IntegerField()
    
    silabo_url = models.CharField(max_length=512, null=True, blank=True)

    Fase1notaAlta_url = models.CharField(max_length=512, null=True, blank=True)
    Fase1notaMedia_url = models.CharField(max_length=512, null=True, blank=True)
    Fase1notaBaja_url = models.CharField(max_length=512, null=True, blank=True)
    Fase2notaAlta_url = models.CharField(max_length=512, null=True, blank=True)
    Fase2notaMedia_url = models.CharField(max_length=512, null=True, blank=True)
    Fase2notaBaja_url = models.CharField(max_length=512, null=True, blank=True)
    Fase3notaAlta_url = models.CharField(max_length=512, null=True, blank=True)
    Fase3notaMedia_url = models.CharField(max_length=512, null=True, blank=True)
    Fase3notaBaja_url = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        db_table = 'cursos_curso'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

class GrupoCurso(models.Model):
    # 3. Entidad Grupo Curso
    id = models.CharField(max_length=50, primary_key=True)
    # FK a Curso ON DELETE RESTRICT
    curso = models.ForeignKey(
        Curso, 
        on_delete=models.RESTRICT,
        db_column='curso_id',
    )
    
    # FK a Profesor ON DELETE SET NULL
    profesor = models.ForeignKey(
        Profesor, 
        on_delete=models.SET_NULL, 
        db_column='profesor_id',
        null=True, blank=True 
    )
    
    grupo = models.CharField(max_length=1) # CHAR(1)
    capacidad = models.IntegerField()

    class Meta:
        db_table = 'cursos_grupo_curso'
        verbose_name = 'Grupo de Curso'
        verbose_name_plural = 'Grupos de Cursos'
        # UNIQUE KEY (curso_id, grupo)

# 3. Entidad Grupo Curso Teoria (Especialización 1:1)
class GrupoTeoria(models.Model):
    # id INT PRIMARY KEY, FK a GrupoCurso ON DELETE CASCADE
    grupo_curso = models.OneToOneField(
        GrupoCurso, 
        on_delete=models.CASCADE, 
        primary_key=True,
        db_column='id' # Mapea la PK/FK a 'id'
    )

    class Meta:
        db_table = 'cursos_grupo_teoria'
        verbose_name = 'Grupo de Teoría'
        verbose_name_plural = 'Grupos de Teoría'

# 4. Entidad Grupo Curso Laboratorio (Especialización 1:1)
class GrupoLaboratorio(models.Model):
    # id INT PRIMARY KEY, FK a GrupoCurso ON DELETE CASCADE
    grupo_curso = models.OneToOneField(
        GrupoCurso, 
        on_delete=models.CASCADE, 
        primary_key=True,
        db_column='id'
    )

    class Meta:
        db_table = 'cursos_grupo_laboratorio'
        verbose_name = 'Grupo de Laboratorio'
        verbose_name_plural = 'Grupos de Laboratorio'

class BloqueHorario(models.Model):
    # 5. Entidad Bloque Horario (id INT AUTO_INCREMENT es automático)
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    
    # dia ENUM
    DIA_CHOICES = [
        ('LUNES', 'Lunes'), ('MARTES', 'Martes'), ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'), ('VIERNES', 'Viernes')
    ]
    dia = models.CharField(max_length=10, choices=DIA_CHOICES)
    
    # FK a GrupoCurso ON DELETE CASCADE
    grupo_curso = models.ForeignKey(
        GrupoCurso, 
        on_delete=models.CASCADE,
        db_column='grupo_curso_id'
    )

    # FK a Aula ON DELETE CASCADE
    aula = models.ForeignKey(
        Aula, 
        on_delete=models.CASCADE,
        db_column='aula_id'
    )

    class Meta:
        db_table = 'cursos_bloque_horario'
        verbose_name = 'Bloque de Horario'
        verbose_name_plural = 'Bloques de Horario'

class TemaCurso(models.Model):
    # 6. Entidad Tema Curso (id INT AUTO_INCREMENT es automático)
    nombre = models.CharField(max_length=255)
    orden = models.IntegerField()
    completado = models.BooleanField() # BOOL
    fecha = models.DateField()
    
    # FK a GrupoTeoria ON DELETE CASCADE
    grupo_teoria = models.ForeignKey(
        GrupoTeoria, 
        on_delete=models.CASCADE,
        db_column='grupo_teoria_id'
    )

    class Meta:
        db_table = 'cursos_tema_curso'
        verbose_name = 'Tema de Curso'
        verbose_name_plural = 'Temas de Curso'