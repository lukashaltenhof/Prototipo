from django import forms
from .models import Paciente  # Asegúrate de que el modelo Paciente está importado

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['rut_paciente', 'dv', 'nombre', 'fecha_nacimiento', 'fecha_muerte', 'hora_muerte', 'causa_muerte', 'detalles_muerte', 'medico', 'hospital', 'genero']
        widgets = {
            'rut_paciente': forms.TextInput(attrs={'placeholder': 'Ingrese RUT'}),
            'dv': forms.TextInput(attrs={'placeholder': 'Ingrese DV'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ingrese Nombre'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_muerte': forms.DateInput(attrs={'type': 'date'}),
            'hora_muerte': forms.TimeInput(attrs={'type': 'time'}),
            'hospital': forms.Select(attrs={'class': 'form-select'})  # Puedes agregar clases de Bootstrap aquí si quieres
        }
