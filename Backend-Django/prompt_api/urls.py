from django.urls import path
from .views import PromptReceiveAPIView

urlpatterns = [
    path('receive-prompt/', PromptReceiveAPIView.as_view(), name='receive-prompt'),
]