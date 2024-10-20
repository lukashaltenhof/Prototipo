import random
from itertools import cycle
from django.core.management.base import BaseCommand
from muertes_hospitalarias.models import Paciente, CausaMuerte, Medico, Hospital
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Poblar datos de pacientes'

    def handle(self, *args, **kwargs):
        # Obtener todos los médicos, hospitales y causas de muerte
        medicos = Medico.objects.all()
        hospitales = Hospital.objects.all()
        causas_muerte = CausaMuerte.objects.all()

        if not medicos.exists() or not hospitales.exists() or not causas_muerte.exists():
            self.stdout.write(self.style.ERROR('Asegúrate de tener médicos, hospitales y causas de muerte pobladas antes de ejecutar este comando.'))
            return

        # Generar datos ficticios para los pacientes
        pacientes_data = [
            {'nombre': 'Juan Pérez', 'genero': 'masculino'},
            {'nombre': 'María González', 'genero': 'femenino'},
            {'nombre': 'Pedro Rodríguez', 'genero': 'masculino'},
            {'nombre': 'Carmen López', 'genero': 'femenino'},
            {'nombre': 'Francisco Silva', 'genero': 'masculino'},
            {'nombre': 'Patricia Fernández', 'genero': 'femenino'},
            {'nombre': 'Diego Valenzuela', 'genero': 'masculino'},
            {'nombre': 'Ana Martínez', 'genero': 'femenino'},
            {'nombre': 'Jaime Torres', 'genero': 'masculino'},
            {'nombre': 'Laura Ramírez', 'genero': 'femenino'}
        ]

        for paciente_data in pacientes_data:
            try:
                # Generar un RUT ficticio y su dígito verificador
                rut_paciente = random.randint(10000000, 19999999)  # RUT ficticio
                dv = self.calcular_dv(rut_paciente)  # Calcular el DV

                # Generar fecha de nacimiento y muerte
                fecha_nacimiento = datetime.now() - timedelta(days=random.randint(20 * 365, 90 * 365))  # Edad entre 20 y 90 años
                fecha_muerte = fecha_nacimiento + timedelta(days=random.randint(1, 30))  # Muerte entre 1 día y 30 días después del nacimiento
                hora_muerte = datetime.now().time()  # Hora actual como hora de muerte

                # Seleccionar causas de muerte y médico aleatorios
                causa_muerte = random.choice(causas_muerte)
                medico = random.choice(medicos)
                hospital = random.choice(hospitales)

                # Crear el paciente
                paciente = Paciente.objects.create(
                    rut_paciente=rut_paciente,
                    dv=dv,
                    nombre=paciente_data['nombre'],
                    fecha_nacimiento=fecha_nacimiento.date(),
                    fecha_muerte=fecha_muerte.date(),
                    hora_muerte=hora_muerte,
                    causa_muerte=causa_muerte,
                    detalles_muerte='Detalles sobre la muerte de ' + paciente_data['nombre'],
                    medico=medico,
                    hospital=hospital,
                    genero=paciente_data['genero']
                )

                self.stdout.write(self.style.SUCCESS(f"Paciente '{paciente.nombre}' creado exitosamente."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al crear paciente: {e}"))

        self.stdout.write(self.style.SUCCESS('Población de pacientes completada.'))

    # Función para calcular el dígito verificador (DV)
    def calcular_dv(self, rut):
        reversed_digits = map(int, reversed(str(rut)))
        factors = cycle(range(2, 8))  # Usamos cycle para repetir los factores de 2 a 7
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        remainder = (-s) % 11
        if remainder == 10:
            return 'K'
        return str(remainder)
