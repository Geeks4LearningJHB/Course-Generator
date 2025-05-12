
from .generator import CourseGenerator  # Your existing generator code

class CourseGenerationService:
    def __init__(self):
        self.generator = CourseGenerator()
    
    def generate_course(self, topic: str, level: str = "all") -> dict:
        return self.generator.generate_course(topic, level)