from course_gen.core.globals import (logging, APIView, Response, status, async_to_sync)

from .serializer import WebScrapeRequestSerializer
from course_gen.services.course_generator import CourseGenerator
from course_gen.services.database_manager import DatabaseManager
from course_gen.services.knowledge_scraper import PlaywrightScraper, URLManager, ContentCleaner, ContentExtractor, BaseDetector, BaseScraper
from course_gen.utils.file_manager import FileManager

logger = logging.getLogger(__name__)


generator = CourseGenerator()
db_manager = DatabaseManager()
url_manager = URLManager(scraped_urls_file="scraped_urls.json", bad_urls_file="bad_urls.json")
content_cleaner = ContentCleaner()
extractor = ContentExtractor(content_cleaner)
detector = BaseDetector()
scraper = PlaywrightScraper(
            url_manager=url_manager,
            content_cleaner=content_cleaner,
            extractor=extractor,
            detector=detector
        )

new_knowledge = []
search_results = []  # Store temporary search results

class ScrapedContentView(APIView):
    def post(self, request):
        serializer = WebScrapeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        query = data["query"].strip()
        level = data.get("level", "beginner")
        max_results = data.get("max_results", 5)
        save_to_db = data.get("save_to_db", False)

        if not query:
            return Response({"detail": "Query cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Fetch and scrape data
            search_results = async_to_sync(scraper.search_and_scrape_async)(query, level, max_results)

            # 2. Save using FileManager (handles merging/error logging)
            FileManager.save_to_knowledge_base(search_results)

            # 3. Optional DB save
            if save_to_db and hasattr(self, 'db_manager'):
                db_manager.store_knowledge(search_results)

            return Response({
                "message": f"Found {len(search_results)} results.",
                "results": search_results,
                "saved_to_file": "knowledge_base.json",
                "saved_to_db": save_to_db
            })

        except Exception as e:
            logger.error(f"Web search failed: {str(e)}", exc_info=True)
            return Response({"detail": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)