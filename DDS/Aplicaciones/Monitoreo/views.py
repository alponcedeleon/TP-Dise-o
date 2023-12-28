from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm , UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm , UserProfileForm
from .models import Perfil
from .requests import obtener_localidades, obtener_provincias
from django.contrib.auth.decorators import login_required, user_passes_test
import logging

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

@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url='/admin/')
def home_view(request):
    # Obtener grupos a los que pertenece el usuario
    user = request.user
    user_groups = user.groups.all()
    group_names = [group.name for group in user_groups]
    
    # Obtener el perfil del usuario actual, si existe
    perfil_usuario = get_object_or_404(Perfil, user=request.user)

    # Contexto con los datos del perfil para pasar a la plantilla
    context = {
        'request':request,
        'perfil_usuario': perfil_usuario,
        'groups':group_names
    }
    logging.info(request.path)
    return render(request, 'index.html', context)


"""
def perfil_usuario(request):
    
    # Obtener el perfil del usuario actual, si existe
    perfil_usuario = get_object_or_404(Perfil, user=request.user)

    # Contexto con los datos del perfil para pasar a la plantilla
    context = {
        'perfil_usuario': perfil_usuario,
    }

    return render(request, 'perfil.html', context)
    """
@login_required
def perfil_usuario(request):
    # Obtener grupos a los que pertenece el usuario
    user = request.user
    user_groups = user.groups.all()
    group_names = [group.name for group in user_groups]
    
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