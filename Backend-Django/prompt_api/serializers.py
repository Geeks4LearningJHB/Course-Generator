from rest_framework import serializers
from .models import Prompt 

class PromptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prompt
        fields = ['id', 'title', 'level', 'duration', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at'] 

    def validate_title(self, value):
        if len(value.split()) < 0:
            raise serializers.ValidationError("Title not provided.")
        return value

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Course duration must be a positive number.")
        if value > 72:
            raise serializers.ValidationError("Course duration seems excessively long.")
        return value
