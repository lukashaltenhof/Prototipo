from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Paciente, Medico, Hospital, Alerta, CausaMuerte
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .forms import PacienteForm
from django.contrib.auth.decorators import login_required

from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Count
from collections import defaultdict
from datetime import date
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import BuscarPacienteForm
from io import BytesIO
from django.utils import timezone

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
            elif user.groups.filter(name='gerente').exists():
                return redirect('alertas_gerente')  # Redirige a otra vista para analista
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

def render_to_pdf(template_src, context_dict={}):
    template = render_to_string(template_src, context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="analisis_estadistico.pdf"'
    pisa_status = pisa.CreatePDF(template, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF')
    return response

def pdf_view(request):
    # Obtiene la fecha y hora actual
    fecha_hora_actual = timezone.now()

    # Llama a la función que ya calcula los datos
    total_pacientes = Paciente.objects.count()

    muertes_por_genero = Paciente.objects.values('genero').annotate(
        count=Count('rut_paciente')
    ).annotate(
        porcentaje=(Count('rut_paciente') * 100.0 / total_pacientes)
    )

    muertes_por_hospital = Paciente.objects.values('hospital__nombre_hospital').annotate(
        count=Count('rut_paciente')
    ).annotate(
        porcentaje=(Count('rut_paciente') * 100.0 / total_pacientes)
    )

    muertes_por_causa = Paciente.objects.values('causa_muerte__nombre_causa').annotate(
        count=Count('rut_paciente')
    ).annotate(
        porcentaje=(Count('rut_paciente') * 100.0 / total_pacientes)
    )

    # Calcular porcentajes por tramo de edad
    porcentajes_tramo_edad = calcular_porcentaje_por_tramo_edad(Paciente.objects.all(), total_pacientes)

    # Preparar el contexto para la plantilla
    context = {
        'fecha_hora_actual': fecha_hora_actual,  # Añade la fecha y hora al contexto
        'muertes_por_genero': muertes_por_genero,
        'muertes_por_hospital': muertes_por_hospital,
        'muertes_por_causa': muertes_por_causa,
        'porcentajes_tramo_edad': porcentajes_tramo_edad,
        'total_pacientes': total_pacientes,
    }
    
    return render_to_pdf('muertes_hospitalarias/analisis_estadistico.html', context)


def generar_alerta_anomalia(request):
    total_pacientes = Paciente.objects.count()
    umbral = 70  # Porcentaje límite

    causas_muerte = Paciente.objects.values('causa_muerte__nombre_causa').annotate(
        count=Count('rut_paciente')
    ).annotate(
        porcentaje=(Count('rut_paciente') * 100.0 / total_pacientes)
    ).filter(porcentaje__gt=umbral)

    if causas_muerte.exists():
        gerente = User.objects.get(username='gerente1')
        for causa in causas_muerte:
            alerta = Alerta(
                usuario=gerente,
                mensaje=f"Más del {umbral}% de pacientes tienen la causa de muerte: {causa['causa_muerte__nombre_causa']}.",
                leido=False
            )
            alerta.save()
            messages.warning(request, f"Se ha generado una alerta: {alerta.mensaje}")

    else:
        messages.info(request, "No se encontraron anomalías en las causas de muerte.")

    return redirect('analisis_estadistico')  # Redirige a la vista del análisis

def alertas_gerente_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    alertas = Alerta.objects.filter(usuario=request.user).order_by('-fecha')

    return render(request, 'muertes_hospitalarias/alertas_gerente.html', {
        'alertas': alertas,
    })


def buscar_paciente(request):
    informes = None  # Para almacenar los informes
    if request.method == "POST":
        form = BuscarPacienteForm(request.POST)
        if form.is_valid():
            buscar_por = form.cleaned_data['buscar_por']
            valor = form.cleaned_data['valor']  # Esto solo se usa para 'rut' o 'nombre'
            causa_muerte = form.cleaned_data['causa_muerte']
            hospital = form.cleaned_data['hospital']

            if buscar_por == 'rut':
                if valor:  # Asegurarse de que el valor no esté vacío
                    pacientes = Paciente.objects.filter(rut_paciente=valor)
                else:
                    pacientes = None
            elif buscar_por == 'nombre':
                if valor:  # Asegurarse de que el valor no esté vacío
                    pacientes = Paciente.objects.filter(nombre__icontains=valor)
                else:
                    pacientes = None
            elif buscar_por == 'causa_muerte':
                if causa_muerte:  # Usar el valor del dropdown (ID)
                    pacientes = Paciente.objects.filter(causa_muerte=causa_muerte)
                else:
                    pacientes = None
            elif buscar_por == 'hospital':
                if hospital:  # Usar el valor del dropdown (ID)
                    pacientes = Paciente.objects.filter(hospital=hospital)
                else:
                    pacientes = None
            else:
                pacientes = None

            if pacientes:
                # Crear informes para cada paciente encontrado
                informes = []
                for paciente in pacientes:
                    edad = paciente.calcular_edad()
                    informe = {
                        'nombre': paciente.nombre,
                        'rut': f"{paciente.rut_paciente}-{paciente.dv}",
                        'causa_muerte': paciente.causa_muerte.nombre_causa if paciente.causa_muerte else 'N/A',
                        'fecha_nacimiento': paciente.fecha_nacimiento,
                        'fecha_muerte': paciente.fecha_muerte,
                        'hora_muerte': paciente.hora_muerte,
                        'detalles_muerte': paciente.detalles_muerte,
                        'genero': paciente.genero,
                        'hospital': paciente.hospital.nombre_hospital,
                        'medico': paciente.medico.nombre if paciente.medico else 'N/A',
                        'rut_medico': f"{paciente.medico.rut_medico}-{paciente.medico.dv}" if paciente.medico else 'N/A',
                        'edad': edad,
                    }
                    informes.append(informe)
    else:
        form = BuscarPacienteForm()

    return render(request, 'buscar_paciente.html', {'form': form, 'informes': informes})



def generar_pdf_informe(request):
    informe = []  # Lista para almacenar los pacientes filtrados

    if request.method == "POST":
        form = BuscarPacienteForm(request.POST)
        if form.is_valid():
            buscar_por = form.cleaned_data['buscar_por']
            valor = form.cleaned_data['valor']

            # Filtrar pacientes según el campo seleccionado
            if buscar_por == 'rut':
                pacientes = Paciente.objects.filter(rut_paciente=valor)
            elif buscar_por == 'nombre':
                pacientes = Paciente.objects.filter(nombre__icontains=valor)
            elif buscar_por == 'causa_muerte':
                pacientes = Paciente.objects.filter(causa_muerte__id=valor)
            elif buscar_por == 'hospital':
                pacientes = Paciente.objects.filter(hospital__id=valor)
            else:
                pacientes = Paciente.objects.all()
            
            # Preparar datos para el PDF
            informe = [{
                'nombre': paciente.nombre,
                'rut': f"{paciente.rut_paciente}-{paciente.dv}",
                'causa_muerte': paciente.causa_muerte.nombre_causa if paciente.causa_muerte else 'N/A',
                'fecha_nacimiento': paciente.fecha_nacimiento,
                'fecha_muerte': paciente.fecha_muerte,
                'hospital': paciente.hospital.nombre_hospital,
                'medico': paciente.medico.nombre if paciente.medico else 'N/A',
                'genero': paciente.genero,
                'edad': paciente.edad,
                'detalles_muerte': paciente.detalles_muerte
            } for paciente in pacientes]

    # Obtener la plantilla para el PDF
    template_path = 'plantilla_pdf.html'
    context = {
        'informe': informe,
        'current_date': timezone.now().strftime("%Y-%m-%d %H:%M:%S")  # Agregar la fecha de generación
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_pacientes.pdf"'

    # Crear el PDF
    template = get_template(template_path)
    html = template.render(context)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=result)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    response.write(result.getvalue())
    return response