import csv
import io
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

# Importa tus modelos de las apps correspondientes
from cursos.models import Curso, GrupoCurso, GrupoTeoria, GrupoLaboratorio, BloqueHorario
from usuarios.models import Profesor # Asumo que Profesor está en la app usuarios


class Command(BaseCommand):
    help = 'Importa Grupos de Curso y sus Bloques de Horario desde un archivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV de grupos a importar.')

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        self.stdout.write(self.style.NOTICE(f'Iniciando importación de Grupos de Curso desde: {csv_path}'))

        # 1. Leer y Agrupar Datos
        # La clave del diccionario será el 'grupo_id' (la nueva PK)
        grupos_data = defaultdict(
            # Se añaden curso_id y grupo_letra al defaultdict ya que el key ahora es grupo_id
            lambda: {'curso_id': None, 'profesor_codigo': None, 'grupo': None, 'capacidad': None, 'tipo': None, 'horarios': []}
        )
        
        try:
            with io.open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # SE MODIFICAN los campos requeridos para incluir 'grupo_id'
                required_fields = ['grupo_id', 'curso_id', 'profesor_codigo', 'grupo', 'capacidad', 'tipo', 'dia', 'hora_inicio', 'hora_fin', 'id_Aula']
                if not all(field in reader.fieldnames for field in required_fields):
                    raise CommandError(f"El CSV debe contener las siguientes columnas: {', '.join(required_fields)}")

                for row in reader:
                    # LEER el nuevo ID de la columna 'grupo_id'
                    grupo_id_completo = row['grupo_id'].strip()
                    curso_id = row['curso_id'].strip()
                    grupo_letra = row['grupo'].strip().upper()
                    
                    if not grupo_id_completo or not curso_id or not grupo_letra:
                        self.stdout.write(self.style.WARNING(f"Saltando fila con ID/Curso/Grupo vacío: {row}"))
                        continue

                    key = grupo_id_completo # Usamos la nueva PK como clave de agrupación
                    
                    # Almacenar la información general del grupo (solo se guarda una vez por clave)
                    if grupos_data[key]['profesor_codigo'] is None:
                        grupos_data[key]['curso_id'] = curso_id
                        grupos_data[key]['grupo'] = grupo_letra
                        grupos_data[key]['profesor_codigo'] = row['profesor_codigo'].strip()
                        grupos_data[key]['capacidad'] = int(row['capacidad'])
                        grupos_data[key]['tipo'] = row['tipo'].strip().upper()
                        
                    # Almacenar los bloques de horario
                    grupos_data[key]['horarios'].append({
                        'dia': row['dia'].strip().upper(),
                        'horaInicio': row['hora_inicio'].strip(),
                        'horaFin': row['hora_fin'].strip(),
                        'aula': row['id_Aula'].strip(),
                    })
        except FileNotFoundError:
            raise CommandError(f'Archivo no encontrado en la ruta: "{csv_path}"')
        except ValueError as e:
            # Captura errores si 'capacidad' no es número, o si el formato de hora es incorrecto.
            raise CommandError(f'Error de conversión de valor: {e}')


        # 2. Creación de Objetos en BBDD (Transacción Atómica)
        grupos_creados_count = 0
        horarios_creados_count = 0
        
        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS(f'Datos leídos. Procesando {len(grupos_data)} grupos únicos...'))
            
            # La clave es ahora grupo_id_completo
            for grupo_id_completo, data in grupos_data.items():
                curso_id = data['curso_id']
                grupo_letra = data['grupo']
                
                try:
                    # 2.1. Buscar Foráneas (Curso y Profesor)
                    curso_obj = Curso.objects.get(pk=curso_id)
                    
                    profesor_codigo = data['profesor_codigo']
                    profesor_obj = None
                    if profesor_codigo:
                        try:
                            # Asume que el profesor_codigo es el perfil ID
                            profesor_obj = Profesor.objects.get(perfil__id=profesor_codigo) 
                        except Profesor.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'Advertencia: Profesor con código "{profesor_codigo}" no existe para el grupo {grupo_id_completo}. Se asignará NULL.'))
                            profesor_obj = None
                    
                    # 2.2. Crear o Actualizar GrupoCurso usando la PK explícita (grupo_id_completo)
                    grupo_curso_obj, created = GrupoCurso.objects.get_or_create(
                        pk=grupo_id_completo, # ⬅️ Usa el ID del CSV como Primary Key (PK)
                        defaults={
                            # Estos campos son necesarios para la inserción en el modelo
                            'curso': curso_obj,
                            'profesor': profesor_obj, # Puede ser None
                            'grupo': grupo_letra,
                            'capacidad': data['capacidad']
                        }
                    )
                    
                    # Si ya existe, saltamos la creación de especialización y horarios
                    if not created:
                        self.stdout.write(self.style.WARNING(f'Grupo {grupo_id_completo} ya existe. Saltando especialización y horarios para evitar duplicados.'))
                        continue 

                    grupos_creados_count += 1
                    
                    # 2.3. Crear Especialización (Teoría o Laboratorio)
                    if data['tipo'] == 'TEORIA':
                        GrupoTeoria.objects.create(grupo_curso=grupo_curso_obj)
                    elif data['tipo'] == 'LABORATORIO':
                        GrupoLaboratorio.objects.create(grupo_curso=grupo_curso_obj)
                    else:
                        raise CommandError(f"Tipo de grupo no válido '{data['tipo']}' para {grupo_id_completo}.")

                    # 2.4. Crear Bloques de Horario (Múltiples Bloques)
                    bloques_a_crear = []
                    for horario in data['horarios']:
                        bloques_a_crear.append(
                            BloqueHorario(
                                grupo_curso=grupo_curso_obj,
                                dia=horario['dia'],
                                horaInicio=horario['horaInicio'],
                                horaFin=horario['horaFin'],
                                aula_id=horario['aula'],
                            )
                        )
                    
                    # Inserción masiva de todos los bloques asociados
                    BloqueHorario.objects.bulk_create(bloques_a_crear)
                    horarios_creados_count += len(bloques_a_crear)
                    
                    self.stdout.write(self.style.SUCCESS(f'Grupo {grupo_id_completo} creado exitosamente con {len(bloques_a_crear)} bloques.'))

                except Curso.DoesNotExist:
                    raise CommandError(f'Error: Curso con ID "{curso_id}" no existe. La transacción ha sido revertida.')
                except Exception as e:
                    # Capturamos cualquier otro error crítico
                    raise CommandError(f'Error crítico al crear el grupo {grupo_id_completo}: {e}. La transacción ha sido revertida.')

        self.stdout.write(self.style.SUCCESS('\n--- Proceso Finalizado ---'))
        self.stdout.write(self.style.SUCCESS(f'Grupos de Curso creados: {grupos_creados_count}'))
        self.stdout.write(self.style.SUCCESS(f'Bloques de Horario creados: {horarios_creados_count}'))