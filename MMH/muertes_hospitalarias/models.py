from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Hospital(models.Model):
    id_hospital = models.AutoField(primary_key=True)
    nombre_hospital = models.CharField(max_length=100)
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    
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

    def __str__(self):
        return self.nombre

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
    rol = models.CharField(max_length=20)  # Por ejemplo, 'recopilador', 'administrador', etc.

    def __str__(self):
        return self.user.username