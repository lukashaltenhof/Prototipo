import os
import django
from django.db import IntegrityError

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

from tu_aplicacion.models import Paciente

def prueba_fiabilidad():
    """
    Realiza 5 modificaciones en el modelo Paciente para probar fiabilidad.
    Registra si hubo errores durante el proceso.
    """
    modificaciones_exitosas = 0
    errores = []

    pacientes = [
        {
            'rut_paciente': '12345678',
            'dv': '9',
            'nombre': 'Paciente 1',
            'fecha_nacimiento': '1990-01-01',
            'fecha_muerte': '2024-11-21',
            'hora_muerte': '14:30:00',
            'causa_muerte': 'Infarto',
            'detalles_muerte': 'Infarto masivo',
            'medico': 'Dr. Smith',
            'hospital': 'Hospital Central',
            'genero': 'M',
        },
        {
            'rut_paciente': '87654321',
            'dv': 'K',
            'nombre': 'Paciente 2',
            'fecha_nacimiento': '1980-05-15',
            'fecha_muerte': '2024-11-21',
            'hora_muerte': '10:00:00',
            'causa_muerte': 'Accidente',
            'detalles_muerte': 'Accidente de tránsito',
            'medico': 'Dr. Jones',
            'hospital': 'Hospital Regional',
            'genero': 'F',
        },
        # Agrega otros 3 pacientes similares
    ]

    for i, datos_paciente in enumerate(pacientes, start=1):
        try:
            paciente = Paciente(**datos_paciente)
            paciente.save()
            modificaciones_exitosas += 1
            print(f"Modificación {i}: Exitosa")
        except IntegrityError as e:
            errores.append(f"Modificación {i}: Error de integridad - {e}")
        except Exception as e:
            errores.append(f"Modificación {i}: Error inesperado - {e}")

    print("\nResultados de la prueba de fiabilidad:")
    print(f"Modificaciones exitosas: {modificaciones_exitosas}")
    if errores:
        print("Errores encontrados:")
        for error in errores:
            print(error)
    else:
        print("No se encontraron errores críticos. Prueba exitosa.")

if __name__ == "__main__":
    prueba_fiabilidad()
