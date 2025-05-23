from course_gen.core.globals import (logging, APIView, Response, status)

from .serializer import CourseGenerationRequestSerializer
from course_gen.services.course_generator import CourseGenerator

logger = logging.getLogger(__name__)

class CourseGenerationAPI(APIView):
    """
    API endpoint for generating courses
    """
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