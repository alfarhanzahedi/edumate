from django.db import models
from apps.accounts.models import User
from apps.classroom.models import Classroom


# Create your models here.

class Exams(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete = models.CASCADE, related_name = 'exams_in_classroom')
    students = models.ManyToManyField(User, related_name = 'exams_takenby_student')
    title = models.CharField(max_length = 256)
    description = models.TextField()
    instructions = models.TextField()
    unique_code = models.CharField(max_length = 6)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    total_marks = models.IntegerField(null=True)
    active_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def __str__(self):
        return self.title

class Questions(models.Model):
    exam =  models.ForeignKey(Exams, on_delete = models.CASCADE, related_name = 'Questions_in_exam')
    types = (
            ('1','MCQ(Single Option Correct)'),
            ('2','MCQ(Multiple Option Correct)'),
            ('3','Subjective')
            )
    q_type = models.CharField(max_length=1,choices=types,default='1')
    body = models.TextField()
    marks = models.IntegerField(blank=False)
    img = models.ImageField(upload_to='uploads/exams/',blank=True, null=True )
    def __str__(self):
        return self.body

class Options(models.Model):
    question =  models.ForeignKey(Questions, on_delete = models.CASCADE, related_name = 'Options_for_Questions')
    text = models.TextField()
    ans = models.BooleanField(default=False)

    def __str__(self):
        return self.text


