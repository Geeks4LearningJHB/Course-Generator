from course_gen.core.globals import (serializers)

class WebScrapeRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    max_results = serializers.IntegerField(default=5)
    save_to_db = serializers.BooleanField(default=False)
