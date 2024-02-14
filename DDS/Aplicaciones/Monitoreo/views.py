from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm , UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm , UserProfileForm, FormularioComunidad
from .models import Perfil, Comunidad, ComunidadPerfil, Servicio, LineaTransporte, Organizacion, Estacion, Sucursal, PrestacionServicioEstacion, PrestacionServicioSucursal, ServicioPerfilEstacion, ServicioPerfilSucursal
from .requests import obtener_localidades, obtener_provincias
from django.contrib.auth.decorators import login_required, user_passes_test
import logging
from django.db.models import Q
from django.core.mail import send_mail
from django.http import HttpResponse


            

########################################################################################################################################################
def register(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            username = formulario.cleaned_data['username']
            user = authenticate(username=username, password=formulario.cleaned_data['password1'],)
            login(request,user)
            messages.success(request,"Te has registrado correctamente")
            return redirect(to='index')
            
        data["form"] = formulario

    return render(request, 'registration/register.html',data)



def requestGroups(request):
    user = request.user
    user_groups = user.groups.all()
    group_names = [group.name for group in user_groups]
    return group_names
########################################################################################################################################################
@login_required
def listar_comunidades(request):
    group_names = requestGroups(request)
    comunidades = Comunidad.objects.all()
    perfil = Perfil.objects.get(user=request.user)

    if request.method == 'POST':
        comunidad_id = request.POST.get('comunidad_id')
        comunidad = Comunidad.objects.get(id=comunidad_id)

        if 'unirse' in request.POST:
            if comunidad not in perfil.comunidades.all():
                perfil.comunidades.add(comunidad)
                perfil.save()
        elif 'salir' in request.POST:
            if comunidad in perfil.comunidades.all():
                perfil.comunidades.remove(comunidad)
                perfil.save()

    perfil_comunidades = perfil.comunidades.all()
    context = {
        'request':request,
        'groups':group_names,
        'comunidades': comunidades, 
        'perfil': perfil, 
        'perfil_comunidades': perfil_comunidades
    }

    return render(request, 'listar_comunidades.html', context)

def listar_comunidades_perfil(request):
    group_names = requestGroups(request)
    perfil = Perfil.objects.get(user=request.user)
    comunidades_admin = ComunidadPerfil.objects.filter(perfil=perfil,esAdmin=True)
    comunidades_no_admin = ComunidadPerfil.objects.filter(perfil=perfil,esAdmin=False)
    context = {
        'request':request,
        'groups':group_names,
        'perfil': perfil,
        'comunidades_admin': comunidades_admin,
        'comunidades_no_admin': comunidades_no_admin
    }

    return render(request, 'mis_comunidades.html', context)

def crear_comunidad(request):
    group_names = requestGroups(request)
    perfil = Perfil.objects.get(user=request.user)
    if request.method == 'POST':
        form = FormularioComunidad(request.POST)
        if form.is_valid():
            comunidad = Comunidad(
                nombre=form.cleaned_data['nombre'],
                descripcion=form.cleaned_data['descripcion']
            )
            comunidad.save()
            perfil.comunidades.add(comunidad)
            comunidad_perfil = ComunidadPerfil.objects.get(comunidad=comunidad, perfil=perfil)
            comunidad_perfil.esAdmin = True
            comunidad_perfil.save()
            perfil.save()

            return redirect('listar_comunidades')
    else:
        form = FormularioComunidad()
        perfil_comunidades = perfil.comunidades.all()
        context = {
            'request': request,
            'groups': group_names,
            'perfil': perfil,
            'form' :form
        }
    return render(request, 'crear_comunidad.html', context)


########################################################################################################################################################
@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='/admin/')
def home_view(request):
    
    queryset = request.GET.get("buscar")
    lineas = LineaTransporte.objects.all()[:6]
    organizaciones = Organizacion.objects.all()[:6]
    estaciones = Estacion.objects.all()[:6]
    sucursales = Sucursal.objects.all()[:6]
    if queryset:
        lineas = LineaTransporte.objects.filter(
            Q(nombre__icontains = queryset)| Q(provincia__icontains = queryset) | Q(tipo_transporte__icontains = queryset)
        ).distinct
        organizaciones = Organizacion.objects.filter(
             Q(nombre__icontains = queryset)| Q(provincia__icontains = queryset) | Q(tipo_organizacion__icontains = queryset)
        ).distinct
        estaciones = Estacion.objects.filter(
            Q(nombre__icontains = queryset) | Q(provincia__icontains = queryset) | Q(departamento__icontains = queryset) | Q(ubicacion_geografica__icontains = queryset)
        ).distinct
        sucursales = Sucursal.objects.filter(
            Q(nombre__icontains = queryset) | Q(provincia__icontains = queryset) | Q(departamento__icontains = queryset) | Q(ubicacion_geografica__icontains = queryset)
        ).distinct


    # Obtener grupos a los que pertenece el usuario

    group_names = requestGroups(request)
    
    # Obtener el perfil del usuario actual, si existe
    perfil_usuario = get_object_or_404(Perfil, user=request.user)

    # Contexto con los datos del perfil para pasar a la plantilla
    context = {
        'request':request,
        'groups':group_names,
        'perfil_usuario': perfil_usuario,
        'lineas':lineas,
        'organizaciones':organizaciones,
        'estaciones':estaciones,
        'sucursales':sucursales

    }
    logging.info(request.path)
    logging.info(context) 
    return render(request, 'index.html', context)
########################################################################################################################################################
@login_required
def entidad(request,id,tipo):
    lineas = None
    estaciones_intermedias = None
    estacion_origen = None
    estacion_destino = None
    organizaciones = None
    sucursales = None
    if tipo =='lineatransporte':
        lineas = get_object_or_404(LineaTransporte, id=id)
        datos_tabla_intermedia = LineaTransporte.estaciones_intermedias.through.objects.filter(lineatransporte_id=id)
        ids_estaciones_intermedias = [datos.estacion_id for datos in datos_tabla_intermedia]
        estaciones_intermedias = Estacion.objects.filter(id__in=ids_estaciones_intermedias)
        estacion_origen = Estacion.objects.get(id = lineas.estacion_origen_id)
        estacion_destino = Estacion.objects.get(id = lineas.estacion_destino_id)
    else:
        organizaciones =  get_object_or_404(Organizacion, id=id)  
        sucursales = Sucursal.objects.filter(organizacion_id=id)
    context = {
        'tipo':tipo,
        'organizaciones':organizaciones,
        'sucursales':sucursales,
        'estaciones_intermedias' : estaciones_intermedias,
        'lineas': lineas,
        'estacion_origen':estacion_origen,
        'estacion_destino':estacion_destino


    }
    return render(request, 'entidad.html',context)
########################################################################################################################################################
@login_required
def servicio_perfil_estacion(request, servicio_id, establecimiento_id,tipo):
    # Crear el nuevo registro
    perfil = Perfil.objects.get(user=request.user)
    nuevo_registro = None
    if tipo == 'estacion':
        servicio = PrestacionServicioEstacion.objects.get(servicio_id=servicio_id,estacion_id=establecimiento_id)
        nuevo_registro = ServicioPerfilEstacion(servicio=servicio, perfil=perfil)
    else:
        servicio = PrestacionServicioSucursal.objects.get(servicio_id=servicio_id,sucursal_id=establecimiento_id)
        nuevo_registro = ServicioPerfilSucursal(servicio=servicio, perfil=perfil)
        
    
    nuevo_registro.save()
     
    return redirect('establecimiento', id=establecimiento_id, tipo=tipo)
########################################################################################################################################################
@login_required
def eliminar_servicio_perfil_estacion(request, servicio_id, establecimiento_id,tipo):
    perfil = Perfil.objects.get(user=request.user)
    if tipo == 'estacion':
        servicio = PrestacionServicioEstacion.objects.get(servicio_id=servicio_id,estacion_id=establecimiento_id)
        servicio_perfil_estacion = get_object_or_404(ServicioPerfilEstacion,servicio=servicio,perfil=perfil)
        servicio_perfil_estacion.delete()
    else:
        servicio = PrestacionServicioSucursal.objects.get(servicio_id=servicio_id,sucursal_id=establecimiento_id)
        servicio_perfil_sucursal = get_object_or_404(ServicioPerfilSucursal,servicio=servicio,perfil=perfil)
        servicio_perfil_sucursal.delete()    
        
    return redirect('establecimiento', id=establecimiento_id, tipo=tipo)
########################################################################################################################################################


@login_required
def establecimiento(request,id,tipo):
    perfil = Perfil.objects.get(user=request.user)
    establecimiento=None
    detalles_servicios = []
    if tipo == 'estacion':
        establecimiento = get_object_or_404(Estacion,id=id)
        prestaciones_servicio = PrestacionServicioEstacion.objects.filter(estacion=establecimiento)
        for prestacion in prestaciones_servicio:
            servicio = prestacion.servicio
            actividad = 'Activo' if prestacion.actividad else 'Inactivo'
            suscrito = ServicioPerfilEstacion.objects.filter(servicio=prestacion, perfil=perfil).exists()
            detalles_servicios.append({'servicio': servicio, 'actividad': actividad, 'suscrito': suscrito})
    else:
        establecimiento = get_object_or_404(Sucursal,id=id)
        prestaciones_servicio = PrestacionServicioSucursal.objects.filter(sucursal=establecimiento)
        for prestacion in prestaciones_servicio:
            servicio = prestacion.servicio
            actividad = 'Activo' if prestacion.actividad else 'Inactivo'
            suscrito = ServicioPerfilSucursal.objects.filter(servicio=prestacion, perfil=perfil).exists()
            detalles_servicios.append({'servicio': servicio, 'actividad': actividad, 'suscrito': suscrito})

    context = {
        'establecimiento': establecimiento,
        'detalles_servicios': detalles_servicios,  
        'tipo':tipo      
    }
    
    return render(request, 'establecimiento.html', context)


########################################################################################################################################################
@login_required
def perfil_usuario(request):
    # Obtener grupos a los que pertenece el usuario
    group_names = requestGroups(request)
    
    # Obtener el perfil del usuario actual, si existe
    perfil_usuario = get_object_or_404(Perfil, user=request.user)
    provincias = obtener_provincias()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=perfil_usuario)
        if form.is_valid():
            form.save()
            if(perfil_usuario.email != 'email@monitoreo.com'):
                print('envio de mail en progreso')
                send_mail(
                    '¡Actualizaste tu mail!',
                    f'Hola {perfil_usuario.nombre},\n\nTodas las actualizaciones de tus servicios publicos favoritos llegaran a este correo.\n\nAtentamente,\nEl equipo de nuestra aplicación',
                    'alejo.poncedleon@gmail.com',  # Tu dirección de correo electrónico
                    [f'{perfil_usuario.email}'],  # Lista de direcciones de correo electrónico de destino
                    fail_silently=False,
                )
            # Redirigir a la página del perfil o a donde sea necesario después de guardar los cambios
            return redirect('index')  # Cambia 'perfil' por el nombre de la URL de tu vista de perfil
    else:
        form = UserProfileForm(instance=perfil_usuario)

    # Contexto con los datos del perfil para pasar a la plantilla
    context = {
        'request':request,
        'perfil_usuario': perfil_usuario,
        'form': form,
        'provincias': provincias,
        'groups':group_names
    }
    logging.info(request.path)

    return render(request, 'perfil.html', context)
########################################################################################################################################################
import pymongo
from django.conf import settings
my_client = pymongo.MongoClient(settings.DB_NAME)

# First define the database name
dbname = my_client['dds2023']

# Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection)
collection_name = dbname["incidente"]

#let's create two documents
incidente = {
    "incidenteId": "0000001",
    "servicio" : "Baño hombres",
    "comunidad" : "Silla de rueda",
    "departamento" : "test1",
    "provincia": "test1",
    "usuarioReportador" : "2",
    "solucionado" : "False",
    "fechaCreado" : "07/01/2024 13:59",
    "fechaCierre" : "",
}
incidente2 = {
    "incidenteId": "0000002",
    "servicio" : "Baño mujeres",
    "comunidad" : "Silla de rueda",
    "departamento" : "test2",
    "provincia": "test2",
    "usuarioReportador" : "2",
    "solucionado" : "False",
    "fechaCreado" : "07/01/2024 13:59",
    "fechaCierre" : "",
}

collection_name.insert_many([incidente,incidente2])

med_details = collection_name.find({})

for r in med_details:
    print(r["departamento"])

update_data = collection_name.update_one({'incidenteId':'0000001'}, {'$set':{'departamento':'test3'}})

