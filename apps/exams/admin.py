from django.contrib import admin

from .models import Exam
from .models import Question
from .models import Option
from .models import Submission
from .models import Answer

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    pass

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    pass

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    readonly_fields = ('started_at', 'ended_at')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    pass
