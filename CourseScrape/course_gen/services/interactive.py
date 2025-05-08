from course_gen.core.globals import (
    List, Dict, logger, Optional
)

from typing import Optional
from .course_generator import CourseGenerator
from .knowledge_scraper import KnowledgeScraper

class CourseBuilderInterface:
    """
    Interactive interface for AI Course Builder with these features:
    - Course generation from scraped knowledge
    - Interactive menu system
    - Database integration (optional)
    - Markdown export
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize with optional database manager
        
        Args:
            db_manager: Database manager instance (optional)
        """
        self.generator = CourseGenerator()
        self.scraper = KnowledgeScraper()
        self.db_manager = db_manager
        self._current_page = 0  # For pagination
        
    @property
    def knowledge(self) -> List[Dict]:
        """Access the current knowledge base"""
        return self.generator.knowledge
        
    @knowledge.setter
    def knowledge(self, value: List[Dict]):
        """Update the knowledge base"""
        self.generator.knowledge = value
        
    def interactive_mode(self):
        logger.info("Interactive mode loop triggered")

        """Main interactive loop"""
        print("\n" + "="*60)
        print("AI COURSE BUILDER".center(60))
        print("="*60)
        
        while True:
            self._display_main_menu()
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                self._handle_course_creation()
            elif choice == "2":
                self._update_knowledge_base()
            elif choice == "3":
                self._list_topics()
            elif choice == "4":
                self._browse_courses()
            elif choice == "5":
                self._search_courses()
            elif choice == "6":
                print("\nThank you for using AI Course Generator!")
                break
            else:
                print("\nInvalid choice. Please try again.")

    # Menu Handlers
    def _display_main_menu(self):
        """Display the main menu options"""
        print("\n" + "-"*60)
        print("MAIN MENU".center(60))
        print("-"*60)
        print("1. Create New Course")
        print("2. Update Knowledge Base")
        print("3. List Available Topics")
        print("4. Browse Saved Courses")
        print("5. Search Courses")
        print("6. Exit")
        print("-"*60)

    def _handle_course_creation(self):
        """Handle course creation workflow"""
        print("\nCreate New Course")
        print("-----------------")
        
        topic = input("Enter a topic: ").strip().lower()
        if not topic:
            print("No topic entered. Returning to main menu.")
            return
            
        level = input("Enter level (beginner/intermediate/advanced): ").strip().lower()
        level = level if level in ["beginner", "intermediate", "advanced"] else "beginner"
        
        print(f"\nGenerating {level} course for '{topic}'...")
        course = self.generator.generate_course(topic, level)
        
        if "error" in course:
            print(f"Error: {course['error']}")
            return
            
        print("\nCourse created successfully!")
        print(f"Title: {course['title']}")
        print(f"Modules: {len(course['modules'])}")
        
        self._handle_course_save(course)

    def _update_knowledge_base(self):
        """Update the knowledge base by scraping"""
        print("\nUpdating knowledge base...")
        try:
            self.knowledge = self.scraper.scrape_knowledge_base()
            self.generator.load_knowledge()
            print("\nKnowledge base updated successfully!")
        except Exception as e:
            logger.error(f"Failed to update knowledge: {str(e)}")
            print("\nFailed to update knowledge base. Check logs for details.")

    def _list_topics(self):
        """List available topics in knowledge base"""
        topics = sorted({item['topic'] for item in self.knowledge})
        print("\nAvailable Topics:")
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic.title()}")

    # Database Operations
    def _browse_courses(self):
        """Browse saved courses with pagination"""
        if not self.db_manager:
            print("\nDatabase not connected.")
            return
            
        while True:
            courses = self.db_manager.list_courses(limit=10, offset=self._current_page*10)
            if not courses:
                print("\nNo courses found.")
                break
                
            self._display_courses(courses)
            action = input("\n[n]ext [p]rev [v#]view [b]ack: ").lower()
            
            if action == 'b':
                break
            elif action == 'n':
                self._current_page += 1
            elif action == 'p' and self._current_page > 0:
                self._current_page -= 1
            elif action.startswith('v'):
                self._view_course_detail(action[1:], courses)

    def _search_courses(self):
        """Search courses in database"""
        if not self.db_manager:
            print("\nDatabase not connected.")
            return
            
        query = input("\nSearch term: ").strip()
        if not query:
            return
            
        results = self.db_manager.search_courses(query)
        if not results:
            print("\nNo matching courses found.")
            return
            
        self._display_courses(results)
        selection = input("\nEnter # to view or [b]ack: ").lower()
        if selection.isdigit():
            self._view_course_detail(selection, results)

    # Helper Methods
    def _display_courses(self, courses: List[Dict]):
        """Display list of courses"""
        print("\nSaved Courses:")
        for i, course in enumerate(courses, 1):
            print(f"{i}. {course['title']}")

    def _view_course_detail(self, selection: str, courses: List[Dict]):
        """View detailed course information"""
        try:
            idx = int(selection) - 1
            course = courses[idx]
            print("\n" + "="*60)
            print(f"{course['title']}".center(60))
            print("="*60)
            print(f"Topic: {course['topic']}")
            print(f"Level: {course['level']}")
            print(f"Modules: {len(course['modules'])}")
            
            if input("\nExport to Markdown? [y/N]: ").lower() == 'y':
                filename = input("Filename (blank for default): ").strip()
                self.generator.export_markdown(course, filename or None)
        except (ValueError, IndexError):
            print("\nInvalid selection")

    def _handle_course_save(self, course: Dict):
        """Handle course saving options"""
        if input("\nSave to Markdown? [y/N]: ").lower() == 'y':
            filename = input("Filename (blank for default): ").strip()
            self.generator.export_markdown(course, filename or None)
            
        if self.db_manager:
            self.db_manager.store_course(course)
            print("Saved to database")

    # Proxy methods to generator
    def generate_course(self, topic: str, level: str) -> Dict:
        """Generate a course (delegates to GenerateCourse)"""
        return self.generator.generate_course(topic, level)
        
    def export_markdown(self, course: Dict, filename: Optional[str] = None) -> str:
        """Export course to markdown (delegates to GenerateCourse)"""
        return self.generator.export_markdown(course, filename)
        
    def load_knowledge(self):
        """Load knowledge base (delegates to GenerateCourse)"""
        return self.generator.load_knowledge()