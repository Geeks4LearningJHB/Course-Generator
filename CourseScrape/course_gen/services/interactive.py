from course_gen.core.globals import (
    List, Dict, logger, Optional, asyncio, json, os, traceback
)

from .course_generator import CourseGenerator
from .database_manager import DatabaseManager
from .knowledge_scraper import StandardScraper, PlaywrightScraper, URLManager, ContentCleaner, ContentExtractor, BaseDetector, BaseScraper


class CourseBuilderInterface:
    """
    Interactive interface for AI Course Builder with these enhanced features:
    - Course generation from scraped knowledge
    - Web search integration with Playwright for JavaScript-heavy sites
    - Interactive menu system
    - Database integration (optional)
    - Markdown export
    """
    url_manager = URLManager(scraped_urls_file="scraped_urls.json", bad_urls_file="bad_urls.json")
    content_cleaner = ContentCleaner()
    extractor = ContentExtractor(content_cleaner)
    detector = BaseDetector()
    
    def __init__(self, db_manager=None):
        """
        Initialize with optional database manager
        
        Args:
            db_manager: Database manager instance (optional)
        """
        self.generator = CourseGenerator()
        self.scraper_async = PlaywrightScraper(
            url_manager=self.url_manager,
            content_cleaner=self.content_cleaner,
            extractor=self.extractor,
            detector=self.detector
        )
        self.scraper_sync = StandardScraper(
            url_manager=self.url_manager,
            content_cleaner=self.content_cleaner,
            extractor=self.extractor,
            detector=self.detector
        )
        self.db_manager = DatabaseManager()
        self._current_page = 0  # For pagination
        self._search_results = []  # Store temporary search results
        
    @property
    def knowledge(self) -> List[Dict]:
        """Access the current knowledge base"""
        return self.generator.knowledge
        
    @knowledge.setter
    def knowledge(self, value: List[Dict]):
        """Update the knowledge base"""
        self.generator.knowledge = value
        
    def interactive_mode(self):
        print("\n" + "="*60)
        print("AI COURSE BUILDER".center(60))
        print("="*60)
        
        while True:
            self._display_main_menu()
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                self._handle_course_creation()
            elif choice == "2":
                self._update_knowledge_base()
            elif choice == "3":
                self._search_web_for_knowledge()
            elif choice == "4":
                self._list_topics()
            elif choice == "5":
                self._browse_courses()
            elif choice == "6":
                self._search_courses()
            elif choice == "7":
                print("\nThank you for using AI Course Generator!")
                break
            else:
                print("\nInvalid choice. Please try again.")

    # Menu Handlers
    def _display_main_menu(self):
        """Display the enhanced main menu options"""
        print("\n" + "-"*60)
        print("MAIN MENU".center(60))
        print("-"*60)
        print("1. Create New Course")
        print("2. Update Knowledge Base (Configured Sources)")
        print("3. Search Web for Additional Knowledge")
        print("4. List Available Topics")
        print("5. Browse Saved Courses")
        print("6. Search Courses")
        print("7. Exit")
        print("-"*60)

    async def _search_web_for_knowledge_async(self):
        """Async version of web search with Playwright support"""
        print("\nSearch Web for Knowledge")
        print("------------------------")
        
        query = input("Enter search query: ").strip()
        if not query:
            print("No query entered. Returning to main menu.")
            return
            
        try:
            max_results = int(input("Max results to fetch (default 5): ") or 5)
            if max_results <= 0:
                max_results = 5
        except ValueError:
            max_results = 5
            
        print(f"\nSearching for '{query}'...")
        print("This might take a few minutes. Please be patient.")
        
        try:
            # Determine which scraper to use
            if isinstance(self.scraper_async, PlaywrightScraper):
                # Use async method directly
                self._search_results = await self.scraper_async.search_and_scrape_async(query, max_results)
            else:
                # Use sync method for StandardScraper
                self._search_results = self.scraper_async.search_and_scrape(query, max_results)
            
            if not self._search_results:
                print("No quality content found (many sites have paywalls or restrictive robots.txt)")
                return
                
            print(f"\nFound {len(self._search_results)} good resources:")
            for i, item in enumerate(self._search_results, 1):
                print(f"{i}. {item['title']} ({item['source']})")
                
            # Always extend knowledge and save to file
            self.knowledge.extend(self._search_results)
            self.generator.load_knowledge()
            print(f"Added {len(self._search_results)} items to in-memory knowledge base.")
                    
            # Save to JSON file
            file_path = "knowledge_base.json"
            existing_knowledge = []
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        existing_knowledge = json.load(f)
                    except json.JSONDecodeError:
                        existing_knowledge = []

            all_knowledge = existing_knowledge + self._search_results
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(all_knowledge, f, ensure_ascii=False, indent=4)
            print(f"Saved to '{file_path}'.")

            # Optional DB save
            if self.db_manager and input("Also save to database? [y/N]: ").lower() == 'y':
                self.db_manager.store_knowledge(self._search_results)
                print("Saved to database.")
                
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            print(f"\nFailed to search web: {str(e)}")
            traceback.print_exc()  # Print full traceback for debugging
    
    def _search_web_for_knowledge(self):
        """Sync wrapper for async web search"""
        asyncio.run(self._search_web_for_knowledge_async())

    async def _handle_course_creation_async(self):
        """Async version of course creation with web search"""
        print("\nCreate New Course")
        print("-----------------")
        
        topic = input("Enter a topic: ").strip().lower()
        if not topic:
            print("No topic entered. Returning to main menu.")
            return
            
        level = input("Enter level (beginner/intermediate/advanced): ").strip().lower()
        level = level if level in ["beginner", "intermediate", "advanced"] else "beginner"
        
        # Offer to search web for additional knowledge
        if input("\nSearch web for additional content on this topic? [y/N]: ").lower() == 'y':
            try:
                search_results = await self.scraper_async.search_and_scrape_async(f"{topic} {level} course")
                if search_results:
                    print(f"\nFound {len(search_results)} additional resources:")
                    for i, item in enumerate(search_results, 1):
                        print(f"{i}. {item['title']} ({item['source']})")
                        
                    if input("\nAdd to knowledge base? [y/N]: ").lower() == 'y':
                        self.knowledge.extend(search_results)
                        self.generator.load_knowledge()
            except Exception as e:
                logger.error(f"Web search during course creation failed: {str(e)}")
                print("Web search failed, continuing with existing knowledge...")
        
        print(f"\nGenerating {level} course for '{topic}'...")
        course = self.generator.generate_course(topic, level)
        
        if "error" in course:
            print(f"Error: {course['error']}")
            return
            
        print("\nCourse created successfully!")
        print(f"Title: {course['title']}")
        print(f"Modules: {len(course['modules'])}")
        
        self._handle_course_save(course)
    
    def _handle_course_creation(self):
        """Sync wrapper for async course creation"""
        asyncio.run(self._handle_course_creation_async())

    def _update_knowledge_base(self):
        """Update the knowledge base by scraping"""
        print("\nUpdating knowledge base...")
        try:
            self.knowledge = self.scraper_sync.scrape_configured_sources()
            self.generator.load_knowledge()
            
            # Always extend knowledge and save to file
            self.knowledge.extend(self._search_results)
            self.generator.load_knowledge()
            print(f"Added {len(self._search_results)} items to in-memory knowledge base.")
                    
            # Save to JSON file
            file_path = "knowledge_base.json"
            existing_knowledge = []
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        existing_knowledge = json.load(f)
                    except json.JSONDecodeError:
                        existing_knowledge = []

            all_knowledge = existing_knowledge + self._search_results
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(all_knowledge, f, ensure_ascii=False, indent=4)
            print(f"Saved to '{file_path}'.")
            
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