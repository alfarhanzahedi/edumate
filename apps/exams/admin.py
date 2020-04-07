from django.contrib import admin

from apps.exams.models import Exam

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    pass
