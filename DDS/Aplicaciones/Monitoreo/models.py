from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class Estacion(models.Model):
    nombre = models.CharField(max_length=30)
    ubicacion_geografica = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre
    
class LineaTransporte(models.Model):
    TIPO_CHOICES = (
        ('Subterraneo', 'Subterráneo'),
        ('Ferrocarril', 'Ferrocarril'),
    )

    nombre = models.CharField(max_length=100)
    estacion_origen = models.ForeignKey(Estacion, related_name='estacion_origen', on_delete=models.CASCADE)
    estacion_destino = models.ForeignKey(Estacion, related_name='estacion_destino', on_delete=models.CASCADE)
    estaciones_intermedias = models.ManyToManyField(Estacion, related_name='estaciones_intermedias')
    tipo_transporte = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre
    
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre


class PrestacionServicio(models.Model):
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)


class Comunidad(models.Model):
    nombre = models.CharField(max_length=100)
    

    def __str__(self):
        return self.nombre

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(max_length=100,blank=True, null=True)
    direccion = models.CharField(max_length=100,blank=True, null=True)
    comunidades = models.ManyToManyField(Comunidad, related_name='comunidades', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Nuevo campo para la foto de perfil
    def __str__(self):
        return self.user.username
    
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