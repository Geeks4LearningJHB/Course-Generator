from rest_framework import serializers

class CourseGenerationRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(required=True, max_length=100)
    level = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced'],
        default='beginner'
    )
    save_to_db = serializers.BooleanField(default=False)