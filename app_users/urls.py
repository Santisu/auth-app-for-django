from django.urls import path
from .views import MainUserRegisterView, MinionUserRegisterView, UpdatePasswordView, UserLoginView, UserProfileEditView, VerificationForMainUserView, logout, UserProfileView

urlpatterns = [
    path('register/main-user/', MainUserRegisterView.as_view(), name='main_user_register'),
    path('register/', MinionUserRegisterView.as_view(), name='minion_user_register'),
    path('verify/', VerificationForMainUserView.as_view(), name='verify'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', UserProfileEditView.as_view(), name='user_profile_edit'),
    path('profile/edit/password/', UpdatePasswordView.as_view(), name='update_password'),

]