from django.contrib import admin
from .models import Estacion, LineaTransporte, Servicio, Categoria, Comunidad, Perfil, ComunidadPerfil, Sucursal, Organizacion, Establecimiento, OrganismoExterno, PrestacionServicioEstacion,PrestacionServicioSucursal,ServicioPerfilEstacion,ServicioPerfilSucursal, SolicitudComunidad
from django import forms
import requests 
##################################################################################
class CustomChoiceField(forms.ChoiceField):
    def validate(self, value):
        # Override the validation to skip choices validation
        pass
    
##################################################################################
class EstablecimientoAdminForm(forms.ModelForm):
    class Meta:
        model = Estacion  # O puedes usar Sucursal si lo prefieres
        fields = '__all__'

    provincia = forms.ChoiceField(choices=[], required=False)
    departamento = CustomChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Llena las opciones del campo 'provincia' con los resultados de la API
        provincias = self.get_provincia_choices()
        self.fields['provincia'].choices = provincias
        

    def get_provincia_choices(self):
        api_url = 'https://apis.datos.gob.ar/georef/api/provincias'
        response = requests.get(api_url)

        if response.status_code == 200:
            provincias = response.json().get("provincias", [])
            return [(provincia["nombre"], provincia["nombre"]) for provincia in provincias]
        else:
            return []
        
    
    
    class Media:
        js = ('https://code.jquery.com/jquery-3.6.4.min.js','admin/js/establecimiento_admin.js',)
##################################################################################
class EstacionAdmin(admin.ModelAdmin):
    form = EstablecimientoAdminForm
    list_display = ('nombre', 'provincia', 'ubicacion_geografica')
##################################################################################
class SucursalAdmin(admin.ModelAdmin):
    form = EstablecimientoAdminForm
    list_display = ('nombre', 'provincia', 'ubicacion_geografica')

def aprobar_solicitud(modeladmin,request,queryset):
    for solicitud in queryset:
        # Crear un nuevo objeto Comunidad basado en la solicitud
        comunidad = Comunidad.objects.create(nombre=solicitud.nombre, descripcion=solicitud.descripcion)
        # Guardar el nuevo objeto Comunidad
        comunidad.save()
        # Eliminar la solicitud actual
        solicitud.delete()

class SolicitudComunidadAdmin(admin.ModelAdmin):
    actions = [aprobar_solicitud]

admin.site.register(SolicitudComunidad,SolicitudComunidadAdmin)
admin.site.register(Estacion, EstacionAdmin)
admin.site.register(Sucursal, SucursalAdmin)
admin.site.register(LineaTransporte)
admin.site.register(Organizacion)
admin.site.register(Servicio)
admin.site.register(PrestacionServicioEstacion)
admin.site.register(PrestacionServicioSucursal)
admin.site.register(ServicioPerfilSucursal)
admin.site.register(ServicioPerfilEstacion)
admin.site.register(Perfil)
admin.site.register(Categoria)
admin.site.register(ComunidadPerfil)
admin.site.register(Comunidad)
admin.site.register(OrganismoExterno)


