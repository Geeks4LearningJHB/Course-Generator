from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PromptSerializer

class PromptReceiveAPIView(APIView):
    """
    API endpoint that receives and saves user prompts.
    It expects JSON data with 'title', 'level', and 'duration' (course duration).
    """
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create and save a new prompt.
        """
        serializer = PromptSerializer(data=request.data)
        if serializer.is_valid():
            # ModelSerializer's save() method will create a new Prompt instance
            saved_prompt = serializer.save()

            print(f"Saved Prompt: ID={saved_prompt.id}, Title='{saved_prompt.title}', Level='{saved_prompt.level}', Duration={saved_prompt.duration} mins")

            return Response(
                {"message": "Prompt received and saved successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)