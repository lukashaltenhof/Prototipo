from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Paciente
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .forms import PacienteForm
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Count, Avg
from collections import defaultdict
from datetime import date

# Listar los pacientes
class PacienteListView(ListView):
    model = Paciente
    template_name = 'muertes_hospitalarias/paciente_list.html'
    paginate_by = 10  # Número de pacientes por página

    def get_queryset(self):
        queryset = super().get_queryset()  # Obtiene todos los pacientes
        query = self.request.GET.get('q')  # Busca el parámetro 'q' en la URL

        if query:
            # Filtra los pacientes que contengan la cadena de búsqueda en su nombre (case insensitive)
            queryset = queryset.filter(nombre__icontains=query)
        
        return queryset

# Crear un nuevo paciente
class PacienteCreateView(CreateView):
    model = Paciente
    form_class = PacienteForm  # Usa tu formulario personalizado
    template_name = 'muertes_hospitalarias/paciente_form.html'
    success_url = reverse_lazy('paciente-list')

    def form_valid(self, form):
        # Aquí puedes añadir lógica adicional antes de guardar
        return super().form_valid(form)

    def form_invalid(self, form):
        # Maneja el caso donde el formulario es inválido
        return self.render_to_response({'form': form})

# Editar un paciente
class PacienteUpdateView(UpdateView):
    model = Paciente
    form_class = PacienteForm  # Usa tu formulario personalizado
    template_name = 'muertes_hospitalarias/paciente_form.html'
    success_url = reverse_lazy('paciente-list')

    def form_valid(self, form):
        # Aquí puedes añadir lógica adicional antes de guardar
        return super().form_valid(form)

    def form_invalid(self, form):
        # Maneja el caso donde el formulario es inválido
        return self.render_to_response({'form': form})

# Eliminar un paciente
class PacienteDeleteView(DeleteView):
    model = Paciente
    template_name = 'muertes_hospitalarias/paciente_confirm_delete.html'
    success_url = reverse_lazy('paciente-list')

# Detalles del paciente
class PacienteDetailView(DetailView):
    model = Paciente
    template_name = 'muertes_hospitalarias/paciente_detail.html'  # Asegúrate de que esta ruta sea correcta

# Vista de login con verificación de roles basados en grupos
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Verificar si el usuario pertenece al grupo 'recopilador'
            if user.groups.filter(name='recopilador').exists():
                return redirect('paciente-list')  # Redirige al mantenedor de pacientes
            # Verificar si el usuario pertenece al grupo 'analista'
            elif user.groups.filter(name='analista').exists():
                return redirect('analisis')  # Redirige a otra vista para analista
            else:
                # Si el usuario no pertenece a ningún grupo conocido
                return redirect('default-vista')  # Cambia esto según tu lógica
        else:
            # Credenciales incorrectas
            return render(request, 'login.html', {'error': 'Credenciales incorrectas'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('login')  # Redirige a la página de login después de cerrar sesión

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def analisis_estadistico(request):
    # Total de pacientes
    total_pacientes = Paciente.objects.count()

    # Muertes por género
    muertes_por_genero = Paciente.objects.values('genero').annotate(
        count=Count('rut_paciente')
    ).annotate(
        porcentaje=(Count('rut_paciente') * 100.0 / total_pacientes)
    )

    # Muertes por hospital
    muertes_por_hospital = Paciente.objects.values('hospital__nombre_hospital').annotate(
        count=Count('rut_paciente')
    ).annotate(
        porcentaje=(Count('rut_paciente') * 100.0 / total_pacientes)
    )

    # Muertes por causa
    muertes_por_causa = Paciente.objects.values('causa_muerte__nombre_causa').annotate(
        count=Count('rut_paciente')
    ).annotate(
        porcentaje=(Count('rut_paciente') * 100.0 / total_pacientes)
    )

    # Calcular edad promedio al momento de la muerte
    pacientes = Paciente.objects.all()
    edades = []
    for paciente in pacientes:
        if paciente.fecha_nacimiento and paciente.fecha_muerte:
            edad = paciente.fecha_muerte.year - paciente.fecha_nacimiento.year
            if (paciente.fecha_muerte.month, paciente.fecha_muerte.day) < (paciente.fecha_nacimiento.month, paciente.fecha_nacimiento.day):
                edad -= 1  # Ajustar si no ha llegado el cumpleaños
            edades.append(edad)

    # Calcular promedio
    edad_promedio = sum(edades) / len(edades) if edades else 0

    # Porcentajes por tramo de edad (ejemplo de tramos, ajustar según necesidad)
    tramos_edad = [
        (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 89)
    ]
    porcentajes_tramo_edad = []
    for tramo in tramos_edad:
        count = Paciente.objects.filter(
            fecha_nacimiento__gte=date.today().replace(year=date.today().year - tramo[1]),
            fecha_nacimiento__lt=date.today().replace(year=date.today().year - tramo[0])
        ).count()
        porcentaje = (count * 100.0 / total_pacientes) if total_pacientes > 0 else 0
        porcentajes_tramo_edad.append({'tramo': f"{tramo[0]}-{tramo[1]}", 'cantidad': count, 'porcentaje': porcentaje})

    context = {
        'total_pacientes': total_pacientes,
        'muertes_por_genero': muertes_por_genero,
        'muertes_por_hospital': muertes_por_hospital,
        'muertes_por_causa': muertes_por_causa,
        'edad_promedio': edad_promedio,
        'porcentajes_tramo_edad': porcentajes_tramo_edad,
    }

    return render(request, 'muertes_hospitalarias/analisis_estadistico.html', context)


def calcular_porcentaje_por_hospital(pacientes, total_pacientes):
    # Calcular porcentajes por hospital
    if total_pacientes == 0:
        return []

    return [
        {
            'hospital': hospital['hospital__nombre_hospital'],
            'cantidad': hospital['count'],
            'porcentaje': (hospital['count'] / total_pacientes) * 100
        }
        for hospital in pacientes.values('hospital__nombre_hospital').annotate(count=Count('hospital'))
    ]

def calcular_porcentaje_por_genero(pacientes, total_pacientes):
    # Calcular porcentajes por género
    if total_pacientes == 0:
        return []

    return [
        {
            'genero': genero['genero'],
            'cantidad': genero['count'],
            'porcentaje': (genero['count'] / total_pacientes) * 100
        }
        for genero in pacientes.values('genero').annotate(count=Count('genero'))
    ]

def calcular_porcentaje_por_tramo_edad(pacientes, total_pacientes):
    # Crear un diccionario para contar pacientes por tramo de edad
    tramos_edad = defaultdict(int)

    # Contar pacientes por tramo de edad
    for paciente in pacientes:
        edad = paciente.calcular_edad()
        if edad is not None:
            tramo = (edad // 10) * 10  # Obtener el tramo de 10 en 10
            tramos_edad[tramo] += 1

    # Calcular porcentajes
    if total_pacientes == 0:
        return []

    return [
        {
            'tramo': f'{tramo}-{tramo + 9}',
            'cantidad': cantidad,
            'porcentaje': (cantidad / total_pacientes) * 100
        }
        for tramo, cantidad in tramos_edad.items()
    ]
