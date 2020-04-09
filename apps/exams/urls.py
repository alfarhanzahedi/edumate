from django.urls import path

from .views import ExamCreateView
from .views import ExamDetailView
from .views import ExamUpdateView
from .views import ExamPublishView
from .views import ExamQuestionCreateView
from .views import ExamQuestionUpdateView
from .views import ExamQuestionDeleteView

urlpatterns = [
    path('create/', ExamCreateView.as_view(), name = 'exam_create'),
    path('<int:exam_id>/', ExamDetailView.as_view(), name = 'exam_detail'),
    path('<int:exam_id>/update/', ExamUpdateView.as_view(), name = 'exam_update'),
    path('<int:exam_id>/publish/', ExamPublishView.as_view(), name = 'exam_publish'),
    path('<int:exam_id>/question/create/', ExamQuestionCreateView.as_view(), name = 'question_create'),
    path('<int:exam_id>/question/<int:question_id>/update/', ExamQuestionUpdateView.as_view(), name = 'question_update'),
    path('<int:exam_id>/question/<int:question_id>/delete/', ExamQuestionDeleteView.as_view(), name = 'question_delete')
]
