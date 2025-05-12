# course_generator/urls.py
from django.urls import path
from .views import GenerateCourseView

urlpatterns = [
    path('generate/', GenerateCourseView.as_view(), name='generate_course'),
]