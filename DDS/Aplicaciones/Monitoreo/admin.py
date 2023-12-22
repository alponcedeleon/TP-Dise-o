from django.contrib import admin
from .models import Estacion, LineaTransporte, Servicio, PrestacionServicio, Categoria, Comunidad, Perfil
# Register your models here.

admin.site.register(Estacion)
admin.site.register(LineaTransporte)
admin.site.register(Servicio)
admin.site.register(PrestacionServicio)
admin.site.register(Categoria)
admin.site.register(Comunidad)
admin.site.register(Perfil)

