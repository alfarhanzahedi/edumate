from django.urls import path

from .views import ClassroomCreateView
from .views import ClassroomDetailView
from .views import ClassroomUpdateView
from .views import ClassroomDeleteView
from .views import ClassroomJoinView
from .views import ClassroomStudentRemoveView
from .views import ClassroomPostCreateView
from .views import ClassroomPostDetailView
from .views import ClassroomPostUpdateView
from .views import ClassroomPostDeleteView
from .views import ClassroomPostCommentCreateView
from .views import ClassroomPostCommendDeleteView

urlpatterns = [
    path('create/', ClassroomCreateView.as_view(), name = 'classroom_create'),
    path('<int:id>/', ClassroomDetailView.as_view(), name = 'classroom_detail'),
    path('<int:id>/update/', ClassroomUpdateView.as_view(), name = 'classroom_update'),
    path('<int:id>/delete/', ClassroomDeleteView.as_view(), name = 'classroom_delete'),
    path('join/', ClassroomJoinView.as_view(), name = 'classroom_join'),
    path('<int:id>/<str:username>/delete/', ClassroomStudentRemoveView.as_view(), name = 'classroom_student_remove'),
    path('<int:classroom_id>/post/create/', ClassroomPostCreateView.as_view(), name = 'classroom_post_create'),
    path('<int:classroom_id>/post/<int:post_id>/', ClassroomPostDetailView.as_view(), name = 'classroom_post_detail'),
    path('<int:classroom_id>/post/<int:post_id>/update/', ClassroomPostUpdateView.as_view(), name = 'classroom_post_update'),
    path('<int:classroom_id>/post/<int:post_id>/delete/', ClassroomPostDeleteView.as_view(), name = 'classroom_post_delete'),
    path('<int:classroom_id>/post/<int:post_id>/comment/create/', ClassroomPostCommentCreateView.as_view(), name = 'classroom_post_comment_create'),
    path('<int:classroom_id>/post/<int:post_id>/comment/<int:comment_id>/delete/', ClassroomPostCommendDeleteView.as_view(), name = 'classroom_post_comment_delete'),
]
