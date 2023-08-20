from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
import os
import uuid
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

def avatar_file_path(instance, filename):
    """Set the path of the avatar with a random filename"""
    extension = os.path.splitext(filename)[1]
    random_filename = f"{uuid.uuid4().hex}{extension}"
    return os.path.join('avatar_pics/', random_filename)

def cv_file_path(instance, filename):
    """Set the path of the CV file with user's first name and last name"""
    extension = os.path.splitext(filename)[1]
    filename = f"{instance.user.first_name}_{instance.user.last_name}_{instance.user.id}_CV{extension}"
    return os.path.join('cv_files/', filename)

############################################################################################################

class User(AbstractUser):
    """
    Custom user model, it sets the email instead of username,
    adds the boolean to identify a main user.
    Remember tu set in settings:
        AUTH_USER_MODEL='users.User'
    """
    email = models.EmailField('Correo electrónico', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    is_main = models.BooleanField(default=False)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.email

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'



class UserProfile(models.Model):
    """
    Profile information of every user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    bio_short = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    linkedin = models.URLField(max_length=200, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=avatar_file_path)
    cv = models.FileField(null=True, blank=True, upload_to=cv_file_path)

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        else:
            return self.user.email
        

@receiver(post_save, sender=UserProfile)
def resize_avatar(sender, instance, **kwargs):
    if instance.avatar and instance.avatar.path:
        img = Image.open(instance.avatar.path)
        desired_height = 500
        aspect_ratio = img.height / img.width
        desired_width = int(desired_height / aspect_ratio)
        img = img.resize((desired_width, desired_height), Image.LANCZOS)
        quality = 100
        img_format = 'JPEG'
        img.save(instance.avatar.path, format=img_format, quality=quality, optimize=True)

@receiver(pre_delete, sender=UserProfile)
def delete_picture_files(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)