from django.db import models

from apps.accounts.models import Student
from apps.accounts.models import Teacher

class Classroom(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    teacher = models.ForeignKey(Teacher, on_delete = models.CASCADE, related_name = 'classrooms')
    students = models.ManyToManyField(Student, related_name = 'classrooms')
    title = models.CharField(max_length = 256)
    description = models.TextField()