from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User, UserProfile

class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        labels = {
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'password1': 'Contraseña',
            'password2': 'Confirmación contraseña',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class LoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ('email', 'password')
        labels = {
            'email': 'Correo electrónico',
            'password': 'Contraseña',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class VerificationForm(forms.Form):
    verification_key = forms.CharField(
        max_length=20, widget=forms.TextInput(
        attrs={'placeholder': 'Ingrese la clave de verificación'}
        ))
    

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'bio_short', 'linkedin', 'cv']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'bio_short': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'cv': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'avatar': 'Foto de perfil',
            'bio': 'Descripción principal',
            'bio_short': 'Descripción corta',
            'linkedin': 'LinkedIn',
            'cv': 'Curriculum Vitae',
        }

class UserForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }

class UpdatePasswordForm(PasswordChangeForm):
    class Meta:
        model = User 
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})