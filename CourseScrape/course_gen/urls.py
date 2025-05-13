from django.urls import path
from .views import PromptReceiveAPIView

urlpatterns = [
    path('api/prompt/', PromptReceiveAPIView.as_view(), name='prompt-receive'),
]
