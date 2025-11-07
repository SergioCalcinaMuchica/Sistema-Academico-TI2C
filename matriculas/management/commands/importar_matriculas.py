import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from matriculas.models import Matricula
# Asegúrate de importar los modelos FK de sus respectivas apps
from usuarios.models import Estudiante # Asumiendo que Estudiante está en 'usuarios'
from cursos.models import GrupoCurso   # Asumiendo que GrupoCurso está en 'cursos'

# Función de ayuda para procesar las notas del CSV
def parse_nota(value):
    """
    Convierte un valor de cadena de nota a float. 
    Retorna None si es nulo, vacío o no es un número válido.
    """
    if value is None or str(value).strip() == '':
        return None
    try:
        # Intentamos convertir a float. Es buena práctica reemplazar comas por puntos.
        return float(str(value).replace(',', '.').strip())
    except ValueError:
        # Si el valor no es numérico, lo tratamos como None (NULL)
        return None

class Command(BaseCommand):
    help = 'Importa registros de matrícula desde un archivo CSV, asociando Estudiantes y Grupos de Curso.'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', 
            type=str, 
            help='La ruta completa al archivo CSV de matrículas'
        )

    def handle(self, *args, **options):
        file_path = options['csv_file']

        if not os.path.exists(file_path):
            raise CommandError(f'El archivo CSV no fue encontrado en: "{file_path}"')

        self.stdout.write(self.style.NOTICE(f'Iniciando importación de matrículas desde: {file_path}'))
        
        registros_procesados = 0
        
        try:
            with transaction.atomic():
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Usamos DictReader para acceder a las columnas por su nombre
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        estudiante_id = row.get('estudiante_id')
                        grupo_curso_id = row.get('grupo_curso_id')
                        
                        if not estudiante_id or not grupo_curso_id:
                            self.stdout.write(self.style.ERROR(
                                f'Fila omitida por datos faltantes (estudiante_id={estudiante_id}, grupo_curso_id={grupo_curso_id})'
                            ))
                            continue
                            
                        try:
                            # 1. Obtener las instancias de los modelos relacionados (FKs)
                            estudiante = Estudiante.objects.get(perfil_id=estudiante_id)
                            grupo_curso = GrupoCurso.objects.get(id=grupo_curso_id)

                            # 2. Crear o actualizar la entidad Matricula
                            matricula, created = Matricula.objects.update_or_create(
                                # Campos usados para la búsqueda (unique_together)
                                estudiante=estudiante,          
                                grupo_curso=grupo_curso,        
                                defaults={
                                    # Estado inicial de la matrícula
                                    'estado': True, 
                                    
                                    # --- LECTURA CONDICIONAL DE NOTAS DEL CSV ---
                                    # Si la columna existe y tiene valor, lo convierte a float; si no, es None
                                    'EC1': parse_nota(row.get('EC1')),
                                    'EP1': parse_nota(row.get('EP1')),
                                    'EC2': parse_nota(row.get('EC2')),
                                    'EP2': parse_nota(row.get('EP2')),
                                    'EC3': parse_nota(row.get('EC3')),
                                    'EP3': parse_nota(row.get('EP3')),
                                    # ---------------------------------------------
                                }
                            )

                            if created:
                                self.stdout.write(self.style.SUCCESS(
                                    f'Matrícula creada: Estudiante ID {estudiante_id} en Grupo ID {grupo_curso_id}'
                                ))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    f'Matrícula actualizada (ya existía): Estudiante ID {estudiante_id} en Grupo ID {grupo_curso_id}'
                                ))
                                
                            registros_procesados += 1
                            
                        except Estudiante.DoesNotExist:
                            self.stdout.write(self.style.ERROR(
                                f'Error en Estudiante ID {estudiante_id}: No existe el estudiante. Fila omitida.'
                            ))
                        except GrupoCurso.DoesNotExist:
                            self.stdout.write(self.style.ERROR(
                                f'Error en GrupoCurso ID {grupo_curso_id}: No existe el grupo de curso. Fila omitida.'
                            ))
                        except Exception as e:
                             self.stdout.write(self.style.ERROR(
                                f'Error al procesar la fila de Estudiante {estudiante_id}, Grupo {grupo_curso_id}: {e}'
                            ))


            self.stdout.write(self.style.SUCCESS(f'\n--- Proceso Finalizado ---'))
            self.stdout.write(self.style.SUCCESS(f'Total de registros procesados con éxito: {registros_procesados}'))

        except Exception as e:
            raise CommandError(f'Fallo la importación debido a un error de archivo o transacción: {e}')