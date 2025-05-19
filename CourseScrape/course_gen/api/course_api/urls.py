from django.urls import path
from .views import CourseGenerationAPI

urlpatterns = [
    path('generate-course/', CourseGenerationAPI.as_view(), name='generate-course'),
]