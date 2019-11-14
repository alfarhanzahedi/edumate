from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

import uuid

from apps.accounts.models import User
from apps.accounts.decorators import teacher_required
from apps.pages.common_functions import get_sidebar_context

from .models import Classroom
from .forms import ClassroomCreationForm
from .forms import ClassroomJoinForm

class ClassroomCreateView(View):
    
    @method_decorator([login_required, teacher_required])
    def post(self, request):
        redirect_to = request.POST.get('next', '/')
        form = ClassroomCreationForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit = False)
            classroom.unique_code = uuid.uuid4().hex[:6]
            classroom.teacher = user = request.user
            classroom.save()
            return redirect('classroom_detail', id = classroom.id)
        return redirect(redirect_to)

class ClassroomDetailView(View):

    @method_decorator(login_required)
    def get(self, request, id):
        classroom = get_object_or_404(Classroom, id = id)
        if classroom.teacher != request.user and (not classroom.students.filter(username = request.user.username).exists()):
            raise Http404
        context = get_sidebar_context(request)
        context['classroom'] = {}
        context['classroom']['details'] = classroom
        context['classroom']['students'] = classroom.students.prefetch_related().all()[:5]
        context['classroom']['permissions'] = {}
        context['classroom']['permissions']['can_remove_users'] = (classroom.teacher == request.user)
        return render(request, 'classroom/classroom_detail.html', context)

class ClassroomUpdateView(View):
    pass

class ClassroomDeleteView(View):
    pass

class ClassroomJoinView(View):

    @method_decorator(login_required)
    def post(self, request):
        redirect_to = request.POST.get('next', '/')
        form = ClassroomJoinForm(request.POST)
        if form.is_valid():
            unique_code = form.cleaned_data.get('unique_code')
            classroom = Classroom.objects.get(unique_code = unique_code)
            classroom.students.add(request.user)
            classroom.save()
            messages.success(request, f'You have been added to classroom - {classroom.title}. You now have access to all its conversations and notes!')
            return redirect('classroom_detail', id = classroom.id)
        messages.error(request, f'The unique code is not associated with any classroom!')
        return redirect(redirect_to)

class ClassroomStudentRemoveView(View):

    @method_decorator(login_required)
    def post(self, request, id, username):
        try:
            user = User.objects.get(username = username)
            classroom = Classroom.objects.get(id = id)
            if classroom.teacher != request.user:
                raise Exception()
            Classroom.objects.get(id = id).students.remove(user)
            messages.success(request, f'\'{user.first_name} {user.last_name}\' was removed from the classroom successfully!')
        except Exception:
            messages.error(request, f'An unexpected error occurred. Contact support at support@edumate.com.')
        return redirect('classroom_detail', id = id)
