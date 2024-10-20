from django.urls import path
from .views import PacienteListView, PacienteCreateView, PacienteUpdateView, PacienteDeleteView, login_view, PacienteDetailView, logout_view, analisis_estadistico, pdf_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('pacientes/', PacienteListView.as_view(), name='paciente-list'),
    path('pacientes/nuevo/', PacienteCreateView.as_view(), name='paciente-create'),
    path('pacientes/editar/<int:pk>/', PacienteUpdateView.as_view(), name='paciente-edit'),
    path('pacientes/eliminar/<int:pk>/', PacienteDeleteView.as_view(), name='paciente-delete'),
    path('login/', login_view, name='login'),
    
    path('logout/', logout_view, name='logout'),
    path('paciente/<int:pk>/', PacienteDetailView.as_view(), name='paciente-detail'),
    path('analisis/', analisis_estadistico, name='analisis'),
    path('analisis/pdf/', pdf_view, name='pdf_view'),  # URL para generar el PDF
    
]
