from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django import forms
from .models import Profile, Order

# Aquí se crean las clases de los formularios necesarios para la tienda
# nótese que todos ellos cruzan su lógica con los atributos de bootstrap, de ahí su complejidad
# Este formulario está vinculado al modelo Profile
# y se utiliza para actualizar la información del perfil del usuario.

# Formulario de orden de compra para el cliente de salón

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'dni','email', 'address', 'postal_code', 'city']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'dni': 'DNI',
            'email': 'Correo electrónico',
            'address': 'Dirección',
            'postal_code': 'Código postal',
            'city': 'Ciudad',
        }


class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nombre'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Apellido'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'Nombre de Usuario'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Requerido. 150 caracteres o menos. Letras, dígitos y@/./+/-/_ únicamente.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Contraseña'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Su contraseña no puede ser muy similar a su otra información personal.</li><li>Su contraseña debe contener al menos 8 caracteres.</li><li>Su contraseña no puede ser una contraseña de uso común. </li><li>Su contraseña no puede ser completamente numérica.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirmar Contraseña'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Ingrese la misma contraseña que antes, para verificación.</small></span>'