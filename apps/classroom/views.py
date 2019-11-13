from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from apps.accounts.decorators import teacher_required

from .models import Classroom
from .forms import ClassroomCreationForm

class ClassroomCreateView(View):
    
    @method_decorator([login_required, teacher_required])
    def get(self, request):
        form = ClassroomCreationForm()
        return render(request, 'classroom/classroom_create_form.html', {'form': form})

    @method_decorator([login_required, teacher_required])
    def post(self, request):
        form = ClassroomCreationForm(request.POST)
        if form.is_valid:
            classroom = form.save()
            return redirect()
        return render(request, 'classroom/classroom_create_form.html', {'form': form})

class ClassroomDetailView(View):

    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'classroom/classroom_detail_template.html')


class ClassroomUpdateView(View):
    pass

class ClassroomDeleteView(View):
    pass