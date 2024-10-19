from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Paciente
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.models import Group


# Listar los pacientes
class PacienteListView(ListView):
    model = Paciente
    template_name = 'muertes_hospitalarias/paciente_list.html'

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
    template_name = 'muertes_hospitalarias/paciente_form.html'
    fields = '__all__'
    success_url = reverse_lazy('paciente-list')

# Editar un paciente
class PacienteUpdateView(UpdateView):
    model = Paciente
    template_name = 'muertes_hospitalarias/paciente_form.html'
    fields = '__all__'
    success_url = reverse_lazy('paciente-list')

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
                return redirect('otra-vista')  # Redirige a otra vista para analista
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