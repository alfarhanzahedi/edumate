from django.urls import path

from .views import ExamCreateView
from .views import ExamDetailView
from .views import ExamUpdateView
from .views import ExamPublishView
from .views import ExamQuestionCreateView
from .views import ExamQuestionUpdateView
from .views import ExamQuestionDeleteView
from .views import ExamStartView
from .views import ExamResumeView
from .views import ExamEndView
from .views import ExamEvaluateView
from .views import SubmissionDetailView
from .views import SubmissionEvaluateView
from .views import AnswerView
from .views import AnswerEvaluateView

urlpatterns = [
    path('create/', ExamCreateView.as_view(), name = 'exam_create'),
    path('<int:exam_id>/', ExamDetailView.as_view(), name = 'exam_detail'),
    path('<int:exam_id>/update/', ExamUpdateView.as_view(), name = 'exam_update'),
    path('<int:exam_id>/publish/', ExamPublishView.as_view(), name = 'exam_publish'),
    path('<int:exam_id>/question/create/', ExamQuestionCreateView.as_view(), name = 'question_create'),
    path('<int:exam_id>/question/<int:question_id>/update/', ExamQuestionUpdateView.as_view(), name = 'question_update'),
    path('<int:exam_id>/question/<int:question_id>/delete/', ExamQuestionDeleteView.as_view(), name = 'question_delete'),
    path('<int:exam_id>/start/', ExamStartView.as_view(), name = 'exam_start'),
    path('<int:exam_id>/resume/', ExamResumeView.as_view(), name = 'exam_resume'),
    path('<int:exam_id>/end/', ExamEndView.as_view(), name = 'exam_end'),
    path('<int:exam_id>/evaluate/', ExamEvaluateView.as_view(), name = 'exam_evaluate'),
    path('<int:exam_id>/submission/<int:submission_id>/', SubmissionDetailView.as_view(), name = 'submission_detail'),
    path('<int:exam_id>/submission/<int:submission_id>/evaluate/', SubmissionEvaluateView.as_view(), name = 'submission_evaluate'),
    path('<int:exam_id>/submission/<int:submission_id>/question/<int:question_id>/answer/', AnswerView.as_view(), name = 'answer'),
    path('<int:exam_id>/submission/<int:submission_id>/question/<int:question_id>/evaluate/', AnswerEvaluateView.as_view(), name = 'answer_evaluate'),
]
