import os
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PromptSerializer
from .models import Prompt
from .services import CourseGenerator

class CourseGenerationAPIView(APIView):
    async def post(self, request, *args, **kwargs):
        serializer = PromptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            saved_prompt = serializer.save()
            generator = CourseGenerator()
            
            prompt_data = {
                'courseTitle': saved_prompt.courseTitle,
                'difficulty': saved_prompt.difficulty,
                'duration': saved_prompt.duration
            }
            
            course = await generator.generate_course(prompt_data)
            
            return Response({
                "status": "success",
                "course_id": course.get('_id'),
                "data": course['course']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)