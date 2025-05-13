from django.urls import path
from .views import ScrapedContentView

urlpatterns = [
    path('search/', ScrapedContentView.as_view(), name='web-search'),
]