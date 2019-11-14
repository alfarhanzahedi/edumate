from django.shortcuts import render
from django.views import View

from .common_functions import get_sidebar_context

class LandingPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            context = get_sidebar_context(request)
            return render(request, 'pages/feed.html', context)
        return render(request, 'pages/landing_page.html')
