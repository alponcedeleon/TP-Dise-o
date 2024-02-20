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
    path('crear-comunidad/', views.crear_solicitud_comunidad, name='crear_comunidad'),
    path('mis-comunidades/', views.listar_comunidades_perfil, name='listar_comunidades_perfil'),
    path('administrar-comunidad/<int:id_comunidad>', views.administrar_comunidad, name='administrar_comunidad'),
    path('eliminar_miembro/<int:perfil_id>/<int:comunidad_id>/', views.eliminar_miembro, name='eliminar_miembro'),
    path('designar_admin/<int:perfil_id>/<int:comunidad_id>/', views.designar_admin, name='designar_admin'),
    path('sacar_admin/<int:perfil_id>/<int:comunidad_id>/', views.sacar_admin, name='sacar_admin'),
    path('entidad/<int:id>/<str:tipo>/',views.entidad, name = "entidad"),
    path('establecimiento/<int:id>/<str:tipo>/',views.establecimiento, name = "establecimiento"),
    path('servicio-perfil-estacion/<int:servicio_id>/<int:establecimiento_id>/<str:tipo>/', views.servicio_perfil_estacion, name='servicio_perfil_estacion'),
    path('reportar_incidente/<int:servicio_id>/<int:establecimiento_id>/<str:comunidades_nombres>/<str:tipo>/', views.reportar_incidente, name='reportar_incidente'),
    path('get-location/', views.get_location, name='get_location'),
    path('process-location/', views.process_location, name='process_location'),
    path('eliminar_servicio_perfil_estacion/<int:servicio_id>/<int:establecimiento_id>/<str:tipo>/', views.eliminar_servicio_perfil_estacion, name='eliminar_servicio_perfil_estacion'),
    path('cargar-datos/', views.cargar_datos_desde_csv, name='cargar_datos'),
    path('salir_comunidad/<int:comunidad_id>/<str:pag_redirect>/<str:tipo>/', views.salir_comunidad, name='salir_comunidad'),
]
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)