from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DetailView

class ClassroomCreateView(CreateView):
    pass

class ClassroomUpdateView(UpdateView):
    pass

class ClassroomDeleteView(DetailView):
    pass