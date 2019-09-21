from django.shortcuts import render
from django.views import View

class LandingPage(View):
    def get(self, request):
        return render(request, 'pages/landing_page.html')
