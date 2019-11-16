from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage

import uuid

from apps.accounts.models import User
from apps.accounts.decorators import teacher_required
from apps.pages.common_functions import get_sidebar_context

from .models import Classroom
from .models import Post
from .models import Comment
from .forms import ClassroomCreationForm
from .forms import ClassroomJoinForm
from .forms import ClassroomPostCreateForm

def in_classroom(classroom, user):
    if classroom.teacher == user or classroom.students.filter(username = user.username).exists():
        return True
    return False

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
        classroom = get_object_or_404(Classroom.objects.select_related('teacher'), id = id)
        if not in_classroom(classroom, request.user):
            raise Http404
        context = get_sidebar_context(request)
        context['classroom'] = {}
        context['classroom']['details'] = classroom
        context['classroom']['students'] = classroom.students.prefetch_related().all()[:5]
        context['classroom']['permissions'] = {}
        context['classroom']['permissions']['can_remove_users'] = (classroom.teacher == request.user)
        context['classroom']['permissions']['can_remove_posts'] = (classroom.teacher == request.user)
        context['classroom']['forms'] = {}
        context['classroom']['forms']['post_create_form'] = ClassroomPostCreateForm()
        
        post_list = Post.objects.select_related('user').filter(classroom = classroom).order_by('-updated_at')
        page = request.GET.get('page', 1)

        paginator = Paginator(post_list, 2)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['classroom']['posts'] = posts
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
            classroom = Classroom.objects.prefetch_related('students').get(unique_code = unique_code)
            if in_classroom(classroom, request.user):
                messages.success(request, f'You are already a member of the classroom - {classroom.title}.')
                return redirect('classroom_detail', id = classroom.id)    
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

class ClassroomPostCreateView(View):
    
    @method_decorator(login_required)
    def post(self, request, classroom_id):
        form = ClassroomPostCreateForm(request.POST)
        html_post = request.POST.get('html_data')
        if form.is_valid():
            try:
                classroom = Classroom.objects.get(id = classroom_id)
                print(form.cleaned_data.get('post'))
                if not in_classroom(classroom, request.user):
                    raise Exception()
                Post.objects.create(
                    classroom = classroom,
                    user = request.user,
                    post = html_post
                )
                messages.success(request, f'Post added successfully!')
            except Exception:
                messages.error(request, f'An unexpected error occurred. Contact support at support@edumate.com.')
            return redirect('classroom_detail', id = classroom_id)

        messages.error(request, f'Empty posts are not allowed!')
        return redirect('classroom_detail', id = classroom_id)

class ClassroomPostDeleteView(View):
    
    @method_decorator(login_required)
    def post(self, request, classroom_id, post_id):
        redirect_to = request.POST.get('next', '/')
        try:
            classroom = Classroom.objects.get(id = classroom_id)
            post = Post.objects.get(id = post_id)
            if post.user == request.user or classroom.teacher == request.user:
                post.delete()
                messages.success(request, f'The post was deleted successfully!')
                return redirect(redirect_to)
            raise Exception()
        except Exception:
            messages.error(request, f'An unexpected error occurred. Contact support at support@edumate.com.')
        return redirect(redirect_to)

class ClassroomPostCommentCreateView(View):
    pass

class ClassroomPostCommendDeleteView(View):
    pass
