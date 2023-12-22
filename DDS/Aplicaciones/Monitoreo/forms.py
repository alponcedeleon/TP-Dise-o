from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil

class CustomUserCreationForm(UserCreationForm):
    pass

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre', 'apellido','email', 'direccion' ,'comunidades', 'profile_picture']
        # Asegúrate de incluir 'profile_picture' si es el campo para la foto de perfil en tu modelo
        widgets = {
            'comunidades': forms.CheckboxSelectMultiple()  # Esto es un ejemplo, puedes cambiar el widget según tu necesidad
        }
