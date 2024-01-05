from django.contrib import admin
from .models import Estacion, LineaTransporte, Servicio, PrestacionServicio, Categoria, Comunidad, Perfil, ComunidadPerfil
# Register your models here.

admin.site.register(Estacion)
admin.site.register(LineaTransporte)
admin.site.register(Servicio)
admin.site.register(PrestacionServicio)
admin.site.register(Categoria)
admin.site.register(Comunidad)
admin.site.register(Perfil)
admin.site.register(ComunidadPerfil)

