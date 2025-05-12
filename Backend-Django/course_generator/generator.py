import requests
from bs4 import BeautifulSoup
import time
import re
import random
import logging
from urllib.parse import urljoin, urlparse, quote
from typing import List, Dict, Any, Optional
import os
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("course_generator.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CourseGenerator')

class ContentEnhancer:
    """Enhanced content generator with GPT-2 fallback"""
    def __init__(self):
        try:
            # Initialize GPT-2 model
            self.model_name = "gpt2-large"
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
            self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.has_gpt = True
            logger.info("GPT-2 model loaded successfully")
        except Exception as e:
            self.has_gpt = False
            logger.warning(f"Failed to load GPT-2 model: {str(e)}. Using simple enhancement only.")

    def enhance(self, text: str, context: str = "", max_length: int = 200) -> str:
        """Enhance text with GPT-2 if available, otherwise use simple enhancement"""
        if not text and not context:
            return ""

        # If we have GPT-2 and the text is worth enhancing
        if self.has_gpt and (len(text) > 50 or context):
            try:
                prompt = f"Explain this {context}:\n\n{text[:500]}\n\nEnhanced explanation:"

                inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )

                enhanced = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Extract just the enhanced part
                if "Enhanced explanation:" in enhanced:
                    enhanced = enhanced.split("Enhanced explanation:")[-1]
                return self._clean_text(enhanced)
            except Exception as e:
                logger.error(f"GPT-2 enhancement failed: {str(e)}")
                # Fall through to simple enhancement

        # Simple enhancement fallback
        return self._simple_enhance(text)

    def generate_content(self, topic: str, level: str = "beginner", module_type: str = "introduction") -> str:
        """Generate content from scratch using GPT-2"""
        if not self.has_gpt:
            return f"This would be a {level} level {module_type} about {topic}."

        try:
            prompt = f"Create a {level} level {module_type} about {topic} with 2-3 key points:"

            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                inputs,
                max_length=300,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )

            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return self._clean_text(generated)
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return f"Generated {level} level content about {topic}."

    def _simple_enhance(self, text: str) -> str:
        """Basic text cleaning and formatting"""
        if not text:
            return ""

        text = re.sub(r'\s+', ' ', text).strip()
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        return text

    def _clean_text(self, text: str) -> str:
        """Clean generated text"""
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove any incomplete sentences at the end
        text = re.sub(r'[^.!?]+$', '', text)
        return text

class CourseScraper:
    """Enhanced web scraper with difficulty detection"""
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Trusted educational sites
        self.trusted_sites = [
            'geeksforgeeks.org', 'w3schools.com', 'developer.mozilla.org',
            'freecodecamp.org', 'digitalocean.com', 'realpython.com',
            'tutorialspoint.com', 'javatpoint.com', 'learn.microsoft.com',
            'docs.python.org'
        ]

        # Content extraction patterns
        self.content_patterns = [
            {'tag': 'article', 'attrs': {}},
            {'tag': 'div', 'attrs': {'class': 'content'}},
            {'tag': 'main', 'attrs': {}},
            {'tag': 'div', 'attrs': {'id': 'content'}},
            {'tag': 'div', 'attrs': {'class': 'article-body'}},
            {'tag': 'div', 'attrs': {'class': 'entry-content'}},
            {'tag': 'div', 'attrs': {'class': 'post-content'}},
            {'tag': 'div', 'attrs': {'class': 'tutorial-content'}}
        ]

        # Code extraction patterns
        self.code_patterns = [
            {'tag': 'pre', 'attrs': {}},
            {'tag': 'code', 'attrs': {}},
            {'tag': 'div', 'attrs': {'class': 'highlight'}}
        ]

        # URLs to avoid
        self.avoid_patterns = [
            'practice', 'quiz', 'exercise', 'test',
            'forum', 'signup', 'login', 'profile',
            'course', 'certificate', 'pricing'
        ]

        self.visited = set()
        self.max_pages = 5
        self.delay = (1, 3)

    def search_topic(self, topic: str) -> List[str]:
        """Find relevant educational content for a topic"""
        topic = self._clean_query(topic)
        if not topic:
            return []

        # Try direct URLs first
        urls = []
        for site in self.trusted_sites:
            # The method _generate_direct_urls was called, but it was not defined.
            # Changed to call _generate_and_check_urls instead.
            urls.extend(self._generate_and_check_urls(site, topic))
            if len(urls) >= self.max_pages:
                break
            time.sleep(random.uniform(*self.delay))

        # If we didn't get enough URLs, try Google search
        if len(urls) < self.max_pages:
            google_urls = self._google_search(topic)
            urls.extend(google_urls)

        return list(dict.fromkeys(urls))[:self.max_pages]
    def _generate_and_check_urls(self, site: str, topic: str) -> List[str]:
      """Generate direct URLs for a site based on common patterns and check which ones exist"""
      topic_slug = topic.replace(' ', '-').lower()
      topic_underscore = topic.replace(' ', '_').lower()

      generated_urls = []
      valid_urls = []

      if site == 'w3schools.com':
          generated_urls = [
              f"https://www.w3schools.com/{topic_slug}/default.asp",
              f"https://www.w3schools.com/{topic_slug}_intro.asp",
              f"https://www.w3schools.com/tags/{topic_slug}.asp",
              f"https://www.w3schools.com/{topic_slug}/index.php"
          ]
      elif site == 'geeksforgeeks.org':
          generated_urls = [
              f"https://www.geeksforgeeks.org/{topic_slug}-tutorial/",
              f"https://www.geeksforgeeks.org/introduction-to-{topic_slug}/",
              f"https://www.geeksforgeeks.org/{topic_slug}-basics/"
          ]
      elif site == 'developer.mozilla.org':
          generated_urls = [
              f"https://developer.mozilla.org/en-US/docs/Web/{topic_slug}",
              f"https://developer.mozilla.org/en-US/docs/Learn/{topic_slug}"
          ]
      elif site == 'tutorialspoint.com':
          generated_urls = [
              f"https://www.tutorialspoint.com/{topic_slug}/index.htm",
              f"https://www.tutorialspoint.com/{topic_underscore}_tutorial.htm"
          ]
      elif site == 'realpython.com':
          generated_urls = [
              f"https://realpython.com/{topic_slug}/",
              f"https://realpython.com/{topic_slug}-tutorial/"
          ]
      elif site == 'javatpoint.com':
          generated_urls = [
              f"https://www.javatpoint.com/{topic_slug}-tutorial",
              f"https://www.javatpoint.com/{topic_slug}"
          ]
      else:
          # Generic patterns for other sites
          generated_urls = [
              f"https://www.{site}/{topic_slug}",
              f"https://www.{site}/{topic_slug}-tutorial",
              f"https://www.{site}/tutorial/{topic_slug}",
              f"https://www.{site}/docs/{topic_slug}"
          ]

      # Check each URL to see if it exists
      for url in generated_urls:
          try:
              response = requests.head(url, allow_redirects=True, timeout=5)
              if response.status_code == 200:
                  valid_urls.append(url)
          except requests.RequestException:
              continue

      return valid_urls

    def _google_search(self, query: str) -> List[str]:
        """Fallback to extract URLs from Google search"""
        try:
            # Format a Google search URL with site: operators for our trusted sites
            site_filters = " OR ".join([f"site:{site}" for site in self.trusted_sites])
            search_url = f"https://www.google.com/search?q={quote(query)}+{quote(site_filters)}"

            # Add a referrer to avoid being blocked
            special_headers = self.headers.copy()
            special_headers['Referer'] = 'https://www.google.com/'

            # Make the request
            response = requests.get(search_url, headers=special_headers, timeout=10)
            response.raise_for_status()

            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract URLs - Google puts them in <a> tags with href attributes
            # that start with "/url?q="
            urls = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/url?q='):
                    # Extract actual URL
                    url = href.split('/url?q=')[1].split('&')[0]
                    # Check if it's from a trusted site
                    if any(site in url for site in self.trusted_sites):
                        urls.append(url)

            return urls
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            return []

    def scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a single page with difficulty detection"""
        if any(bad in url.lower() for bad in self.avoid_patterns):
            return None

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract content
            title = self._clean_text(soup.title.string if soup.title else "Untitled")
            content = self._extract_content(soup)
            code_examples = self._extract_code(soup)

            # Determine difficulty level
            difficulty = self._determine_difficulty(content, url)

            return {
                'title': title,
                'content': content,
                'code_examples': code_examples,
                'url': url,
                'difficulty': difficulty
            }
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return None

    def _determine_difficulty(self, content: str, url: str) -> str:
        """Determine difficulty level of content"""
        text = (content + " " + url).lower()

        # Advanced indicators
        advanced_terms = ['advanced', 'expert', 'deep dive', 'optimization',
                         'algorithm', 'complexity', 'performance', 'concurrency',
                         'asynchronous', 'multithreading', 'design pattern']
        if any(term in text for term in advanced_terms):
            return "advanced"

        # Intermediate indicators
        intermediate_terms = ['intermediate', 'guide', 'tutorial', 'how to',
                             'implementation', 'function', 'method', 'class',
                             'object', 'api', 'library']
        if any(term in text for term in intermediate_terms):
            return "intermediate"

        # Default to beginner
        return "beginner"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Try each content pattern
        for pattern in self.content_patterns:
            elements = soup.find_all(pattern['tag'], pattern['attrs'] if pattern['attrs'] else {})
            if elements:
                # Take the longest content block (likely the main content)
                text = max([self._clean_text(el.get_text()) for el in elements], key=len, default="")
                if len(text) > 100:  # Ensure we have substantial content
                    return text

        return ""

    def _extract_code(self, soup: BeautifulSoup) -> List[str]:
        """Extract code examples from page"""
        examples = []
        for pattern in self.code_patterns:
            for element in soup.find_all(pattern['tag'], pattern['attrs'] if pattern['attrs'] else {}):
                code = self._clean_code(element.get_text())
                if code and len(code) > 10:  # Ensure it's not just a tiny code snippet
                    examples.append(code)
        return examples

    def _clean_query(self, text: str) -> str:
        """Clean search query"""
        return re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower()

    def _clean_text(self, text: str) -> str:
        """Clean extracted text content"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'Advertisement\s*', '', text, flags=re.IGNORECASE)
        return text.strip()

    def _clean_code(self, code: str) -> str:
        """Clean code examples"""
        if not code:
            return ""
        return re.sub(r'\s+\n', '\n', code).strip()

class CourseGenerator:
    """Enhanced course generator with difficulty levels and GPT fallback"""
    def __init__(self):
        self.scraper = CourseScraper()
        self.enhancer = ContentEnhancer()

    def generate_course(self, topic: str, target_level: str = "all") -> dict:
        """Generate a course with optional difficulty filtering"""
        logger.info(f"Generating {target_level} course for: {topic}")

        # Find and scrape relevant pages
        urls = self.scraper.search_topic(topic)
        if not urls:
            return self._generate_fallback_course(topic)

        pages = []
        for url in urls:
            content = self.scraper.scrape_page(url)
            if content:
                pages.append(content)
            time.sleep(random.uniform(*self.scraper.delay))

        if not pages:
            return self._generate_fallback_course(topic)

        # Filter by difficulty if requested
        if target_level.lower() != "all":
            pages = [p for p in pages if p['difficulty'].lower() == target_level.lower()]
            if not pages:
                return {
                    "error": f"No {target_level} content found for '{topic}'",
                    "suggestion": "Try generating a course for all levels"
                }

        # Structure the course
        course_level = self._determine_course_level(pages)
        modules = self._create_modules(pages, topic, course_level)

        # Ensure we have at least 3 modules
        if len(modules) < 3:
            modules = self._fill_missing_modules(modules, topic, course_level)

        return {
            "title": f"{topic.title()} Course",
            "level": course_level,
            "modules": modules,
            "resources": [p['url'] for p in pages if 'url' in p],
            "generated_date": time.strftime("%Y-%m-%d")
        }

    def _generate_fallback_course(self, topic: str) -> dict:
        """Generate a course using GPT when scraping fails"""
        logger.warning(f"Generating fallback course for: {topic}")

        # Create basic modules with GPT-generated content
        modules = []
        module_types = ["introduction", "core concepts", "advanced topics"]

        for i, module_type in enumerate(module_types):
            content = self.enhancer.generate_content(topic, "beginner", module_type)
            modules.append({
                "title": f"Module {i+1}: {module_type.title()}",
                "content": content,
                "examples": [],
                "difficulty": "beginner",
                "generated": True  # Mark as GPT-generated
            })

        return {
            "title": f"{topic.title()} Course (Generated)",
            "level": "beginner",
            "modules": modules,
            "resources": [],
            "generated_date": time.strftime("%Y-%m-%d"),
            "warning": "This course was generated automatically as no relevant content was found"
        }

    def _fill_missing_modules(self, existing_modules: List[dict], topic: str, level: str) -> List[dict]:
        """Fill in missing modules with GPT-generated content"""
        target_count = 3  # We want at least 3 modules
        if len(existing_modules) >= target_count:
            return existing_modules

        # Determine what types of modules we need
        module_types = ["introduction", "core concepts", "advanced topics"]
        existing_types = [m['title'].lower() for m in existing_modules]

        new_modules = existing_modules.copy()

        for i in range(target_count - len(existing_modules)):
            # Find a module type we don't have yet
            for module_type in module_types:
                if module_type not in existing_types:
                    content = self.enhancer.generate_content(topic, level, module_type)
                    new_modules.append({
                        "title": f"Module {len(new_modules)+1}: {module_type.title()}",
                        "content": content,
                        "examples": [],
                        "difficulty": level,
                        "generated": True
                    })
                    existing_types.append(module_type)
                    break

        return new_modules

    def _determine_course_level(self, pages: List[dict]) -> str:
        """Determine overall course level based on module levels"""
        levels = [p['difficulty'] for p in pages]
        if "advanced" in levels:
            return "advanced"
        if "intermediate" in levels:
            return "intermediate"
        return "beginner"

    def _create_modules(self, pages: List[dict], topic: str, course_level: str) -> List[dict]:
        """Organize content into modules with enhanced explanations"""
        modules = []

        # Sort pages by difficulty (beginners first)
        pages.sort(key=lambda p: ["beginner", "intermediate", "advanced"].index(p['difficulty']))

        for i, page in enumerate(pages):
            # Enhance content with context
            enhanced_content = self.enhancer.enhance(
                page['content'],
                f"{topic} {page['title']} at {page['difficulty']} level"
            )

            module = {
                "title": f"Module {i+1}: {page['title']}",
                "content": enhanced_content,
                "examples": [],
                "difficulty": page['difficulty'],
                "source": page['url']
            }

            # Add code examples with explanations
            for j, code in enumerate(page['code_examples'][:2]):
                module["examples"].append({
                    "title": f"Example {j+1} from {page['title']}",
                    "code": code,
                    "explanation": self.enhancer.enhance(
                        "",
                        f"explanation of this {topic} code example: {code[:100]}..."
                    )
                })

            modules.append(module)

        return modules

    def interactive_mode(self):
        """Enhanced interactive interface with difficulty selection"""
        print("\n=== Enhanced Course Generator ===")
        while True:
            topic = input("\nEnter a programming topic (or 'quit'): ").strip()
            if topic.lower() == 'quit':
                break

            if not topic:
                print("Please enter a valid topic")
                continue

            print("\nSelect difficulty level:")
            print("1. Beginner")
            print("2. Intermediate")
            print("3. Advanced")
            print("4. All Levels")
            level_choice = input("Enter choice (1-4): ").strip()

            levels = {
                "1": "beginner",
                "2": "intermediate",
                "3": "advanced",
                "4": "all"
            }
            target_level = levels.get(level_choice, "all")

            course = self.generate_course(topic, target_level)
            self._display_course(course)

    def _display_course(self, course: dict):
        """Display course information and handle saving"""
        if "error" in course:
            print(f"\nError: {course['error']}")
            if "suggestion" in course:
                print(f"Suggestion: {course['suggestion']}")
            return

        print(f"\nGenerated Course: {course['title']}")
        print(f"Level: {course['level'].title()}")
        print(f"Modules: {len(course['modules'])}")
        print(f"Date: {course['generated_date']}")

        if "warning" in course:
            print(f"\nWarning: {course['warning']}")

        # Show module previews
        for i, module in enumerate(course['modules']):
            print(f"\nModule {i+1}: {module['title']}")
            print(f"Difficulty: {module['difficulty'].title()}")
            if module.get('generated'):
                print("[AI-Generated Content]")
            preview = module['content'][:100] + "..." if len(module['content']) > 100 else module['content']
            print(f"Preview: {preview}")
            print(f"Examples: {len(module['examples'])}")

        # Show resources if available
        if course['resources']:
            print("\nResources:")
            for url in course['resources']:
                print(f"- {url}")

        # Save option
        save = input("\nSave to file? (y/n): ").lower()
        if save == 'y':
            self._save_course(course)

    def _save_course(self, course: dict):
        """Save course to markdown file"""
        filename = f"{course['title'].replace(' ', '_').lower()}_course.md"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {course['title']}\n\n")
                f.write(f"**Level:** {course['level'].title()}\n")
                f.write(f"**Generated:** {course['generated_date']}\n\n")

                if "warning" in course:
                    f.write(f"> Note: {course['warning']}\n\n")

                f.write("## Course Overview\n\n")
                f.write(f"This course covers {course['title'].split(' Course')[0]} at {course['level']} level.\n\n")

                for module in course['modules']:
                    f.write(f"## {module['title']}\n\n")
                    if module.get('generated'):
                        f.write("> This content was generated automatically\n\n")
                    f.write(f"**Difficulty:** {module['difficulty'].title()}\n\n")
                    f.write(f"{module['content']}\n\n")

                    if module['examples']:
                        f.write("### Code Examples\n\n")
                        for example in module['examples']:
                            f.write(f"#### {example['title']}\n\n")
                            f.write(f"```\n{example['code']}\n```\n\n")
                            f.write(f"{example['explanation']}\n\n")

                if course['resources']:
                    f.write("## Resources\n\n")
                    for url in course['resources']:
                        f.write(f"- [{urlparse(url).netloc}]({url})\n")

            print(f"Course saved to {filename}")
        except Exception as e:
            print(f"Failed to save course: {str(e)}")

if __name__ == "__main__":
    generator = CourseGenerator()
    generator.interactive_mode()