from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm , UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm , UserProfileForm
from .models import Perfil, Comunidad, Servicio, LineaTransporte, Organizacion, Estacion, Sucursal
from .requests import obtener_localidades, obtener_provincias
from django.contrib.auth.decorators import login_required, user_passes_test
import logging
from django.db.models import Q



# Create your views here.
def register(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username=formulario.cleaned_data['username'], password=formulario.cleaned_data['password1'],)
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

@login_required
def listar_servicios(request):
    group_names = requestGroups(request)
    servicios = Servicio.objects.all()
    lineas = LineaTransporte.objects.all()
    perfil = Perfil.objects.get(user=request.user)

    if request.method == 'POST':
        servicio_id = request.POST.get('servicio_id')
        servicio = Servicio.objects.get(id=servicio_id)

        if 'agregar' in request.POST:
            if servicio not in perfil.servicios.all():
                perfil.servicios.add(servicio)
                perfil.save()
        elif 'quitar' in request.POST:
            if servicio in perfil.servicios.all():
                perfil.servicios.remove(servicio)
                perfil.save()
        elif 'agregar' in request.POST:
            if servicio not in perfil.servicios.all():
                perfil.servicios.add(servicio)
                perfil.save()
        elif 'quitar' in request.POST:
            if servicio in perfil.servicios.all():
                perfil.servicios.remove(servicio)
                perfil.save()

    perfil_servicios = perfil.servicios.all()
    context = {
        'request':request,
        'groups':group_names,
        'servicios': servicios, 
        'perfil': perfil, 
        'perfil_servicios': perfil_servicios , 
        'lineas':lineas
    }

    return render(request, 'listar_servicios.html', context)

@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='/admin/')
def home_view(request):
    print(request.GET)
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

@login_required
def establecimientos(request,id,tipo):
    print(id)
    print(tipo)
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
    return render(request, 'establecimientos.html',context)


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

