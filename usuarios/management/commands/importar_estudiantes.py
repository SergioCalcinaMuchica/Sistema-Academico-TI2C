# usuarios/management/commands/importar_estudiantes.py
import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from usuarios.models import Perfil, Estudiante

class Command(BaseCommand):
    help = 'Importa perfiles de estudiantes y sus datos de un archivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', 
            type=str, 
            help='La ruta completa al archivo CSV de estudiantes'
        )

    def handle(self, *args, **options):
        file_path = options['csv_file']

        if not os.path.exists(file_path):
            raise CommandError(f'El archivo CSV no fue encontrado en: "{file_path}"')

        self.stdout.write(self.style.NOTICE(f'Iniciando importación desde: {file_path}'))
        
        # Usamos una transacción para asegurar que, si falla una inserción, todas se reviertan.
        try:
            with transaction.atomic():
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    estudiantes_creados = 0
                    
                    for row in reader:
                        # 1. Crear el objeto Perfil
                        perfil, created = Perfil.objects.update_or_create(
                            id=row['id'], # Usamos el ID como clave de búsqueda
                            defaults={
                                'nombre': row['nombre'],
                                'password': row['password'], # ¡ADVERTENCIA: Contraseña en texto plano!
                                'email': row['email'],
                                'estadoCuenta': True, # Asumimos cuenta activa
                                'rol': 'ESTUDIANTE', # Rol fijo para esta importación
                            }
                        )
                        
                        # 2. Crear o actualizar la entidad Estudiante
                        Estudiante.objects.update_or_create(
                            perfil=perfil,
                            defaults={} # Estudiante no tiene campos adicionales por ahora
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(f'Perfil y Estudiante creados para ID: {perfil.id}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'Perfil y Estudiante actualizados para ID: {perfil.id}'))
                            
                        estudiantes_creados += 1

                self.stdout.write(self.style.SUCCESS(f'\n--- Proceso Finalizado ---'))
                self.stdout.write(self.style.SUCCESS(f'Total de registros procesados: {estudiantes_creados}'))

        except Exception as e:
            raise CommandError(f'Fallo la importación debido a un error: {e}')