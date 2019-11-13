from django.urls import path

from .views import ClassroomCreateView
from .views import ClassroomDetailView
from .views import ClassroomUpdateView
from .views import ClassroomDeleteView

urlpatterns = [
    path('classroom/create/', ClassroomCreateView.as_view(), name = 'classroom_create'),
    path('classroom/<uuid:uuid>/', ClassroomDetailView.as_view(), name = 'classroom_detail'),
    path('classroom/<uuid:uuid>/update/', ClassroomUpdateView.as_view(), name = 'classroom_update'),
    path('classroom/<uuid:uuid>/delete/', ClassroomDeleteView.as_view(), name = 'classroom_delete'),
]
