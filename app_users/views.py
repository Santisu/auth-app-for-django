from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from verify_email.email_handler import send_verification_email
from .forms import LoginForm, UpdatePasswordForm, UserForm, UserProfileForm, UserRegistrationForm, VerificationForm
from .models import User, UserProfile
import dotenv
import os

dotenv.load_dotenv('.env/.verification_key')

def verify_access(view_func):
    """
    Decorator for key verification
    """
    def wrapped_view(request, *args, **kwargs):
        verification_key = request.session.get('verification_key')
        if verification_key != os.getenv('vkey'):
            return redirect('verify')
        return view_func(request, *args, **kwargs)
    return wrapped_view

class MainUserRegisterView(View):
    """
    Main user registration, a main user can only be created if it has the key
    to create a main user
    
    """
    template_name = 'register.html'
    form_class = UserRegistrationForm
    main_user = True

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('login'))  # Redirige al index
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(verify_access)
    def get(self, request):
        form = self.form_class()
        context = {'form': form,
                   'main_user': self.main_user}
        return render(request, self.template_name, context)

    @method_decorator(verify_access)
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.is_main = True
            user = send_verification_email(request, form)
            user_profile = UserProfile(user=user)
            user_profile.save()
            return redirect('index')
        context = {'form': form,
                   'main_user': self.main_user}
        return render(request, self.template_name, context)

class MinionUserRegisterView(View):

    """
    Any user that doesn't have the verification key can create not-main-account
    """
    template_name = 'register.html'
    form_class = UserRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('login'))  # Redirige al index
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user = send_verification_email(request, form)
            user_profile = UserProfile(user=user)
            user_profile.save()
            return redirect('index')
        context = {'form': form}
        return render(request, self.template_name, context)

class VerificationForMainUserView(View):
    """
    Verification view to indroduce the key
    """
    template_name = 'verification.html'
    form_class = VerificationForm

    def get(self, request):
        context = {'form': self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request):
        verification_key = request.POST.get('verification_key')
        if verification_key == os.getenv('vkey'):
            request.session['verification_key'] = verification_key
            return redirect('main_user_register')
        context = {'form': self.form_class()}
        return render(request, self.template_name, context)

class UserLoginView(View):
    """Login view"""

    form = LoginForm
    template = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('index'))  # Redirige al index
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form()
        context = {'form' : form}
        return render(request, self.template, context)
    
    def post(self, request):
        user = authenticate(request, email=request.POST['username'], password=request.POST['password'])
        if user is None:
            context = {"error": "Usuario no encontrado",
                       'form': self.form()}
            return render(request, 'login.html', context)
        else:
            login(request, user)
            return redirect('login')
            
        
@login_required
def logout(request):
    """Logout view"""
    logout(request)
    return redirect('index')


class UserProfileView(View):

    """
    Simple user profile information view
    """
    template_name = 'user_profile.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            self.user = User.objects.get(id=request.user.id)
            self.profile = UserProfile.objects.get(user=self.user)
        else:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {'user': self.user,
                   'profile': self.profile}       
        return render(request, self.template_name, context)
    
class UserProfileEditView(View):
    """
    Simple user profile update view
    """
    template_name = 'user_profile.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            self.user = User.objects.get(id=request.user.id)
            self.profile = UserProfile.objects.get(user=self.user)
            self.user_form = UserForm(instance=self.user)
            self.profile_form = UserProfileForm(instance=self.profile)
        else:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {'user_form': self.user_form, 
                   'profile_form': self.profile_form,
                    'form': True}        
        return render(request, self.template_name, context)
    

    def post(self, request):
        user_form = UserForm(request.POST, instance=self.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=self.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile')
        context = {'user_form': self.user_form, 
                   'profile_form': self.profile_form,
                   'form': True} 
        if user_form.errors or profile_form.errors:
            error = [user_form.errors, profile_form.errors]
            context['error'] = error
        
        return render(request, self.template_name, context)
    

class UpdatePasswordView(View):

    """
    Simple password update view
    """

    template_name = 'user_profile.html'
    form_class = UpdatePasswordForm

    def get(self, request):
        form = self.form_class(user=request.user)
        context = {'form_password': form,
                   'form': True}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
        context = {'form_password': form,
                   'form': True}
        return render(request, self.template_name, context)