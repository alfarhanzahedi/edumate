from django.urls import path
from .views import CreateExam
from .views import AddQuestions

urlpatterns = [
    path('create/',CreateExam.as_view(), name='create_exam'),
    path('<int:exam_id>/add/',AddQuestions.as_view(),name='add_question')
]