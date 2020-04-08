from django.contrib import admin

from .models import Exam
from .models import Question
from .models import Option

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    pass

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    pass
