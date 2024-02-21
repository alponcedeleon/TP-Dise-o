from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Perfil, Categoria,SolicitudComunidad, SolicitudServicio


class CustomUserCreationForm(UserCreationForm):
    pass

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre', 'apellido','email', 'direccion', 'departamento' , 'profile_picture']
        # Asegúrate de incluir 'profile_picture' si es el campo para la foto de perfil en tu modelo
       # widgets = {
       #     'comunidades': forms.CheckboxSelectMultiple()  # Esto es un ejemplo, puedes cambiar el widget según tu necesidad
       # }

class SolicitudComunidadForm(forms.ModelForm):
    class Meta:
        model = SolicitudComunidad
        fields = ['nombre', 'descripcion', 'perfil', 'motivo']

class SolicitudServicio(forms.ModelForm):
    class Meta:
        model = SolicitudServicio
        fields = ['nombre', 'categoria', 'categoria_alternativa' ,'comunidad','perfil', 'motivo']

    

class CSVUploadForm(forms.Form):
    archivo_csv = forms.FileField(widget=forms.FileInput(attrs={'class': 'boton-fileupload'}))
