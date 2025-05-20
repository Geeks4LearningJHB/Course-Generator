from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializer import CourseGenerationRequestSerializer
from course_gen.services.course_generator import CourseGenerator
import logging

logger = logging.getLogger(__name__)

@authentication_classes([])
@permission_classes([AllowAny])
class CourseGenerationAPI(APIView):
    """
    API endpoint for generating courses
    """
    @csrf_exempt
    def post(self, request):
        serializer = CourseGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            topic = serializer.validated_data['topic']
            level = serializer.validated_data['level']
            save_to_db = serializer.validated_data['save_to_db']

            generator = CourseGenerator()
            course = generator.generate_course(
                topic=topic,
                level=level,
                save_to_db=save_to_db
            )

            response_data = {
                'status': 'success',
                'course': course
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Course generation failed: {str(e)}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
