from django.urls import path
from .views import PacienteListView, PacienteCreateView, PacienteUpdateView, PacienteDeleteView, login_view, PacienteDetailView, logout_view, analisis_estadistico, pdf_view, buscar_paciente, generar_pdf_informe
from django.contrib.auth.views import LogoutView
from . import views

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
    path('alertas-gerente/', views.alertas_gerente_view, name='alertas_gerente'),
     path('buscar/', buscar_paciente, name='buscar_paciente'),
    path('muertes-hospitalarias/pdf/', views.generar_pdf_informe, name='generar_pdf_informe'),
    
]
