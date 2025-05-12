from django.shortcuts import render
from django.views import View
from .services import CourseGenerationService
import json

class GenerateCourseView(View):
    template_name = 'course_generator/generate.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        topic = request.POST.get('topic', '')
        level = request.POST.get('level', 'all')
        
        service = CourseGenerationService()
        course = service.generate_course(topic, level)
        
        context = {
            'course': course,
            'course_json': json.dumps(course, indent=2),
            'topic': topic,
            'level': level,
        }
        return render(request, self.template_name, context)