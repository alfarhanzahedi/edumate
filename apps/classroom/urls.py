from django.urls import path

from .views import ClassroomCreateView
from .views import ClassroomDetailView
from .views import ClassroomUpdateView
from .views import ClassroomDeleteView
from .views import ClassroomJoinView

urlpatterns = [
    path('create/', ClassroomCreateView.as_view(), name = 'classroom_create'),
    path('<int:id>/', ClassroomDetailView.as_view(), name = 'classroom_detail'),
    path('<int:id>/update/', ClassroomUpdateView.as_view(), name = 'classroom_update'),
    path('<int:id>/delete/', ClassroomDeleteView.as_view(), name = 'classroom_delete'),
    path('join/', ClassroomJoinView.as_view(), name = 'classroom_join'),
]
