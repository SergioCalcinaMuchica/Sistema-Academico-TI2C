import csv
import io
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Importa el modelo Aula desde tu app de reservas
from reservas.models import Aula 

class Command(BaseCommand):
    help = 'Importa registros de Aulas desde un archivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', 
            type=str, 
            help='La ruta completa al archivo CSV de aulas'
        )

    def handle(self, *args, **options):
        file_path = options['csv_file']

        if not os.path.exists(file_path):
            raise CommandError(f'El archivo CSV no fue encontrado en: "{file_path}"')

        self.stdout.write(self.style.NOTICE(f'Iniciando importación de Aulas desde: {file_path}'))
        
        aulas_procesadas = 0
        aulas_creadas = 0
        aulas_actualizadas = 0
        
        try:
            with transaction.atomic():
                with io.open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    required_fields = ['id', 'tipo']
                    if not all(field in reader.fieldnames for field in required_fields):
                        raise CommandError(f"El CSV debe contener las siguientes columnas: {', '.join(required_fields)}")

                    for row in reader:
                        aula_id = row.get('id', '').strip()
                        aula_tipo = row.get('tipo', '').strip().upper() # Convertir a mayúsculas
                        
                        aulas_procesadas += 1

                        if not aula_id or not aula_tipo:
                            self.stdout.write(self.style.WARNING(
                                f'Fila {aulas_procesadas}: Omitida por ID o Tipo vacío. Datos: {row}'
                            ))
                            continue
                            
                        # Validar que el tipo sea uno de los definidos en el modelo
                        TIPO_VALIDO = [choice[0] for choice in Aula.TIPO_CHOICES]
                        if aula_tipo not in TIPO_VALIDO:
                             self.stdout.write(self.style.ERROR(
                                f'Fila {aulas_procesadas}: Tipo de aula "{aula_tipo}" no válido para ID "{aula_id}". Omitida.'
                            ))
                             continue

                        try:
                            # Usamos update_or_create con la PK (id) para manejar inserción y actualización
                            aula_obj, created = Aula.objects.update_or_create(
                                pk=aula_id, # El ID del CSV es usado como la clave primaria
                                defaults={
                                    'tipo': aula_tipo, 
                                    # Si tu modelo Aula tuviera el campo 'capacidad' y estuviera en el CSV:
                                    # 'capacidad': int(row.get('capacidad', 0)) 
                                }
                            )

                            if created:
                                aulas_creadas += 1
                                self.stdout.write(self.style.SUCCESS(
                                    f'Aula creada: ID {aula_id} ({aula_tipo})'
                                ))
                            else:
                                aulas_actualizadas += 1
                                self.stdout.write(self.style.WARNING(
                                    f'Aula actualizada: ID {aula_id} ({aula_tipo})'
                                ))
                            
                        except Exception as e:
                             self.stdout.write(self.style.ERROR(
                                f'Fila {aulas_procesadas}: Error al procesar Aula ID {aula_id}: {e}'
                            ))

            self.stdout.write(self.style.SUCCESS(f'\n--- Proceso Finalizado ---'))
            self.stdout.write(self.style.SUCCESS(f'Total de registros procesados: {aulas_procesadas}'))
            self.stdout.write(self.style.SUCCESS(f'Aulas creadas: {aulas_creadas}'))
            self.stdout.write(self.style.SUCCESS(f'Aulas actualizadas: {aulas_actualizadas}'))

        except FileNotFoundError:
            raise CommandError(f'Archivo no encontrado en la ruta: "{file_path}"')
        except Exception as e:
            # Errores que podrían ser por problemas de archivo, permisos, etc.
            raise CommandError(f'Fallo la importación debido a un error: {e}')