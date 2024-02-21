from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Estacion,SolicitudServicio, LineaTransporte, Servicio, Categoria, Comunidad, Perfil, ComunidadPerfil, Sucursal, Organizacion, Establecimiento, OrganismoExterno, PrestacionServicioEstacion,PrestacionServicioSucursal,ServicioPerfilEstacion,ServicioPerfilSucursal, SolicitudComunidad
from django import forms
import requests 
from django.core.mail import send_mail
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
        
        comunidad = Comunidad.objects.create(nombre=solicitud.nombre, descripcion=solicitud.descripcion)
        comunidad_perfil = ComunidadPerfil.objects.create(comunidad=comunidad, perfil=solicitud.perfil, esAdmin=True, observador=False)
        usuario = solicitud.perfil.user
        usuario_mail=solicitud.perfil
        nuevo_grupo = Group.objects.get(name='ComunidadAdmin')  
        usuario.groups.set([nuevo_grupo])       
        send_mail(
                    'Solicitud de Comunidad Aprobada',
                    f'Hola {usuario_mail.nombre},\n\nTe informamos que tu solicitud para la creacion de la comunidad "{solicitud.nombre}" ha sido aprobada. Ahora al entrar al sistema obtienes acceso al panel de administración de tu comunidad ¡Felicitaciones!\n\nAtentamente,\nEl equipo de nuestra aplicación',
                   'alejo.poncedleon@gmail.com',  
                    [f'{usuario_mail.email}'],  
                   fail_silently=False,
                )
        solicitud.delete()

def rechazar_solicitud(modeladmin,request,queryset):
    for solicitud in queryset:
                
        usuario = solicitud.perfil        
        send_mail(
                    'Solicitud de Comunidad Rechazada',
                    f'Hola {usuario.nombre},\n\nTe informamos que tu solicitud para la creacion de la comunidad "{solicitud.nombre}" ha sido rechazada.\n\nAtentamente,\nEl equipo de nuestra aplicación',
                   'alejo.poncedleon@gmail.com',  
                    [f'{usuario.email}'],  
                   fail_silently=False,
                )        
        solicitud.delete()

def aprobar_solicitud_Servicio(modeladmin,request,queryset):
    for solicitud in queryset:
        
        usuario = solicitud.perfil       
        send_mail(
                    'Solicitud de Servicio Aprobada',
                    f'Hola {usuario.nombre},\n\nTe informamos que tu solicitud para la creacion del servicio "{solicitud.nombre}" ha sido aprobada ¡Felicitaciones!\n\nAtentamente,\nEl equipo de nuestra aplicación',
                   'alejo.poncedleon@gmail.com',  
                    [f'{usuario.email}'],  
                   fail_silently=False,
                )
        #solicitud.delete()

def rechazar_solicitud_Servicio(modeladmin,request,queryset):
    for solicitud in queryset:
                
        usuario = solicitud.perfil        
        send_mail(
                    'Solicitud de Servicio Rechazada',
                    f'Hola {usuario.nombre},\n\nTe informamos que tu solicitud para la creacion del servicio "{solicitud.nombre}" ha sido rechazada.\n\nAtentamente,\nEl equipo de nuestra aplicación',
                   'alejo.poncedleon@gmail.com',  
                    [f'{usuario.email}'],  
                   fail_silently=False,
                )        
        solicitud.delete()

class SolicitudComunidadAdmin(admin.ModelAdmin):
    actions = [aprobar_solicitud,rechazar_solicitud]

class SolicitudServicioAdmin(admin.ModelAdmin):
    actions = [aprobar_solicitud_Servicio,rechazar_solicitud_Servicio]



admin.site.register(SolicitudComunidad,SolicitudComunidadAdmin)
admin.site.register(Estacion, EstacionAdmin)
admin.site.register(Sucursal, SucursalAdmin)
admin.site.register(SolicitudServicio, SolicitudServicioAdmin)
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


