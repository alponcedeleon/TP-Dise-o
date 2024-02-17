from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Perfil, Categoria,SolicitudComunidad


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

class FormularioServicio(forms.Form):
    nombre = forms.CharField(label='Nombre del servicio', max_length=100)
    categoria = forms.ChoiceField(label='Categoría', choices=[])

    def __init__(self, *args, **kwargs):
        super(FormularioServicio, self).__init__(*args, **kwargs)
        categorias = Categoria.objects.all()
        choices = [(categoria.id, categoria.nombre) for categoria in categorias]
        self.fields['categoria'].choices = choices

class CSVUploadForm(forms.Form):
    archivo_csv = forms.FileField(widget=forms.FileInput(attrs={'class': 'boton-fileupload'}))
