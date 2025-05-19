import json
from datetime import datetime
from .content_scraper import ContentScraper
from .LLM import LLMService
from course_gen.services.mongo_client import MongoDBClient
#from CourseScrape.config import settings  # Import settings from the appropriate module

class CourseGenerator:
    def __init__(self):
        self.scraper = ContentScraper()
        self.llm = LLMService()
        self.mongo = MongoDBClient().get_collection()
     #   self.gpt_model = "gpt-4-turbo" if settings.LLM_PROVIDER == "openai" else None
    
    async def generate_course(self, prompt_data):
        scraped_content = await self.scraper.scrape_topic(prompt_data['courseTitle'])
        prompt = self._build_prompt(prompt_data, scraped_content)
        
        # Use LLM service instead of direct OpenAI call
        llm_response = await self.llm.generate(prompt)
        course_content = json.loads(llm_response)
        
        course = self._structure_course(prompt_data, course_content, scraped_content)
        self._save_to_mongodb(course)
        return course
    
    def _build_prompt(self, prompt_data, scraped_content):
        base_prompt = f"""
        Generate a comprehensive {prompt_data['difficulty']} level course on {prompt_data['courseTitle']} 
        with a duration of {prompt_data['duration']} months. The course should include:
        
        1. Detailed learning objectives
        2. 8-12 modules with clear outcomes
        3. 3-5 units per module with content
        4. Practical activities and assessments
        
        Use the following verified sources as references:
        {self._format_scraped_content(scraped_content)}
        
        Return the response as a JSON object with this structure:
        {{
            "courseTitle": "...",
            "overview": "...",
            "objectives": ["..."],
            "modules": [
                {{
                    "title": "...",
                    "outcomes": ["..."],
                    "units": [
                        {{
                            "title": "...",
                            "content": "...",
                            "activities": ["..."]
                        }}
                    ],
                    "assessment": "..."
                }}
            ],
            "references": [
                {{
                    "url": "...",
                    "snippet": "..."
                }}
            ]
        }}
        """
        return base_prompt
    
    def _structure_course(self, prompt_data, gpt_content, scraped_content):
         return {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "source_prompt": prompt_data,
                "model_used": self.gpt_model
            },
            "course": gpt_content,
            "source_materials": scraped_content
        }
    
    def _save_to_mongodb(self, course_data):          
        try:
            result = self.mongo.insert_one(course_data)
            course_data['_id'] = str(result.inserted_id)
            return course_data
        except Exception as e:
            raise Exception(f"MongoDB insertion failed: {str(e)}")