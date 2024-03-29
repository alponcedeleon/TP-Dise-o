from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm , UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User,Group
from django.contrib import messages



from .forms import CustomUserCreationForm, SolicitudServicio, UserProfileForm, SolicitudComunidadForm
from .models import Perfil, Categoria, Comunidad, ComunidadPerfil, Servicio, LineaTransporte, Organizacion, Estacion, Sucursal, PrestacionServicioEstacion, PrestacionServicioSucursal, ServicioPerfilEstacion, ServicioPerfilSucursal, OrganismoExterno, Establecimiento
from .requests import obtener_localidades, obtener_provincias, obtener_ubicacion
from django.contrib.auth.decorators import login_required, user_passes_test
import logging
from django.db.models import Q
import csv
import io 
from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse
from django.http import JsonResponse

from .forms import CSVUploadForm
from bson.objectid import ObjectId

import pymongo
from django.conf import settings
from datetime import datetime

class CSVRow:
    def __init__(self, columna_1, columna_2):
        self.columna_1 = columna_1
        self.columna_2 = columna_2

my_client = pymongo.MongoClient(settings.DB_NAME)
# First define the database name
dbname = my_client['dds2023']
# Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection)
base_incidentes = dbname["incidente"]

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

########################################################################################################################################################

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
def listar_comunidades_perfil(request):
    group_names = requestGroups(request)
    perfil = Perfil.objects.get(user=request.user)
    comunidades_admin = ComunidadPerfil.objects.filter(perfil=perfil,esAdmin=True)
    comunidades_no_admin = ComunidadPerfil.objects.filter(perfil=perfil,esAdmin=False)
    
    incidentes = []
    # Recorrer las comunidades donde el usuario es administrador
    for comunidad in comunidades_admin:
        # Consultar la base de datos no SQL para contar los incidentes
        incidentes_count = base_incidentes.count_documents({"comunidad": comunidad.comunidad.nombre,"solucionado":False})
        # Almacenar la información en un diccionario
        resultado_comunidad = {
            'comunidad': comunidad.comunidad.nombre,
            'incidentes_count': incidentes_count
        }
        incidentes.append(resultado_comunidad)

    # Recorrer las comunidades donde el usuario no es administrador (si es necesario)
    for comunidad in comunidades_no_admin:
        # Consultar la base de datos no SQL para contar los incidentes
        incidentes_count = base_incidentes.count_documents({"comunidad": comunidad.comunidad.nombre,"solucionado":False})
        # Almacenar la información en un diccionario
        resultado_comunidad = {
            'comunidad': comunidad.comunidad.nombre,
            'incidentes_count': incidentes_count
        }
        incidentes.append(resultado_comunidad)
    
    context = {
        'request':request,
        'groups':group_names,
        'perfil': perfil,
        'comunidades_admin': comunidades_admin,
        'comunidades_no_admin': comunidades_no_admin,
        'incidentes':incidentes
    }

    return render(request, 'mis_comunidades.html', context)
########################################################################################################################################################

def listar_incidentes_comunidades(request, id_comunidad):
    
    group_names = requestGroups(request)
    perfil = Perfil.objects.get(user=request.user)
    comunidad = Comunidad.objects.get(id=id_comunidad)

    incidente_cursor = base_incidentes.find({"comunidad": comunidad.nombre,"solucionado":False})
    # Lista para almacenar los incidentes relevantes
    lista_incidentes = []

    # Iterar sobre los resultados del cursor y filtrar el campo _id
    for incidente in incidente_cursor:
        incidente['id'] = str(incidente['_id'])
        incidente2 = base_incidentes.find_one({'_id': ObjectId(incidente['_id'])})
        lista_incidentes.append(incidente)
    
    for incidente in lista_incidentes:
        logging.info(incidente)
    
    context = {
        'request':request,
        'groups':group_names,
        'perfil': perfil,
        'lista_incidentes':lista_incidentes,
        'id_comunidad':id_comunidad
    }

    return render(request, 'incidentes_comunidad.html', context)

def resolver_incidente(request, id_incidente, id_comunidad):
    incidente = base_incidentes.find_one({'_id': ObjectId(id_incidente)})
    if incidente:
        fecha_actual = datetime.now()
        fecha_cierre = fecha_actual.strftime("%d/%m/%Y %H:%M")
        
        # Crear un diccionario para las actualizaciones
        actualizaciones = {
            "solucionado": True,
            "fechaCierre": fecha_cierre
        }
        
        # Actualizar el documento en la base de datos
        base_incidentes.update_one({"_id": ObjectId(id_incidente)}, {"$set": actualizaciones})
        print("Incidente resuelto correctamente.")
    else:
        print("No se encontró ningún incidente con el ID proporcionado.")
      
    return redirect('listar_incidentes_comunidades', id_comunidad=id_comunidad)
########################################################################################################################################################
def crear_solicitud_comunidad(request):
    admin = User.objects.get(is_superuser=True)
    if request.method == 'POST':
        form = SolicitudComunidadForm(request.POST)
        if form.is_valid():
            solicitud_comunidad=form.save()
            nombre = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            motivo = form.cleaned_data['motivo']          
            objeto_id = solicitud_comunidad.id
                       
            send_mail(
                    'Solicitud de Creación de comunidad',
                    f'ID Solicitud: {objeto_id}\n\nNombre comunidad: {nombre}\n\nDescripcion: {descripcion}\n\nMotivo: {motivo}',
                    'alejo.poncedleon@gmail.com',  
                    [f'{admin.email}'],  # CAMBIAR CORREO ADMIN PARA TESTEAR
                    fail_silently=False,
                )
            

            # Redirigir a alguna página de éxito
            return redirect('index')
    else:
        form = SolicitudComunidadForm()
    return render(request, 'crear_comunidad.html', {'form': form})
########################################################################################################################################################

def administrar_comunidad(request, id_comunidad):
    admin = User.objects.get(is_superuser=True)
    perfil = Perfil.objects.get(user=request.user)
    if request.method == 'POST': 
        form = SolicitudServicio(request.POST)
        if form.is_valid():
            solicitud_servicio=form.save()
            nombre = form.cleaned_data['nombre']
            categoria = form.cleaned_data['categoria']
            categoria_alternativa = form.cleaned_data['categoria_alternativa']
            motivo = form.cleaned_data['motivo']  
            comunidad = form.cleaned_data['comunidad']      
            objeto_id = solicitud_servicio.id
                       
            if categoria_alternativa is None:
                categoria_alternativa= "Null"
            if motivo is None:
                motivo = "Null"
            
            send_mail(
                    'Solicitud de Creación de Servicio',
                    f'ID Solicitud: {objeto_id}\n\nComunidad: {comunidad}\n\nNombre usuario: {perfil.user.username}\n\nNombre Servicio: {nombre}\n\nCategoría: {categoria}\n\nCategoría alternativa: {categoria_alternativa}\n\nMotivo: {motivo}',
                    'alejo.poncedleon@gmail.com',  
                    [f'{admin.email}'],  # CAMBIAR CORREO ADMIN PARA TESTEAR
                    fail_silently=False,
                )


        else:
            print('error en formulario')
            print(form.errors)

    perfil = Perfil.objects.get(user=request.user)
    comunidad_perfiles = ComunidadPerfil.objects.filter(comunidad=id_comunidad).exclude(perfil=perfil)
    cantidad_miembros = comunidad_perfiles.count()
    group_names = requestGroups(request)
    comunidad = get_object_or_404(Comunidad, pk=id_comunidad)
    categorias = Categoria.objects.all()
    
    form = SolicitudServicio()
    context = { 'comunidad_perfiles': comunidad_perfiles, 
               'form': form, 
               'id_comunidad': id_comunidad,
               'comunidad':comunidad,
               'groups':group_names,
               'cantidad_miembros':cantidad_miembros,
               'categorias':categorias
               
               }
    

    return render(request, 'administrar_comunidad.html', context)
########################################################################################################################################################
def eliminar_miembro(request,perfil_id,comunidad_id):
    miembro = get_object_or_404(ComunidadPerfil,perfil_id=perfil_id,comunidad_id=comunidad_id)
    miembro.delete()    
    return redirect('administrar_comunidad',id_comunidad=comunidad_id)
########################################################################################################################################################
def designar_admin(request,perfil_id,comunidad_id):
    perfil = Perfil.objects.get(id=perfil_id)
    usuario= perfil.user
    grupo_usuario = usuario.groups.first()
    nuevo_grupo = Group.objects.get(name="ComunidadAdmin")
    miembro = get_object_or_404(ComunidadPerfil,perfil_id=perfil_id,comunidad_id=comunidad_id)
    miembro.esAdmin = True
    miembro.save()
    
    if grupo_usuario.name == 'Usuario':
        usuario.groups.set([nuevo_grupo])

    return redirect('administrar_comunidad',id_comunidad=comunidad_id)

########################################################################################################################################################    
def sacar_admin(request,perfil_id,comunidad_id):
    perfil = Perfil.objects.get(id=perfil_id)
    usuario= perfil.user
    nuevo_grupo = Group.objects.get(name="Usuario")
    miembro = get_object_or_404(ComunidadPerfil,perfil_id=perfil_id,comunidad_id=comunidad_id)
    miembro.esAdmin = False
    miembro.save()
    otras_comunidades =  ComunidadPerfil.objects.filter(perfil=perfil,esAdmin=True)
    if not otras_comunidades.exists():
        print('no es admin de otro grupo')
        usuario.groups.set([nuevo_grupo])
    
    return redirect('administrar_comunidad',id_comunidad=comunidad_id)

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

@login_required
def reportar_incidente(request, servicio_id, establecimiento_id, comunidades_nombres, tipo):
    
    # Crear el nuevo registro
    perfil = Perfil.objects.get(user=request.user)
    lista_comunidades = comunidades_nombres.split('-') 
    
    establecimiento = None
    nombre_establecimiento= None
    nuevo_registro = None
    if tipo == 'estacion':
        establecimiento = Estacion.objects.get(id=establecimiento_id)
        nombre_establecimiento = establecimiento.nombre

    else:
        establecimiento = Sucursal.objects.get(id=establecimiento_id)
        nombre_establecimiento = establecimiento.nombre
        
    servicio = Servicio.objects.get(id=servicio_id)
    fecha_actual = datetime.now()
    fecha_formateada = fecha_actual.strftime("%d/%m/%Y %H:%M")
    incidentes = [] 
    
    for comunidad in lista_comunidades:
        incidente = {
            "incidenteId": "0000001",
            "establecimiento": nombre_establecimiento,
            "servicio" : servicio.nombre,
            "comunidad" : comunidad,
            "departamento" : establecimiento.departamento,
            "provincia": establecimiento.provincia,
            "usuarioReportador" : perfil.id,
            "solucionado" : False,
            "fechaCreado" : fecha_formateada,
            "fechaCierre" : None
        }
        incidentes.append(incidente)
        
    base_incidentes.insert_many(incidentes)
     
    return redirect('establecimiento', id=establecimiento_id, tipo=tipo)

########################################################################################################################################################
@login_required
def salir_comunidad(request, comunidad_id, pag_redirect,tipo ):
    
    perfil = Perfil.objects.get(user=request.user)
    salida=None
    if tipo=='usuario':
        
        salida = get_object_or_404(ComunidadPerfil,comunidad_id=comunidad_id,perfil=perfil)  
        salida.delete()
        return redirect('listar_comunidades_perfil')

    else:
        comunidad_perfiles = ComunidadPerfil.objects.filter(comunidad=comunidad_id).exclude(perfil=perfil).filter(esAdmin=True)
        if comunidad_perfiles.exists():
            print('Hay otro admin')
            salida = get_object_or_404(ComunidadPerfil,comunidad_id=comunidad_id,perfil=perfil)  
            salida.delete()
        else:
            print('No hay otro admin')
            comunidad_perfiles = ComunidadPerfil.objects.filter(comunidad=comunidad_id).exclude(perfil=perfil).filter(esAdmin=False)
            primer_registro = comunidad_perfiles.first()
            primer_registro.esAdmin = True
            primer_registro.save()
            salida = get_object_or_404(ComunidadPerfil,comunidad_id=comunidad_id,perfil=perfil)  
            salida.delete()            


        return redirect('listar_comunidades_perfil') 

    

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
    entidad=None
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
    
    comunidades = ComunidadPerfil.objects.filter(perfil=perfil)
    for comunidad in comunidades:
        print(comunidad.comunidad.nombre)
    nombres_comunidades = [comunidad.comunidad.nombre for comunidad in comunidades]
    
    my_client = pymongo.MongoClient(settings.DB_NAME)

    # First define the database name
    dbname = my_client['dds2023']

    # Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection)
    base_incidentes = dbname["incidente"]
    
    incidentes = []

    for servicio in detalles_servicios:
        incidete = []
        incidente_cursor = base_incidentes.find({"establecimiento": establecimiento.nombre, "servicio": servicio["servicio"].nombre, "solucionado": False, "comunidad": {"$in": nombres_comunidades} })
        incidete.extend(list(incidente_cursor)) 
        if incidete:
            logging.info("este entra")
            incidentes.append(incidete[0]["servicio"])  # Convertir el cursor a una lista de documentos y extender la lista de incidentes

    for incidente in incidentes:
        logging.info(incidente)
        
    comunidades_nombres = '-'.join(comunidad.comunidad.nombre for comunidad in comunidades)


    context = {
        'establecimiento': establecimiento,
        'detalles_servicios': detalles_servicios,  
        'tipo':tipo,
        'groups':group_names,   
        'comunidades':comunidades,  
        'incidentes':incidentes,
        'comunidades_nombres':comunidades_nombres
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
        nuevo_email = request.POST.get('email')
        antiguo_email = perfil_usuario.email
        
        if form.is_valid():           
            
            if(nuevo_email != antiguo_email):
                print('envio de mail en progreso')
                                    
                send_mail(
                    '¡Actualizaste tu mail!',
                    f'Hola {perfil_usuario.nombre},\n\nTodas las actualizaciones de tus servicios publicos favoritos llegaran a este correo.\n\nAtentamente,\nEl equipo de nuestra aplicación',
                    'alejo.poncedleon@gmail.com',  # Tu dirección de correo electrónico
                    [nuevo_email],  # Lista de direcciones de correo electrónico de destino
                    fail_silently=False,
                )
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

    return render(request, 'perfil.html', context)

@login_required
def ranking_entidades_con_mayor_tiempo_promedio_de_tiempo_de_cierre_de_incidentes(request):
    from Aplicaciones.Monitoreo import cron
    from django.core.exceptions import ObjectDoesNotExist
    establecimientos = []
    try:
        orgExt = OrganismoExterno.objects.get(nombre=request.user)
    except ObjectDoesNotExist:
        orgExt = None

    if orgExt != None:
        for linea in orgExt.lineas.all():
            establecimientos.append(linea.estacion_origen.nombre)
            establecimientos.append(linea.estacion_destino.nombre)
            for estacion in linea.estaciones_intermedias.all():
                establecimientos.append(estacion.nombre)
    
        for organizacion in orgExt.organizaciones.all():
            establecimientos.append(organizacion.nombre)
    
    print(establecimientos)


    if request.method == 'POST':
        cron.entidades_con_mayor_tiempo_promedio_de_tiempo_de_cierre_de_incidentes()

    return renderizar_csv(request, establecimientos, 'entidades-con-mayor-tiempo-de-cierre-*.csv')

@login_required
def ranking_entidades_con_mayor_incidentes_reportados_en_la_semana(request):
    from Aplicaciones.Monitoreo import cron
    establecimientos = []
    orgExt = OrganismoExterno.objects.get(nombre=request.user)
    for linea in orgExt.lineas.all():
        establecimientos.append(linea.estacion_origen.nombre)
        establecimientos.append(linea.estacion_destino.nombre)
        for estacion in linea.estaciones_intermedias.all():
            establecimientos.append(estacion.nombre)
    
    for organizacion in orgExt.organizaciones.all():
        establecimientos.append(organizacion.nombre)
    
    print(establecimientos)

    if request.method == 'POST':
        cron.entidades_con_mayor_incidentes_reportados_en_la_semana()

    return renderizar_csv(request, establecimientos, 'entidades-con-mas-incidentes-*.csv')

def renderizar_csv(request, establecimientos, nombre_archivo):
    import glob
    import os

    # Buscamos el archivo mas reciente
    ruta = './rankings/'
    patron = nombre_archivo
    archivos_csv = glob.glob(os.path.join(ruta, patron))
    archivo_mas_reciente = max(archivos_csv, key=os.path.getmtime)
    filas = []

    # Abrir el archivo más reciente y leer línea por línea
    with open(archivo_mas_reciente, 'r') as archivo:
        for index, linea in enumerate(archivo):
            elementos = linea.strip().split(',')
            if index == 0 or elementos[0] in establecimientos:
                fila = CSVRow(elementos[0], elementos[1])
                filas.append(fila)
    
    nombre_columnas = filas.pop(0)

    context = {
        'request':request,
        'filas': filas,
        'nombre_columnas':  nombre_columnas
    }
    return render(request, 'visualizar_rankings.html', context)

########################################################################################################################################################

my_client = pymongo.MongoClient(settings.DB_NAME)

# First define the database name
dbname = my_client['dds2023']

# Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection)
base_incidentes = dbname["incidente"]

""" #let's create two documents
incidente = {
    "incidenteId": "0000001",
    "establecimiento": "Carrefour Flores",
    "servicio" : "Baño hombres A",
    "comunidad" : "Silla de rueda",
    "departamento" : "test1",
    "provincia": "test1",
    "usuarioReportador" : "2",
    "solucionado" : True,
    "fechaCreado" : datetime.strptime("07/01/2024 13:59", "%d/%m/%Y %H:%M"),
    "fechaCierre" : datetime.strptime("07/01/2024 14:59", "%d/%m/%Y %H:%M"),
}
incidente2 = {
    "incidenteId": "0000002",
    "establecimiento": "Carrefour Flores",
    "servicio" : "Baño hombres A",
    "comunidad" : "Silla de rueda",
    "departamento" : "test1",
    "provincia": "test1",
    "usuarioReportador" : "2",
    "solucionado" : True,
    "fechaCreado" : datetime.strptime("12/02/2024 13:59", "%d/%m/%Y %H:%M"),
    "fechaCierre" : datetime.strptime("12/02/2024 15:59", "%d/%m/%Y %H:%M"),
}
incidente3 = {
    "incidenteId": "0000003",
    "establecimiento": "San Pedrito",
    "servicio" : "Baño mujeres B",
    "comunidad" : "Silla de rueda",
    "departamento" : "test2",
    "provincia": "test2",
    "usuarioReportador" : "2",
    "solucionado" : True,
    "fechaCreado" : datetime.strptime("10/02/2024 13:59", "%d/%m/%Y %H:%M"),
    "fechaCierre" : datetime.strptime("11/02/2024 18:59", "%d/%m/%Y %H:%M"),
}
incidente4 = {
    "incidenteId": "0000004",
    "establecimiento": "San Pedrito",
    "servicio" : "Baño mujeres B",
    "comunidad" : "Silla de rueda",
    "departamento" : "test2",
    "provincia": "test2",
    "usuarioReportador" : "2",
    "solucionado" : True,
    "fechaCreado" : datetime.strptime("10/02/2024 14:59", "%d/%m/%Y %H:%M"),
    "fechaCierre" : datetime.strptime("11/02/2024 18:59", "%d/%m/%Y %H:%M"),
}
incidente5 = {
    "incidenteId": "0000005",
    "establecimiento": "San Pedrito",
    "servicio" : "Baño mujeres C",
    "comunidad" : "Silla de rueda",
    "departamento" : "test2",
    "provincia": "test2",
    "usuarioReportador" : "2",
    "solucionado" : True,
    "fechaCreado" : datetime.strptime("09/02/2024 13:59", "%d/%m/%Y %H:%M"),
    "fechaCierre" : datetime.strptime("10/02/2024 14:59", "%d/%m/%Y %H:%M"),
}
incidente6 = {
    "incidenteId": "0000006",
    "establecimiento": "San Pedrito",
    "servicio" : "Baño mujeres C",
    "comunidad" : "Silla de rueda",
    "departamento" : "test2",
    "provincia": "test2",
    "usuarioReportador" : "2",
    "solucionado" : True,
    "fechaCreado" : datetime.strptime("11/02/2024 13:59", "%d/%m/%Y %H:%M"),
    "fechaCierre" : datetime.strptime("12/02/2024 14:59", "%d/%m/%Y %H:%M"),
}
base_incidentes.insert_many([incidente,incidente2,incidente3,incidente4,incidente5,incidente6]) """

med_details = base_incidentes.find({})

for r in med_details:
    print(r["servicio"])

""" update_data = base_incidentes.update_one({'incidenteId':'0000001'}, {'$set':{'departamento':'test3'}}) """

