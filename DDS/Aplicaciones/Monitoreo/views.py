from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm , UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm , UserProfileForm
from .models import Perfil, Comunidad, Servicio, LineaTransporte, Organizacion, Estacion, Sucursal, PrestacionServicioEstacion, PrestacionServicioSucursal, ServicioPerfilEstacion, ServicioPerfilSucursal
from .requests import obtener_localidades, obtener_provincias, obtener_ubicacion
from django.contrib.auth.decorators import login_required, user_passes_test
import logging
from django.db.models import Q
import csv
import io 
from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse

from .forms import CSVUploadForm

@login_required
def get_location(request):
    return render(request, 'location.html')

def process_location(request):
    if request.method == 'GET':
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        perfil = Perfil.objects.get(user=request.user)
        perfil.ultima_latitud=latitude
        perfil.ultima_longitud=longitude
        perfil.save()
        # Do whatever logic you need with the latitude and longitude here
        # For example, you could save it to the user's profile or session
        # After processing, redirect the user to the homepage or any other page
        return redirect('/')  # Assuming 'home' is the name of your homepage URL pattern
    else:
        return redirect('/')  # Redirect to the homepage if the request method is not GET



def cargar_datos_desde_csv(request):
    establecimientos_nuevos = None  # Inicializa las variables fuera del bloque condicional
    servicios_nuevos = None
    if request.method == 'POST':
        logging.info(request.FILES)
        if 'establecimientos-archivo_csv' in request.FILES:
            formEstablecimientos = CSVUploadForm(request.POST, request.FILES, prefix='establecimientos')
            if formEstablecimientos.is_valid():
                archivo_csv = request.FILES['establecimientos-archivo_csv']
                # Procesar el archivo CSV de estaciones y guardar los datos en la base de datos
                establecimientos_nuevos = procesar_csv_establecimiento(archivo_csv)
                logging.info(establecimientos_nuevos)
                # Resto del código para renderizar la página con los resultados
        if 'servicios-archivo_csv' in request.FILES:
            logging.info("asdasd")
            formServicios = CSVUploadForm(request.POST, request.FILES, prefix='servicios')
            if formServicios.is_valid():
                archivo_csv = request.FILES['servicios-archivo_csv']
                # Procesar el archivo CSV de servicios y guardar los datos en la base de datos
                servicios_nuevos = procesar_csv_servicios(archivo_csv)
                logging.info("asdasd")
                # Resto del código para renderizar la página con los resultados
        group_names = requestGroups(request)
        context = {
            'request':request,
            'groups':group_names,
            'perfil_usuario': perfil_usuario,
            'establecimientos_nuevos': establecimientos_nuevos,
            'servicios_nuevos': servicios_nuevos,
        }
        return render(request, 'carga_exitosa.html',context)
    else:
        formEstablecimientos = CSVUploadForm(prefix='establecimientos')
        formServicios = CSVUploadForm(prefix='servicios')
        
    group_names = requestGroups(request)
    
    context = {
        'request':request,
        'groups':group_names,
        'perfil_usuario': perfil_usuario,
        'formEstablecimientos': formEstablecimientos,
        'formServicios': formServicios,
    }
    return render(request, 'cargar_datos.html', context)

def procesar_csv_establecimiento(archivo_csv):
    # Aquí colocarías el código para procesar el archivo CSV y guardar los datos en la base de datos
    # Podrías utilizar la función cargar_datos_desde_csv que definiste previamente
    decoded_file = archivo_csv.read().decode('utf-8')  # Lee el contenido del archivo y lo decodifica
    io_string = io.StringIO(decoded_file)  # Crea un objeto StringIO a partir del contenido decodificado
    
    # Luego puedes leer el archivo CSV utilizando el objeto StringIO
    lector_csv = csv.DictReader(io_string)
    nuevos = []
    for fila in lector_csv:
        tipo = fila.pop('tipo')
        latitud = fila.pop('latitud')
        longitud = fila.pop('longitud')
        ubicacion = obtener_ubicacion(latitud,longitud)
        fila['provincia'] = ubicacion['provincia']['nombre']
        fila['departamento'] = ubicacion['departamento']['nombre']
        fila['ubicacion_geografica'] = fila['provincia'] + fila['departamento']
        if tipo == 'Estacion':
            organizacion = fila.pop('organizacion')
            existe = Estacion.objects.filter(**fila).exists()
            if not existe:
                nuevos.append(fila)
                # Crea una instancia de Estacion y guarda los datos en la base de datos
                estacion = Estacion.objects.create(
                nombre=fila['nombre'],
                provincia=fila['provincia'],
                departamento=fila['departamento'],
                foto=fila['foto'],
                ubicacion_geografica=fila['ubicacion_geografica']
                )
                
        elif tipo == 'Sucursal':
            organizacion = Organizacion.objects.get(nombre=fila['organizacion'])
            organizacion_nombre = fila.pop('organizacion')
            existe = Sucursal.objects.filter(**fila).exists()
            if not existe:
                nuevos.append(fila)
                # Crea una instancia de Sucursal y guarda los datos en la base de datos
                sucursal = Sucursal.objects.create(
                nombre=fila['nombre'],
                provincia=fila['provincia'],
                departamento=fila['departamento'],
                foto=fila['foto'],
                ubicacion_geografica=fila['ubicacion_geografica'],
                organizacion=organizacion
            )
    return nuevos

def procesar_csv_servicios(archivo_csv):

    # Aquí colocarías el código para procesar el archivo CSV y guardar los datos en la base de datos
    # Podrías utilizar la función cargar_datos_desde_csv que definiste previamente
    decoded_file = archivo_csv.read().decode('utf-8')  # Lee el contenido del archivo y lo decodifica
    io_string = io.StringIO(decoded_file)  # Crea un objeto StringIO a partir del contenido decodificado
    
    # Luego puedes leer el archivo CSV utilizando el objeto StringIO
    lector_csv = csv.DictReader(io_string)
    nuevos = []
    for fila in lector_csv:
        tipo = fila.pop('tipo')
        if tipo == 'Estacion':
            establecimiento=fila['establecimiento']
            nombre_servicio=fila['servicio']
            prestacion_valor =fila['prestacion']
            estacion = Estacion.objects.get(nombre=establecimiento)
            servicio=Servicio.objects.get(nombre=nombre_servicio)
            if prestacion_valor.lower() == 'si':
                prestacion = True
            else : 
                prestacion = False
            
            existe = PrestacionServicioEstacion.objects.filter(estacion=estacion, servicio=servicio).exists()
            if not existe:
                # Crea una instancia de PrestacionServicioEstacion y guarda los datos en la base de datos
                prestacionServicioEstacion = PrestacionServicioEstacion.objects.create(
                estacion=estacion,
                servicio=servicio,
                actividad=prestacion,
                )
                nuevos.append(fila)
                logging.info(nuevos)
            else:
                sinModificar = PrestacionServicioEstacion.objects.filter(estacion=estacion, servicio=servicio, actividad=prestacion).exists()
                if not sinModificar:
                    prestacionServicioEstacion = PrestacionServicioEstacion.objects.get(estacion=estacion, servicio=servicio)
                    prestacionServicioEstacion.actividad = prestacion
                    prestacionServicioEstacion.save()
                    nuevos.append(fila)
                    logging.info(nuevos)
        elif tipo == 'Sucursal':
            establecimiento=fila['establecimiento']
            nombre_servicio=fila['servicio']
            prestacion_valor =fila['prestacion']
            sucursal = Sucursal.objects.get(nombre=establecimiento)
            servicio=Servicio.objects.get(nombre=nombre_servicio)
            if prestacion_valor.lower() == 'si':
                prestacion = True
            else : 
                prestacion = False
            
            existe = PrestacionServicioSucursal.objects.filter(sucursal=sucursal, servicio=servicio).exists()
            if not existe:
                # Crea una instancia de PrestacionServicioEstacion y guarda los datos en la base de datos
                prestacionServicioSucursal = PrestacionServicioSucursal.objects.create(
                sucursal=sucursal,
                servicio=servicio,
                actividad=prestacion,
                )
                nuevos.append(fila)
                logging.info(nuevos)
            else:
                sinModificar = PrestacionServicioSucursal.objects.filter(sucursal=sucursal, servicio=servicio, actividad=prestacion).exists()
                if not sinModificar:
                    prestacionServicioSucursal = PrestacionServicioSucursal.objects.get(sucursal=sucursal, servicio=servicio)
                    prestacionServicioSucursal.actividad = prestacion
                    prestacionServicioSucursal.save()
                    nuevos.append(fila)
                    logging.info(nuevos)
    
    return nuevos

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
        'sucursales':sucursales,
    }
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
        
    # Obtener grupos a los que pertenece el usuario

    group_names = requestGroups(request)
    context = {
        'tipo':tipo,
        'organizaciones':organizaciones,
        'sucursales':sucursales,
        'estaciones_intermedias' : estaciones_intermedias,
        'lineas': lineas,
        'estacion_origen':estacion_origen,
        'estacion_destino':estacion_destino,
        'groups':group_names,


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
    # Obtener grupos a los que pertenece el usuario
    group_names = requestGroups(request)
    context = {
        'establecimiento': establecimiento,
        'detalles_servicios': detalles_servicios,  
        'tipo':tipo,
        'groups':group_names,      
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

