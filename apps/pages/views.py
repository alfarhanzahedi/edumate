from django.shortcuts import render
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage

from apps.classroom.models import Classroom
from apps.classroom.models import Post

from .common_functions import get_sidebar_context

class LandingPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            context = get_sidebar_context(request)
            context['feed'] = {}
            
            classrooms = Classroom.objects.filter(Q(teacher = request.user) | Q(students__id = request.user.id))
            post_list = Post.objects.select_related('user', 'classroom', 'classroom__teacher').filter(classroom__in = classrooms).order_by('-updated_at')
            page = request.GET.get('page', 1)
            paginator = Paginator(post_list, 2)
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)

            context['feed']['posts'] = posts
            return render(request, 'pages/feed.html', context)
        return render(request, 'pages/landing_page.html')
