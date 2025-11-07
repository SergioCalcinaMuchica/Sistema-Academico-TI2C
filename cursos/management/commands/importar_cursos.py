# cursos/management/commands/importar_cursos.py

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from cursos.models import Curso  # Asegúrate de que esta importación sea correcta

class Command(BaseCommand):
    help = 'Importa datos de cursos, incluyendo porcentajes de evaluación, desde un archivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', 
            type=str, 
            help='La ruta completa al archivo CSV de cursos'
        )

    def handle(self, *args, **options):
        file_path = options['csv_file']

        if not os.path.exists(file_path):
            raise CommandError(f'El archivo CSV no fue encontrado en: "{file_path}"')

        self.stdout.write(self.style.NOTICE(f'Iniciando importación de cursos desde: {file_path}'))
        
        try:
            with transaction.atomic():
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Usamos DictReader para leer los datos por nombre de encabezado
                    reader = csv.DictReader(f)
                    
                    cursos_creados = 0
                    
                    for row in reader:
                        
                        # --- 1. Conversión de Tipos de Datos ---
                        # Los campos IntegerField y BooleanField deben convertirse explícitamente.
                        try:
                            creditos = int(row['creditos'])
                            
                            # Conversión de porcentajes (IntegerFields)
                            porcentajes = {
                                'porcentajeEC1': int(row.get('EC1', 0)),
                                'porcentajeEP1': int(row.get('EP1', 0)),
                                'porcentajeEC2': int(row.get('EC2', 0)),
                                'porcentajeEP2': int(row.get('EP2', 0)),
                                'porcentajeEC3': int(row.get('EC3', 0)),
                                'porcentajeEP3': int(row.get('EP3', 0)),
                            }
                            
                            # Opcional: Validar que la suma de porcentajes sea 100
                            suma_total = sum(porcentajes.values())
                            if suma_total != 100:
                                self.stdout.write(self.style.WARNING(
                                    f"Advertencia: Los porcentajes de evaluación para el curso {row['id']} no suman 100% ({suma_total}%)."
                                ))

                        except ValueError as e:
                            self.stdout.write(self.style.ERROR(
                                f"Skipping course {row.get('id', 'N/A')}: Error de valor en un campo numérico. Detalle: {e}"
                            ))
                            continue # Saltar esta fila y continuar con la siguiente

                        # --- 2. Crear o Actualizar el objeto Curso ---
                        curso, created = Curso.objects.update_or_create(
                            id=row['id'], # Usamos el ID como clave primaria para la búsqueda
                            defaults={
                                'nombre': row['nombre'],
                                'creditos': creditos,
                                
                                # Porcentajes
                                **porcentajes, 
                                
                                # URLs (Pueden ser None si están vacías en el CSV)
                                'silabo_url': row.get('silabo_url'),
                                
                                # URLs de Fases
                                'Fase1notaAlta_url': row.get('Fase1notaAlta_url'),
                                'Fase1notaMedia_url': row.get('Fase1notaMedia_url'),
                                'Fase1notaBaja_url': row.get('Fase1notaBaja_url'),
                                'Fase2notaAlta_url': row.get('Fase2notaAlta_url'),
                                'Fase2notaMedia_url': row.get('Fase2notaMedia_url'),
                                'Fase2notaBaja_url': row.get('Fase2notaBaja_url'),
                                'Fase3notaAlta_url': row.get('Fase3notaAlta_url'),
                                'Fase3notaMedia_url': row.get('Fase3notaMedia_url'),
                                'Fase3notaBaja_url': row.get('Fase3notaBaja_url'),
                            }
                        )
                        
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Curso creado: {curso.id} - {curso.nombre}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Curso actualizado: {curso.id} - {curso.nombre}'))
                            
                        cursos_creados += 1

                self.stdout.write(self.style.SUCCESS(f'\n--- Proceso Finalizado ---'))
                self.stdout.write(self.style.SUCCESS(f'Total de registros procesados: {cursos_creados}'))

        except Exception as e:
            # Capturar cualquier otro error que pueda ocurrir durante la lectura/escritura
            raise CommandError(f'Falló la importación debido a un error crítico: {e}')