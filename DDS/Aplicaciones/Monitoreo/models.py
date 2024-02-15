from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
import requests
from django import forms
from django.forms import Media
from django.contrib import admin
import json


# Create your models here.
#############################################################################################
class Establecimiento(models.Model):
    nombre = models.CharField(max_length=30)
    provincia = models.CharField(max_length=50, null=True)
    departamento = models.CharField(max_length=50, null=True)
    foto = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    class Meta:
        abstract = True
#############################################################################################           
class Estacion(Establecimiento):
    """ solo queda ubicacion geografica para rellenar """
    ubicacion_geografica = models.CharField(max_length=30)
    
    def __str__(self):
        return self.nombre
    


#############################################################################################
class Entidad(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.CharField(max_length=20, null=True)
    foto = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    class Meta:
        abstract = True

#############################################################################################      
class LineaTransporte(Entidad):
    TIPO_CHOICES = (
        ('Subterraneo', 'Subterráneo'),
        ('Ferrocarril', 'Ferrocarril'),
    )
    estacion_origen = models.ForeignKey(Estacion, related_name='estacion_origen', on_delete=models.CASCADE)
    estacion_destino = models.ForeignKey(Estacion, related_name='estacion_destino', on_delete=models.CASCADE)
    estaciones_intermedias = models.ManyToManyField(Estacion, related_name='estaciones_intermedias')
    tipo_transporte = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre
#############################################################################################   
class LineaPerfil(models.Model):
    linea = models.ForeignKey(LineaTransporte, on_delete=models.CASCADE)
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE)
    def __str__(self):
        return 'Usuario '+ self.perfil.user.username + ' esta interesado en ' + self.linea.nombre 

#############################################################################################   
class Organizacion(Entidad):
    TIPO_CHOICES = (
        ('Supermercado', 'Supermercado'),
        ('Centro Comunal', 'Centro Comunal'),
        ('Banco', 'Banco'),
    )
    tipo_organizacion = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre
 #############################################################################################      
class Sucursal(Establecimiento):
    ubicacion_geografica = models.CharField(max_length=30)
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, related_name='organizacion')

    def __str__(self):
        return self.nombre
#############################################################################################   
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre
#############################################################################################   
class PrestacionServicioEstacion(models.Model):
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    actividad = models.BooleanField(default=True)
    def __str__(self):
        estado = 'Activo' if self.actividad else 'Inactivo'
        return f"{self.estacion.nombre}: {self.servicio.nombre} | estado -> {estado}"
#############################################################################################   
class PrestacionServicioSucursal(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    actividad = models.BooleanField(default=True)
    def __str__(self):
        estado = 'Activo' if self.actividad else 'Inactivo'
        return f"{self.sucursal.nombre}: {self.servicio.nombre} | estado -> {estado}"
    
#############################################################################################   
class ServicioPerfilEstacion(models.Model):
    servicio = models.ForeignKey(PrestacionServicioEstacion, on_delete=models.CASCADE)
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE)
    def __str__(self):
        return 'Usuario '+ self.perfil.user.username + ' esta interesado en ' + self.servicio.servicio.nombre  + ' de ' + self.servicio.estacion.nombre
    
#############################################################################################   
class ServicioPerfilSucursal(models.Model):
    servicio = models.ForeignKey(PrestacionServicioSucursal, on_delete=models.CASCADE)
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE)
    def __str__(self):
        return 'Usuario '+ self.perfil.user.username + ' esta interesado en ' + self.servicio.servicio.nombre + ' de ' + self.servicio.sucursal.nombre

#############################################################################################   
class Comunidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.nombre
############################################################################################# 
class ComunidadPerfil(models.Model):
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE)
    esAdmin = models.BooleanField(default=False)
    """ observador, un miembro de la comunidad no afectado por la tematica de la comunidad (usuarios silla de rueda) """
    observador = models.BooleanField(default=True)
    def __str__(self):
        return 'Admin de la comunidad'+ self.comunidad.nombre + '-' + self.perfil.user.username  if self.esAdmin else  'Miembro de la comunidad' + self.comunidad.nombre + ' - ' + self.perfil.user.username 

#############################################################################################   

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    comunidades = models.ManyToManyField(Comunidad, through=ComunidadPerfil, related_name='comunidades', blank=True)
    lineas = models.ManyToManyField(LineaTransporte, through=LineaPerfil, related_name='lineas', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    ultima_latitud = models.FloatField(null=True, blank=True)
    ultima_longitud = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.user.username
####################################################################  
  
class Incidente(models.Model):
    servicio = models.CharField(max_length=30)
    comunidad = models.CharField(max_length=30)
    entidad = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50, null=True)
    departamento = models.CharField(max_length=50, null=True)
    usuarioReportador = models.CharField(max_length=20, null=True)
    solucionado = models.CharField(max_length=20, null=True)
    fechaCreado = models.DateField(null=True)
    fechaCierre = models.DateField(null=True)

    def __str__(self):
        return self.servicio
    
####################################################################  

class OrganismoExterno(models.Model):
    TIPO_CHOICES = (
        ('Entidad prestadora', 'Entidad prestadora'),
        ('Organismo de Control', 'Organismo de Control'),
    )
    nombre = models.CharField(max_length=100)
    tipo_organismo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    lineas = models.ManyToManyField(LineaTransporte, related_name='lineas_org')
    organizaciones = models.ManyToManyField(Organizacion, related_name='organizaciones_org')

    def __str__(self):
        return self.nombre


####################################################################  

def crear_perfil (sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(
            user=instance,
            nombre = "Nombre",
            apellido = "Apellido",
            email = "email@monitoreo.com",
            direccion = "Dirección",
            profile_picture = 'profile_pics/profile_Default.jpg'
            )

post_save.connect(crear_perfil, sender=User)

