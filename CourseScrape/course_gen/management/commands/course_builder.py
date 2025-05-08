from django.core.management.base import BaseCommand
from ...services.interactive import CourseBuilderInterface
from ...services.database_manager import DatabaseManager

class Command(BaseCommand):
    help = 'Run the AI Course Builder Interface'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use_db',
            action='store_true',
            help='Enable database integration for course storage'
        )

    def handle(self, *args, **options):
        print(">>> Starting CourseBuilderInterface...")

        db_manager = DatabaseManager() if options['use_db'] else None
        interface = CourseBuilderInterface(db_manager=db_manager)
        interface.interactive_mode()
