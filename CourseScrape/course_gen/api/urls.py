'''Module Router to organize and structure API logic'''

from django.urls import path, include

urlpatterns = [
    path('scraper/', include('course_gen.api.scrape_api.urls')),
]