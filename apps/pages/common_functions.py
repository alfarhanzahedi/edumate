from django.core.cache import cache

from apps.classroom.models import Classroom
from apps.classroom.forms import ClassroomCreationForm
from apps.classroom.forms import ClassroomJoinForm
from apps.accounts.models import Teacher
from apps.accounts.models import Student
from apps.exams.models import Exam
from apps.exams.forms import ExamJoinForm

def get_sidebar_context(request):
    context = {}
    context['left_sidebar'] = {}
    context['right_sidebar'] = {}

    # Common contents.
    context['right_sidebar']['classroom_join_form'] = ClassroomJoinForm()
    context['right_sidebar']['exam_join_form'] = ExamJoinForm()

    # The contents of the sidebars is different for teachers and students.
    if request.user.is_teacher:
        context['left_sidebar']['classrooms'] = Classroom.objects.filter(teacher = request.user)
        context['left_sidebar']['classroom_create_form'] = ClassroomCreationForm()
        context['left_sidebar']['exams'] = Exam.objects.filter(classroom__in = context['left_sidebar']['classrooms']).select_related('classroom')

    elif request.user.is_student:
        context['left_sidebar']['classrooms'] = request.user.student_of_classrooms.all()
        context['left_sidebar']['exams'] = request.user.exam_set.all().select_related('classroom').prefetch_related('submissions')

    return context
