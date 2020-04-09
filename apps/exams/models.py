from django.db import models
from django.utils.crypto import get_random_string
from django.core.validators import MaxValueValidator, MinValueValidator

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from apps.accounts.models import User
from apps.classroom.models import Classroom

class Exam(models.Model):
    title = models.CharField(max_length = 256)
    about = RichTextField(null = True, blank = True)
    instructions = RichTextField(null = True, blank = True)
    unique_code = models.CharField(max_length = 6, unique = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    is_open_exam = models.BooleanField(default = True)
    is_resumable = models.BooleanField(default = True)
    is_published = models.BooleanField(default = False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.IntegerField(null = True, blank = True)

    students = models.ManyToManyField(User)
    classroom = models.ForeignKey(Classroom, on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = get_random_string(6)
        return super().save(*args, **kwargs)

class Option(models.Model):
    body = models.TextField()
    is_answer = models.BooleanField(default = False)

    def __str__(self):
        return f'{self.body}'

class Question(models.Model):
    MCQ_SOC = '1'
    MCQ_MOC = '2'
    SUBJECTIVE = '3'
    TYPES = (
        (MCQ_SOC,'MCQ (Single Option Correct)'),
        (MCQ_MOC,'MCQ (Multiple Option Correct)'),
        (SUBJECTIVE,'Subjective')
    )

    exam = models.ForeignKey(Exam, on_delete = models.CASCADE)
    type = models.CharField(max_length = 1, choices = TYPES, default = MCQ_SOC)
    body = RichTextUploadingField()
    options = models.ManyToManyField(Option)
    marks = models.FloatField(default = 0, validators = [MinValueValidator(0)])
    negative_marks = models.FloatField(default = 0.0, validators = [MinValueValidator(0.0)])

    def __str__(self):
        return f'{self.body[:20]}...'
    
    def type_verbose(self):
        return dict(Question.TYPES)[self.type]

