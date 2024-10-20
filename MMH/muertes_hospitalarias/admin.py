from django.contrib import admin
from .models import Region, Ciudad, Comuna, Hospital, Medico, CausaMuerte, Paciente, InformeMuerteHospitalaria, PerfilUsuario

admin.site.register(Region)
admin.site.register(Ciudad)
admin.site.register(Comuna)
admin.site.register(Hospital)
admin.site.register(Medico)
admin.site.register(CausaMuerte)
admin.site.register(Paciente)
admin.site.register(InformeMuerteHospitalaria)
admin.site.register(PerfilUsuario)