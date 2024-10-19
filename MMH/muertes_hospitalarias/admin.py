from django.contrib import admin
from .models import Paciente, Medico, Hospital, CausaMuerte, InformeMuerteHospitalaria

admin.site.register(Paciente)
admin.site.register(Medico)
admin.site.register(Hospital)
admin.site.register(CausaMuerte)
admin.site.register(InformeMuerteHospitalaria)