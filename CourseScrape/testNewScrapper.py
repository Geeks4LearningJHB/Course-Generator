import asyncio
import re
import time
import random
import logging
import os
import sys
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("edu_scraper")

class URLManager:
    """Manages URL processing, storage and retrieval"""
    def __init__(self):
        self.scraped_urls: Set[str] = set()
        self.bad_urls: Set[str] = set()
        
        # Configure trusted domains and their delay configurations
        self.trusted_domains = {
            "w3schools.com": (2, 5),
            "geeksforgeeks.org": (2, 5),
            "realpython.com": (2, 5),
            "developer.mozilla.org": (2, 5),
            "docs.python.org": (2, 5),
            "freecodecamp.org": (2, 5),
            "python.org": (2, 5),
            "learnpython.org": (2, 5),
            "programiz.com": (2, 5),
            "tutorialspoint.com": (2, 5)
        }
        
        # Default delay for other sites
        self.default_delay = (5, 10)
        
        # Domains to avoid completely
        self.avoid_domains = [
            "pinterest", "facebook.com", "twitter.com", "instagram.com",
            "youtube.com", "medium.com", "quora.com", "linkedin.com",
            "reddit.com", "courses.com", "udemy.com", "coursera.org"
        ]
        
        self.skip_patterns = [
            "/watch", "/signin", "/login", "/video", "/account", "/register",
            "/premium", "/subscribe", "/donate", "/advertise"
        ]
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL safely"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return ""
    
    def is_trusted_domain(self, url: str) -> bool:
        """Check if URL belongs to a trusted domain"""
        domain = self.extract_domain(url)
        return any(trusted in domain for trusted in self.trusted_domains.keys())
    
    def should_avoid_domain(self, url: str) -> bool:
        """Check if URL belongs to a domain that should be avoided"""
        domain = self.extract_domain(url)
        return any(avoid in domain for avoid in self.avoid_domains)
    
    def should_skip_url(self, url: str) -> bool:
        """Check if URL should be skipped based on patterns"""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.skip_patterns)
    
    def get_delay_for_domain(self, url: str) -> Tuple[float, float]:
        """Get appropriate delay range for a domain"""
        domain = self.extract_domain(url)
        for trusted, delay in self.trusted_domains.items():
            if trusted in domain:
                return delay
        return self.default_delay

class ContentCleaner:
    """Handles cleaning and normalization of scraped content"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content with enhanced ad/cookie removal"""
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Enhanced removal patterns for ads, cookies, and legal notices
        remove_patterns = [
            r'accept\s*(all)?\s*cookies?', 
            r'we\s*use\s*cookies?',
            r'cookie\s*(policy|notice|banner|consent|preferences)',
            r'privacy\s*(policy|notice|statement)',
            r'terms\s*(of\s*service|and\s*conditions)',
            r'advertisement|sponsored\s*content',
            r'(sign\s*up|subscribe)\s*(for\s*free)?\s*(newsletter|updates)',
            r'continue\s*(reading|with)\s*(a\s*subscription|free\s*trial)',
            r'this\s*content\s*is\s*(protected|locked)',
            r'read\s*more\s*(with|by)\s*(subscription|membership)'
        ]
        
        for pattern in remove_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text

    @staticmethod
    def clean_code(code: str) -> str:
        """Clean and format code examples"""
        if not code:
            return ""
            
        # Remove shell prompts and line numbers
        code = re.sub(r'^\s*[\$>]\s*|\s*\d+\s*\|?', '', code, flags=re.MULTILINE)
        # Remove trailing whitespace and normalize line endings
        code = re.sub(r'\s+\n', '\n', code)
        return code.strip()

class ContentExtractor:
    """Handles extraction of content from HTML"""
    
    def __init__(self, cleaner: ContentCleaner):
        self.cleaner = cleaner
        self.code_selectors = ['pre', 'code', '.code-block', '.highlight']
        self.content_selectors = [
            "main article", "article", "#content", ".content", 
            "#main-content", ".main-content", ".tutorial-content",
            ".chapter", ".lesson", ".course-content", ".docs-content"
        ]
        self.remove_selectors = [
            ".ad", ".ad-container", ".cookie-banner", ".newsletter",
            ".popup", ".modal", ".overlay", "aside", ".sidebar",
            ".related-posts", ".comments", "footer", "header nav"
        ]
        self.structure_patterns = {
            "section": r"chapter|section|unit|part|module",
            "subsection": r"lesson|topic|step|example|exercise",
            "title": r"h[1-6]"
        }

    def _clean_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove non-content elements from the soup"""
        clean_soup = copy.copy(soup)
        
        # Remove unwanted elements by selectors
        for selector in self.remove_selectors:
            for element in clean_soup.select(selector):
                element.decompose()
        
        return clean_soup

    def extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract clean main content with enhanced filtering"""
        try:
            clean_soup = self._clean_content(soup)
            
            # Try all content selectors
            for selector in self.content_selectors:
                main_content = clean_soup.select_one(selector)
                if main_content and len(main_content.get_text(strip=True)) > 120:
                    return main_content
                    
            return None
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return None

    def extract_code_examples(self, soup: BeautifulSoup) -> List[str]:
        """Extract code examples from a page"""
        code_examples = []
        
        try:
            for selector in self.code_selectors:
                for code_block in soup.select(selector):
                    code = self.cleaner.clean_code(code_block.get_text(strip=True))
                    if code:
                        code_examples.append(code)
        except Exception as e:
            logger.error(f"Error extracting code examples: {e}")
            
        return code_examples

    def extract_structured_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract and structure educational content"""
        result = {
            "url": url,
            "title": self.get_title(soup),
            "sections": [],
            "code_examples": [],
            "summary": "",
            "metadata": {}
        }
        
        main_content = self.extract_main_content(soup)
        if not main_content:
            return result
            
        # Extract sections and structure
        sections = []
        current_section = None
        
        headings = main_content.find_all(re.compile(self.structure_patterns["title"]))
        for heading in headings:
            heading_text = heading.get_text().strip()
            
            if re.search(self.structure_patterns["section"], heading_text, re.I):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "title": heading_text,
                    "subsections": [],
                    "content": ""
                }
            elif re.search(self.structure_patterns["subsection"], heading_text, re.I):
                if current_section:
                    current_section["subsections"].append({
                        "title": heading_text,
                        "content": self.get_related_content(heading)
                    })
            
            if current_section:
                current_section["content"] += f"\n{heading_text}\n{self.get_related_content(heading)}"
        
        if current_section:
            sections.append(current_section)
            
        result["sections"] = sections
        result["code_examples"] = self.extract_code_examples(soup)
        
        # Extract summary (first few paragraphs)
        paragraphs = main_content.find_all('p')[:3]
        result["summary"] = " ".join(p.get_text().strip() for p in paragraphs)
        
        return result

    def get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title with fallbacks"""
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            return re.sub(r'\s*[-|:]\s*.+$', '', title_text)
        return "Untitled"

    def get_related_content(self, element) -> str:
        """Get content related to a heading"""
        content = []
        next_node = element.next_sibling
        
        while next_node:
            if next_node.name and re.match(self.structure_patterns["title"], next_node.name):
                break
                
            if next_node.name in ['p', 'ul', 'ol', 'div']:
                text = next_node.get_text().strip()
                if text:
                    content.append(text)
                    
            next_node = next_node.next_sibling
            
        return "\n".join(content)

class EduScraper:
    def __init__(self):
        self.url_manager = URLManager()
        self.cleaner = ContentCleaner()
        self.extractor = ContentExtractor(self.cleaner)
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Windows fixes for python3.11+ and playwright 
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            os.environ['PLAYWRIGHT_DISABLE_ISOLATED_HEAP'] = '1'
            os.environ['PLAYWRIGHT_NO_PROXY'] = '1'

    async def handle_cookie_popups(self, page):
        """Attempt to handle cookie consent popups"""
        cookie_selectors = [
            "#cookie-consent", ".cookie-banner", "#accept-cookies",
            "#cookie-notice", ".gdpr-banner", "#consent-banner",
            "button:has-text('Accept')", "button:has-text('Agree')"
        ]
        
        for selector in cookie_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    await page.wait_for_timeout(1000)
                    return True
            except Exception:
                continue
        return False

    async def scrape_page(self, url: str, depth: int = 0, max_depth: int = 2) -> Optional[Dict]:
        """Scrape a single educational page with structured content"""
        if depth > max_depth:
            return None
            
        if self.url_manager.should_skip_url(url):
            return None
            
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.headers["User-Agent"],
                    viewport={"width": 1280, "height": 800},
                    ignore_https_errors=True
                )
                
                # Stealth settings
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.navigator.chrome = { runtime: {} };
                """)
                
                page = await context.new_page()
                await page.set_extra_http_headers(self.headers)
                
                try:
                    # Navigate with timeout and retry logic
                    for attempt in range(3):
                        try:
                            response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                            if response and response.status >= 400:
                                raise Exception(f"HTTP Error {response.status}")
                            break
                        except Exception as e:
                            if attempt == 2:
                                raise
                            await page.wait_for_timeout(2000 * (attempt + 1))
                            continue
                    
                    await page.wait_for_timeout(3000)
                    await self.handle_cookie_popups(page)
                    
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    course_data = self.extractor.extract_structured_content(soup, url)
                    
                    # Try to follow next page link if not at max depth
                    if depth < max_depth:
                        next_url = self.find_next_link(soup, url)
                        if next_url:
                            next_page_data = await self.scrape_page(next_url, depth + 1, max_depth)
                            if next_page_data:
                                course_data['sections'].extend(next_page_data.get('sections', []))
                                course_data['code_examples'].extend(next_page_data.get('code_examples', []))
                    
                    await browser.close()
                    return course_data
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    try:
                        await browser.close()
                    except:
                        pass
                    return None
                    
        except Exception as e:
            logger.error(f"Playwright error: {str(e)}")
            return None

    def find_next_link(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Find and return the URL of the next page if exists"""
        next_selectors = [
            "a:contains('Next')", "a:contains('Continue')", 
            ".next a", "a[rel='next']"
        ]
        
        for selector in next_selectors:
            try:
                next_link = soup.select_one(selector)
                if next_link and next_link.get("href"):
                    next_url = next_link["href"]
                    if not next_url.startswith(('http://', 'https://')):
                        next_url = urljoin(base_url, next_url)
                    return next_url
            except Exception:
                continue
        return None

    async def search_educational_content(self, topic: str, level: str = "beginner") -> List[Dict]:
        """Search for educational content on a topic"""
        demo_urls = {
            "python": [
                "https://www.w3schools.com/python/",
                "https://realpython.com/python-beginner-tips/",
                "https://docs.python.org/3/tutorial/",
                "https://www.learnpython.org/"
            ],
            "javascript": [
                "https://www.w3schools.com/js/",
                "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
                "https://javascript.info/"
            ]
        }
        
        urls = demo_urls.get(topic.lower(), [
            f"https://www.w3schools.com/{topic}/",
            f"https://www.geeksforgeeks.org/{topic}-tutorial/",
            f"https://realpython.com/tutorials/{topic}/"
        ])
        
        course_materials = []
        for url in urls[:5]:  # Limit to 5 URLs
            logger.info(f"Scraping {url}")
            material = await self.scrape_page(url)
            if material:
                course_materials.append(material)
            await asyncio.sleep(random.uniform(2, 5))
            
        return course_materials

    def organize_course(self, materials: List[Dict]) -> Dict:
        """Organize scraped materials into a structured course"""
        if not materials:
            return {}
            
        first_title = materials[0].get('title', '').split('|')[0].split('-')[0].strip()
        course_title = f"Comprehensive {first_title} Course" if first_title else "Generated Course"
        
        course = {
            "title": course_title,
            "description": "A complete course compiled from trusted educational sources",
            "modules": [],
            "resources": [],
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "sources": [m.get('url', '') for m in materials]
            }
        }
        
        for material in materials:
            if material.get('sections'):
                for section in material['sections']:
                    module = {
                        "title": section['title'],
                        "lessons": []
                    }
                    
                    if section.get('subsections'):
                        for sub in section['subsections']:
                            module['lessons'].append({
                                "title": sub['title'],
                                "content": sub['content']
                            })
                    else:
                        module['lessons'].append({
                            "title": section['title'],
                            "content": section['content']
                        })
                    
                    course['modules'].append(module)
            
            if material.get('code_examples'):
                course['resources'].append({
                    "type": "code_examples",
                    "content": material['code_examples']
                })
            if material.get('url'):
                course['resources'].append({
                    "type": "source",
                    "url": material['url'],
                    "title": material.get('title', 'Source Material')
                })
        
        return course

def generate_markdown(course: Dict) -> str:
    """Generate well-formatted markdown content from course structure"""
    if not course:
        return "# No Course Content Available\n"
    
    md_content = []
    md_content.append(f"# {course.get('title', 'Generated Course')}\n")
    md_content.append(f"{course.get('description', '')}\n")
    
    md_content.append("\n## ℹ️ Course Information\n")
    md_content.append(f"- **Generated on**: {course.get('metadata', {}).get('generated_at', 'Unknown')}")
    md_content.append("- **Sources**:")
    for source in course.get('metadata', {}).get('sources', []):
        md_content.append(f"  - {source}")
    
    md_content.append("\n## 📚 Resources\n")
    for resource in course.get('resources', []):
        if resource['type'] == 'source':
            md_content.append(f"- [{resource.get('title', 'Source')}]({resource['url']})")
        elif resource['type'] == 'code_examples' and resource['content']:
            md_content.append("\n### Code Examples\n")
            for i, example in enumerate(resource['content'][:5], 1):
                md_content.append(f"#### Example {i}\n```\n{example}\n```\n")
    
    md_content.append("\n## 📖 Course Modules\n")
    for i, module in enumerate(course.get('modules', []), 1):
        md_content.append(f"### Module {i}: {module['title']}\n")
        
        for lesson in module.get('lessons', []):
            md_content.append(f"#### {lesson['title']}\n")
            md_content.append(f"{lesson['content']}\n\n")
    
    return "\n".join(md_content)

def save_markdown_file(content: str, default_name: str = "generated_course") -> str:
    """Save markdown content to file with user interaction"""
    while True:
        filename = input(f"Enter filename to save course [{default_name}.md]: ") or default_name
        if not filename.endswith('.md'):
            filename += '.md'
        
        try:
            os.makedirs("output", exist_ok=True)
            full_path = os.path.join("output", filename)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ Course saved to: {os.path.abspath(full_path)}")
            return full_path
        except Exception as e:
            print(f"❌ Error saving file: {e}. Please try a different filename.")

async def create_course(topic: str, level: str = "beginner") -> Optional[str]:
    """Main function to create and save a course"""
    try:
        scraper = EduScraper()
        
        print(f"\n🔍 Searching for {level} {topic} content...")
        materials = await scraper.search_educational_content(topic, level)
        
        if not materials:
            print("❌ No suitable educational content found.")
            return None
        
        print(f"\n📚 Found content from {len(materials)} sources. Organizing...")
        course = scraper.organize_course(materials)
        
        if not course.get('modules'):
            print("❌ No valid course modules could be created.")
            return None
        
        print("\n✅ Course Created Successfully!")
        print(f"📛 Title: {course['title']}")
        print(f"📦 Modules: {len(course['modules'])}")
        print(f"🔗 Resources: {len(course['resources'])}")
        
        markdown_content = generate_markdown(course)
        saved_path = save_markdown_file(markdown_content, f"{topic}_{level}_course")
        
        return saved_path
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        print(f"❌ An error occurred while creating the course: {e}")
        return None

async def main():
    """Handle command line arguments and user input"""
    try:
        if len(sys.argv) > 1:
            topic = sys.argv[1]
            level = sys.argv[2] if len(sys.argv) > 2 else "beginner"
        else:
            topic = input("Enter course topic (e.g., python, javascript): ").strip()
            if not topic:
                print("❌ Topic cannot be empty")
                return
                
            level = input("Enter level (beginner/intermediate/advanced) [beginner]: ").strip().lower() or "beginner"
        
        print(f"\n🚀 Creating {level} course on {topic}...")
        result = await create_course(topic, level)
        
        if result:
            print("\n🎉 Course generation complete! You can now view the markdown file.")
        else:
            print("\n❌ Course generation failed. Please check the logs for details.")
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())