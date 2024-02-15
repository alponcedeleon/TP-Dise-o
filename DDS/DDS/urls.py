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
from Aplicaciones.Monitoreo.views import register, home_view, perfil_usuario, listar_comunidades,  entidad,establecimiento,servicio_perfil_estacion,eliminar_servicio_perfil_estacion
from django.urls import include
from django.contrib.auth.views import logout_then_login
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/',register, name = "register"),
    path('', home_view, name='index'),
    path('logout/',logout_then_login,name='logout'),
    path('perfil/',perfil_usuario, name = "perfil_usuario"),
    path('buscar/comunidades',listar_comunidades, name = "listar_comunidades"),
    path('entidad/<int:id>/<str:tipo>/',entidad, name = "entidad"),
    path('establecimiento/<int:id>/<str:tipo>/',establecimiento, name = "establecimiento"),
    path('servicio-perfil-estacion/<int:servicio_id>/<int:establecimiento_id>/<str:tipo>/', servicio_perfil_estacion, name='servicio_perfil_estacion'),
    path('eliminar_servicio_perfil_estacion/<int:servicio_id>/<int:establecimiento_id>/<str:tipo>/', eliminar_servicio_perfil_estacion, name='eliminar_servicio_perfil_estacion'),
]
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)