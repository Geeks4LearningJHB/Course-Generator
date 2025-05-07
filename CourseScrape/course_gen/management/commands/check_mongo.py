from django.core.management.base import BaseCommand
from ...services.database_manager import DatabaseManager

class Command(BaseCommand):
    help = "Checks MongoDB connection and lists available courses"

    def handle(self, *args, **options):
        try:
            db_manager = DatabaseManager()
            courses = db_manager.list_courses(limit=5)
            
            self.stdout.write(self.style.SUCCESS(f"✓ MongoDB connection successful"))
            self.stdout.write(f"Found {len(courses)} courses:")
            
            for course in courses:
                self.stdout.write(f"- {course['title']} (ID: {course['_id']})")
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ MongoDB error: {str(e)}"))