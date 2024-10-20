from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date


# Crear modelo para Region
class Region(models.Model):
    nombre_region = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_region

# Crear modelo para Ciudad
class Ciudad(models.Model):
    nombre_ciudad = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_ciudad

# Crear modelo para Comuna
class Comuna(models.Model):
    nombre_comuna = models.CharField(max_length=100)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_comuna

# Modificar modelo Hospital para incluir comuna
class Hospital(models.Model):
    id_hospital = models.AutoField(primary_key=True)
    nombre_hospital = models.CharField(max_length=100)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)  # Cambiar a ForeignKey de Comuna
    

    def __str__(self):
        return self.nombre_hospital

# Continuar con los demás modelos
class Medico(models.Model):
    rut_medico = models.IntegerField(primary_key=True)
    dv = models.CharField(max_length=1)
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=50, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.rut_medico}-{self.dv}"

class CausaMuerte(models.Model):
    id_causa_muerte = models.AutoField(primary_key=True)
    nombre_causa = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.nombre_causa

class Paciente(models.Model):
    rut_paciente = models.IntegerField(primary_key=True)
    dv = models.CharField(max_length=1)
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_muerte = models.DateField(null=True, blank=True)
    hora_muerte = models.TimeField(null=True, blank=True)
    causa_muerte = models.ForeignKey(CausaMuerte, on_delete=models.SET_NULL, null=True)
    detalles_muerte = models.CharField(max_length=255, null=True, blank=True)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
    ]
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, default='masculino')

    def __str__(self):
        return self.nombre

    def clean(self):
        rut_str = str(self.rut_paciente)
        if not rut_str.isdigit() or not (7 <= len(rut_str) <= 8):
            raise ValidationError("El RUT debe tener entre 7 y 8 dígitos sin contar el DV.")

    def calcular_edad(self):
        """Calcula la edad del paciente en años."""
        if self.fecha_nacimiento:
            today = date.today()
            edad = today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
            return edad
        return None  # Retorna None si no hay fecha de nacimiento

class InformeMuerteHospitalaria(models.Model):
    id_informe = models.AutoField(primary_key=True)
    nombre_paciente = models.CharField(max_length=100)
    rut_paciente = models.IntegerField()
    dv = models.CharField(max_length=1)
    causa_muerte = models.CharField(max_length=50)
    rut_medico = models.CharField(max_length=10)
    nombre_medico = models.CharField(max_length=100)
    nombre_hospital = models.CharField(max_length=100)
    fecha_muerte = models.DateField()
    detalles_muerte = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Informe de {self.nombre_paciente}"

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username
