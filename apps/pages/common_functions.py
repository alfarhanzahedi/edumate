from apps.classroom.forms import ClassroomCreationForm
from apps.classroom.forms import ClassroomJoinForm
from apps.classroom.models import Classroom
from apps.accounts.models import Teacher
from apps.accounts.models import Student

def get_sidebar_context(request):
    context = {}
    context['left_sidebar'] = {}
    context['right_sidebar'] = {}
    if request.user.is_teacher:
        context['left_sidebar']['classroom_create_form'] = ClassroomCreationForm()
        context['left_sidebar']['classrooms'] = Classroom.objects.filter(teacher = request.user)
    elif request.user.is_student:
        context['left_sidebar']['classrooms'] = request.user.student_of_classrooms.all()
    context['right_sidebar']['classroom_join_form'] = ClassroomJoinForm()
    return context
