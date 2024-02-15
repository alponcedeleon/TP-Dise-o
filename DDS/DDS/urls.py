"""
URL configuration for DDS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Aplicaciones.Monitoreo import views
from django.urls import include
from django.contrib.auth.views import logout_then_login
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/',views.register, name = "register"),
    path('', views.home_view, name='index'),
    path('logout/',logout_then_login,name='logout'),
    path('perfil/',views.perfil_usuario, name = "perfil_usuario"),
    path('buscar/comunidades',views.listar_comunidades, name = "listar_comunidades"),
    path('crear-comunidad/', views.crear_comunidad, name='crear_comunidad'),
    path('mis-comunidades/', views.listar_comunidades_perfil, name='listar_comunidades_perfil'),
    path('entidad/<int:id>/<str:tipo>/',views.entidad, name = "entidad"),
    path('establecimiento/<int:id>/<str:tipo>/',views.establecimiento, name = "establecimiento"),
    path('servicio-perfil-estacion/<int:servicio_id>/<int:establecimiento_id>/<str:tipo>/', views.servicio_perfil_estacion, name='servicio_perfil_estacion'),
    path('get-location/', views.get_location, name='get_location'),
    path('process-location/', views.process_location, name='process_location'),
    path('eliminar_servicio_perfil_estacion/<int:servicio_id>/<int:establecimiento_id>/<str:tipo>/', views.eliminar_servicio_perfil_estacion, name='eliminar_servicio_perfil_estacion'),
    path('cargar-datos/', views.cargar_datos_desde_csv, name='cargar_datos'),
    path('calcular-ranking1/', views.entidades_con_mayor_tiempo_promedio_de_tiempo_de_cierre_de_incidentes, name='calcular-ranking1'),
    path('calcular-ranking2/', views.entidades_con_mayor_incidentes_reportados_en_la_semana, name='calcular-ranking2')
]
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)