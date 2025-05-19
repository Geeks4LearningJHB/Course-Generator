from django.urls import path
from .views import CourseGenerationAPIView

urlpatterns = [
    path('api/prompt/', CourseGenerationAPIView.as_view(), name='prompt-receive'),
]
