from django.contrib.auth.models import AbstractUser
from django.db import models

import uuid

def upload_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    return f'{uuid.uuid4()}.{extension}'

class User(AbstractUser):
    is_student = models.BooleanField(default = False)
    is_teacher = models.BooleanField(default = False)

    profile_picture = models.ImageField(upload_to = upload_directory_path, null = True, blank = True)
    email_verified = models.BooleanField(default = False)

    def __str__(self):
        return self.username

class Student(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)

    def __str__(self):
        return self.user.username
