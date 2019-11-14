from django.db import models

from apps.accounts.models import User

class Classroom(models.Model):
    teacher = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'teacher_of_classrooms')
    students = models.ManyToManyField(User, related_name = 'student_of_classrooms')
    title = models.CharField(max_length = 256)
    description = models.TextField()
    unique_code = models.CharField(max_length = 6)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
