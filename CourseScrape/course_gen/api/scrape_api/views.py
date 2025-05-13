from course_gen.core.globals import (logging, asyncio, os, traceback, json)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from course_gen.core import ScrapedContent
from .serializer import WebSearchRequestSerializer
from course_gen.services.course_generator import CourseGenerator
from course_gen.services.database_manager import DatabaseManager
from course_gen.services.knowledge_scraper import PlaywrightScraper, URLManager, ContentCleaner, ContentExtractor, BaseDetector, BaseScraper


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

knowledge = []
search_results = []  # Store temporary search results

class ScrapedContentView(APIView):
    def get(self, request, format=None):
        """Return all scraped content."""
        scraped_content = ScrapedContent.objects.all()
        serializer = WebSearchRequestSerializer(scraped_content, many=True)
        return Response(serializer.data)

    async def post(self, request):
        serializer = WebSearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        query = data["query"].strip()
        max_results = data.get("max_results", 5)
        save_to_db = data.get("save_to_db", False)

        if not query:
            return Response({"detail": "Query cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Perform the search
            if hasattr(scraper, "search_and_scrape_async"):
                search_results = await scraper.search_and_scrape_async(query, max_results)
            else:
                search_results = scraper.search_and_scrape(query, max_results)

            if not search_results:
                return Response({"message": "No quality content found."}, status=200)

            # Extend in-memory knowledge base
            knowledge.extend(search_results)
            generator.load_knowledge()

            # Save to file
            file_path = "knowledge_base.json"
            existing_knowledge = []

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        existing_knowledge = json.load(f)
                    except json.JSONDecodeError:
                        existing_knowledge = []

            all_knowledge = existing_knowledge + search_results
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(all_knowledge, f, ensure_ascii=False, indent=4)

            # Optional DB storage
            if save_to_db and db_manager:
                db_manager.store_knowledge(search_results)

            return Response({
                "message": f"Found {len(search_results)} results.",
                "results": search_results,
                "saved_to_file": file_path,
                "saved_to_db": save_to_db
            })

        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            traceback.print_exc()
            return Response({"detail": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
