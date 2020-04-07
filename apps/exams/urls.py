from django.urls import path

from .views import ExamCreateView
from .views import ExamDetailView
from .views import ExamUpdateView

urlpatterns = [
    path('create/', ExamCreateView.as_view(), name = 'exam_create'),
    path('<int:exam_id>/', ExamDetailView.as_view(), name = 'exam_detail'),
    path('<int:exam_id>/update/', ExamUpdateView.as_view(), name = 'exam_update')
]
