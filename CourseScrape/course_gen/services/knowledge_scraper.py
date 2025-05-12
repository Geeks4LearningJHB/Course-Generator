from course_gen.core.globals import (
    annotations, requests, logger, urljoin, urlparse, BeautifulSoup, time, json, logging,
    ABC, abstractmethod, dataclass, field, aiohttp, re, random, 
    Dict, List, Optional, Set, Tuple, Union, os, DDGS, urllib, asyncio, nest_asyncio, lazy
)

try:
    from playwright.async_api import async_playwright
except ImportError:
    logging.error("Playwright not installed. Run 'pip install playwright' and 'playwright install'")
    async_playwright = None

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("knowledge_scraper")

# Header to use throughout
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Custom exceptions for better error handling
class ScraperException(Exception):
    """Base exception class for all scraper errors"""
    pass

class NetworkError(ScraperException):
    """Raised for network connectivity issues"""
    pass

class PaywallError(ScraperException):
    """Raised when a paywall is detected"""
    pass

class LoginRequiredError(ScraperException):
    """Raised when login is required to access content"""
    pass

class ContentExtractionError(ScraperException):
    """Raised when content cannot be extracted"""
    pass

@dataclass
class ScrapedContent:
    """Data class for storing scraped content"""
    title: str = ""
    text: str = ""
    code: List[str] = field(default_factory=list)
    url: str = ""
    topic: str = ""
    source: str = ""
    level: str = "intermediate"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {
            "topic": self.topic,
            "title": self.title,
            "content": self.text,
            "code_examples": self.code,
            "source": self.source,
            "url": self.url,
            "level": self.level
        }
    
    def is_valid(self) -> bool:
        """More lenient validation"""
        return bool(self.text.strip())

@dataclass
class SourceConfig:
    """Configuration for a specific content source"""
    base_url: str
    topics: Dict[str, Dict[str, Union[str, int]]]
    content_selectors: List[str]
    code_selectors: List[str]
    avoid_urls: List[str]

class URLManager:
    """Manages URL processing, storage and retrieval"""
    def __init__(self, scraped_urls_file: str = "scraped_urls.json", 
                 bad_urls_file: str = "bad_urls.json"):
        self.scraped_urls_file = scraped_urls_file
        self.bad_urls_file = bad_urls_file
        self.scraped_urls = self._load_urls_file(self.scraped_urls_file)
        self.bad_urls = self._load_urls_file(self.bad_urls_file)
        
        # Cache URL results to avoid redundant processing
        self.url_results_cache = {}
        
        # Configure trusted domains and their delay configurations
        self.trusted_domains = {
            "w3schools.com": (1, 2),
            "geeksforgeeks.org": (2, 3),
            "realpython.com": (2, 4),
            "developer.mozilla.org": (1, 2),
            "docs.python.org": (1, 2),
            "github.com": (2, 3),
            "stackoverflow.com": (2, 3),
            "tutorialspoint.com": (1, 2)
        }
        
        # Default delay for other sites
        self.default_delay = (5, 10)
        
        # Domains to avoid completely
        self.avoid_domains = [
            "pinterest", "facebook.com", "twitter.com", "instagram.com",
            "youtube.com", "medium.com", "quora.com", "linkedin.com",
            "reddit.com", "courses.com", "udemy.com", "coursera.org"
        ]
    
    def _load_urls_file(self, file_path: str) -> Set[str]:
        """Load URLs from JSON file into a set with error handling"""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except json.JSONDecodeError:
                logger.warning(f"Could not parse {file_path}. Creating a new file.")
                return set()
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
                return set()
        return set()

    def save_urls_file(self, file_path: str, urls: Set[str]) -> None:
        """Save URLs set to JSON file with error handling"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(list(urls), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving to {file_path}: {str(e)}")
    
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
    
    def get_delay_for_domain(self, url: str) -> Tuple[float, float]:
        """Get appropriate delay range for a domain"""
        domain = self.extract_domain(url)
        for trusted, delay in self.trusted_domains.items():
            if trusted in domain:
                return delay
        return self.default_delay
    
    def should_skip(self, url: str) -> Tuple[bool, str]:
        """Check if URL should be skipped and return reason if so"""
        domain = self.extract_domain(url)
        
        # Skip if domain should be avoided
        if self.should_avoid_domain(url):
            return True, "Avoided domain"
        
        # Skip if URL or its domain is already in bad_urls
        if url in self.bad_urls or domain in self.bad_urls:
            return True, "Bad URL"
        
        # Skip if already scraped
        if url in self.scraped_urls:
            return True, "Already scraped"
            
        return False, ""
    
    def mark_as_scraped(self, url: str) -> None:
        """Mark URL as successfully scraped"""
        self.scraped_urls.add(url)
        self.save_urls_file(self.scraped_urls_file, self.scraped_urls)
    
    def mark_as_bad(self, url: str) -> None:
        """Mark URL or domain as bad"""
        domain = self.extract_domain(url)
        self.bad_urls.add(domain)
        self.save_urls_file(self.bad_urls_file, self.bad_urls)

class ContentCleaner:
    """Handles cleaning and normalization of scraped content"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Remove citations like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove common ads/cookie notice text
        remove_patterns = [
            r'accept all cookies',
            r'we use cookies',
            r'cookie policy',
            r'privacy policy',
            r'terms of service',
            r'all rights reserved',
            r'copyright \d{4}',
        ]
        
        for pattern in remove_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()

    @staticmethod
    def clean_code(code: str) -> str:
        """Clean code examples"""
        if not code:
            return ""
            
        # Remove shell prompts ($ or > at the beginning of lines)
        code = re.sub(r'^\s*[$>]\s*', '', code, flags=re.MULTILINE)
        
        # Remove extra line breaks and normalize whitespace
        code = re.sub(r'\s+\n', '\n', code)
        code = re.sub(r'\n\s+\n', '\n\n', code)
        
        return code.strip()

class ContentExtractor:
    """Handles extraction of content from HTML"""
    
    def __init__(self, cleaner: ContentCleaner):
        self.cleaner = cleaner
    
    def get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        try:
            if soup.title:
                title = soup.title.string
            else:
                # Try to find h1
                h1 = soup.find('h1')
                title = h1.get_text() if h1 else "Untitled"
                
            return self.cleaner.clean_text(title)
        except Exception as e:
            logger.error(f"Error extracting title: {e}")
            return "Untitled"

    def extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """More robust main content extraction"""
        try:
            # Try all common content containers with minimum text check
            containers = []
            for selector in ["main", "article", "#content", ".content", 
                            "#main", ".main", "div.content", "div.main"]:
                elements = soup.select(selector)
                for el in elements:
                    if len(el.get_text(strip=True)) > 50:  # Lower minimum
                        containers.append(el)
            
            if containers:
                # Combine all matching containers
                combined = BeautifulSoup("", "html.parser")
                for container in containers:
                    combined.append(container)
                return combined
            
            # Fallback: find paragraphs with substantial text
            paragraphs = []
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 40:  # Minimum paragraph length
                    paragraphs.append(p)
            
            if len(paragraphs) >= 3:  # Require at least 3 substantial paragraphs
                combined = BeautifulSoup("", "html.parser")
                for p in paragraphs:
                    combined.append(p)
                return combined
                
            return None
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return None

    def extract_code_examples(self, soup: BeautifulSoup) -> List[str]:
        """Extract code examples from a page"""
        code_examples = []
        
        try:
            # Look for code blocks in pre and code tags
            code_selectors = [
                "pre code", "pre", "code", ".code", "#code",
                ".highlight", ".syntax", ".codeblock", ".code-block",
                "[class*='code']", "[class*='syntax']", "[class*='highlight']"
            ]
            
            for selector in code_selectors:
                for code_block in soup.select(selector):
                    code = self.cleaner.clean_code(code_block.get_text())
                    if code and len(code.strip()) > 10:  # Ignore very short snippets
                        code_examples.append(code)
        except Exception as e:
            logger.error(f"Error extracting code examples: {e}")
            
        return code_examples
    
    def extract_content_with_selectors(self, soup: BeautifulSoup, 
                                       content_selectors: List[str],
                                       code_selectors: List[str]) -> Dict:
        """Source-specific content extraction using configured selectors"""
        content = {"text": "", "code": []}
        
        try:
            # Try all content selectors
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = self.cleaner.clean_text(element.get_text())
                    if text and len(text) > 100:  # Minimum content threshold
                        content["text"] += f"\n{text}"
            
            # Try all code selectors
            for selector in code_selectors:
                code_blocks = soup.select(selector)
                for block in code_blocks:
                    code = self.cleaner.clean_code(block.get_text())
                    if code and len(code.strip()) > 10:
                        content["code"].append(code)
        except Exception as e:
            logger.error(f"Error extracting content with selectors: {e}")
        
        return content if content["text"] else None

    def find_links(self, soup: BeautifulSoup, base_url: str, avoid_patterns: List[str]) -> List[str]:
        """Find relevant links on a page"""
        links = set()
        try:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("#") or href.lower().startswith("javascript:"):
                    continue

                full_url = urljoin(base_url, href)
                if not any(p in full_url for p in avoid_patterns):
                    links.add(full_url)
        except Exception as e:
            logger.error(f"Error finding links: {e}")
            
        return list(links)

    def determine_level(self, content: str, url: str) -> str:
        """Determine content difficulty level based on content and URL"""
        try:
            # Check URL for level indicators
            if "beginner" in url or "basics" in url or "tutorial" in url:
                return "beginner"
            elif "advanced" in url or "expert" in url:
                return "advanced"
            
            # Check for beginner-focused domains
            domain = urlparse(url).netloc.lower()
            if any(domain in site for site in ["w3schools.com", "tutorialspoint.com"]):
                return "beginner"
            
            # Check content for complexity indicators
            if not content:
                return "intermediate"
                
            lower_content = content.lower()
            
            # Advanced topics
            advanced_indicators = [
                "advanced", "expert", "complex", "optimization", 
                "architecture", "design pattern", "algorithm", "data structure",
                "scalability", "performance", "concurrency", "threading", 
                "distributed", "microservice", "asynchronous"
            ]
            
            # Basic topics
            basic_indicators = [
                "introduction", "beginner", "basics", "fundamental", "101", 
                "getting started", "learn", "tutorial", "first steps"
            ]
            
            # Count indicators
            advanced_count = sum(lower_content.count(indicator) for indicator in advanced_indicators)
            basic_count = sum(lower_content.count(indicator) for indicator in basic_indicators)
            
            if advanced_count > basic_count * 2:
                return "advanced"
            elif basic_count > advanced_count * 2:
                return "beginner"
            else:
                return "intermediate"
        except Exception as e:
            logger.error(f"Error determining level: {e}")
            return "intermediate"

class BaseDetector:
    """Base class for detecting paywalls, logins, etc."""
    
    def __init__(self):
        # Paywall detection patterns
        self.paywall_patterns = [
            "subscribe", "subscription", "sign in to continue", 
            "continue reading", "create an account", "premium content",
            "paid member", "unlock", "free trial", "register to read",
            "remaining free articles", "remaining articles", "for full access",
            "join now", "become a member", "sign up today"
        ]

class StandardDetector(BaseDetector):
    """Standard detector using regular HTTP requests"""
    
    def __init__(self):
        super().__init__()
        self.headers = HEADERS
    
    def is_login_required(self, url: str) -> bool:
        """Check if a URL requires login"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
            
            # Check HTTP status code
            if response.status_code in [401, 403, 402]:
                return True
            
            # Check for login redirects
            final_url = response.url.lower()
            if "login" in final_url or "signin" in final_url or "account" in final_url:
                return True
            
            # Check for login-related content
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()
            
            login_keywords = ["login", "sign in", "register", "create account"]
            login_forms = soup.find_all("form", id=lambda x: x and any(keyword in x.lower() for keyword in login_keywords))
            login_forms += soup.find_all("form", class_=lambda x: x and any(keyword in x.lower() for keyword in login_keywords))
            
            # Count login keyword appearances
            login_count = sum(text.count(keyword) for keyword in login_keywords)
            
            # If multiple login indicators present, it's likely login-required
            return len(login_forms) > 0 or login_count > 3
            
        except Exception as e:
            logger.error(f"Error checking login requirement for {url}: {str(e)}")
            return True  # Skip if error occurs

    def is_paywall_present(self, url: str) -> bool:
        """Check if a URL has a paywall"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Check HTTP status
            if response.status_code in [401, 402, 403]:
                return True
                
            # Check for paywall indicators in the page content
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()
            
            # Count paywall keyword appearances
            paywall_count = sum(text.count(keyword) for keyword in self.paywall_patterns)
            
            # Check for paywall-related elements
            paywall_elements = soup.find_all(["div", "section"], id=lambda x: x and "paywall" in x.lower())
            paywall_elements += soup.find_all(["div", "section"], class_=lambda x: x and "paywall" in x.lower())
            paywall_elements += soup.find_all(["div", "section"], id=lambda x: x and "subscribe" in x.lower())
            paywall_elements += soup.find_all(["div", "section"], class_=lambda x: x and "subscribe" in x.lower())
            
            # If multiple paywall indicators present, it's likely a paywall
            return len(paywall_elements) > 0 or paywall_count > 3
            
        except Exception as e:
            logger.error(f"Error checking paywall for {url}: {str(e)}")
            return True  # Skip if error occurs

class BaseScraper(ABC):
    """Abstract base class for content scrapers"""
    
    def __init__(self, url_manager: URLManager, content_cleaner: ContentCleaner, 
                 extractor: ContentExtractor, detector: BaseDetector):
        self.url_manager = url_manager
        self.cleaner = content_cleaner
        self.extractor = extractor
        self.detector = detector
        
        self.headers = HEADERS
        
        # Sources configuration
        self.sources = {
            "w3schools": SourceConfig(
                base_url="https://www.w3schools.com/",
                topics={
                    "python": {"url": "python/default.asp", "depth": 3},
                    "javascript": {"url": "js/default.asp", "depth": 3},
                    "sql": {"url": "sql/default.asp", "depth": 2}
                },
                content_selectors=["#main", ".w3-example"],
                code_selectors=[".w3-code"],
                avoid_urls=["tryit.asp", "exercise.asp"]
            ),
            "geeksforgeeks": SourceConfig(
                base_url="https://www.geeksforgeeks.org/",
                topics={
                    "python": {"url": "python-programming-language/", "depth": 3},
                    "data structures": {"url": "data-structures/", "depth": 2},
                    "algorithms": {"url": "fundamentals-of-algorithms/", "depth": 2}
                },
                content_selectors=[".content", "article"],
                code_selectors=[".code-container pre"],
                avoid_urls=["practice/", "quiz/"]
            ),
            "realpython": SourceConfig(
                base_url="https://realpython.com/",
                topics={
                    "python": {"url": "tutorials/", "depth": 2},
                    "django": {"url": "django/", "depth": 2}
                },
                content_selectors=[
                    "article#article-body",
                    ".article-body",
                    ".article-content"],
                code_selectors=["div.highlight pre", "pre code"],
                avoid_urls=["/courses/", "/quiz/"]
            )
        }
    
    '''@abstractmethod
    def scrape_page(self, url: str, topic: str = "") -> Optional[ScrapedContent]:
        """Scrape content from a single page"""
        pass'''

class StandardScraper(BaseScraper):
    """Standard scraper using regular HTTP requests"""
    
    def __init__(self, url_manager: URLManager, content_cleaner: ContentCleaner, 
                 extractor: ContentExtractor, detector: StandardDetector):
        super().__init__(url_manager, content_cleaner, extractor, detector)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_page(self, url: str, topic: str = "") -> Optional[ScrapedContent]:
        """Scrape content from a single page using standard requests"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract title
            title = self.extractor.get_title(soup)
            
            # Extract main content
            main_content = self.extractor.extract_main_content(soup)
            if not main_content:
                return None
                
            # Clean text content
            text = self.cleaner.clean_text(main_content.get_text())
            
            # Extract code examples
            code_examples = self.extractor.extract_code_examples(soup)
            
            content = ScrapedContent(
                title=title,
                text=text,
                code=code_examples,
                url=url,
                topic=topic,
                source="web_search",
                level=self.extractor.determine_level(text, url)
            )
            
            return content #if content.is_valid() else None
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def search_and_scrape(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for content using DuckDuckGo and scrape results"""
        knowledge = []
        results = DDGS().text(query, max_results=max_results * 2)
        
        processed_count = 0
        
        for result in results:
            if processed_count >= max_results:
                break

            url = result['href']

            if self.url_manager.should_skip(url):
                continue

            try:
                delay_range = self.url_manager.get_delay_for_domain(url)
                time.sleep(random.uniform(*delay_range))

                if self.url_manager.should_skip(url):
                    continue

                content = self.scrape_page(url, query)
                if content and content.text.strip():
                    knowledge.append({
                        "topic": query,
                        "title": result['title'] if result['title'] else content.title,
                        "content": content.text,
                        "code_examples": content.code,
                        "source": "web_search",
                        "url": url,
                        "level": content.level
                    })
                    self.url_manager.mark_as_scraped(url)
                    processed_count += 1
                else:
                    logger.info(f"⚠️ No useful content found at: {url}")
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                self.url_manager.mark_as_bad(url)

        return knowledge

    def scrape_configured_sources(self) -> List[Dict]:
        """Scrape content from pre-configured sources"""
        knowledge = []
        
        for source_name, config in self.sources.items():
            for topic, topic_config in config.topics.items():
                logger.info(f"Scraping {topic} from {source_name}")

                try:
                    base_url = urljoin(config.base_url, topic_config["url"])
                    
                    delay_range = self.url_manager.get_delay_for_domain(base_url)
                    time.sleep(random.uniform(*delay_range))
                    
                    response = self.session.get(base_url, timeout=15)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                    # Extract content using source-specific selectors
                    main_content = self.extractor.extract_content_with_selectors(
                        soup, 
                        config.content_selectors,
                        config.code_selectors
                    )
                
                    if main_content and main_content.get("text"):
                        content = ScrapedContent(
                            title=self.extractor.get_title(soup) or f"{topic.capitalize()} Tutorial",
                            text=main_content["text"],
                            code=main_content.get("code", []),
                            url=base_url,
                            topic=topic,
                            source=source_name,
                            level=self.extractor.determine_level(main_content["text"], base_url)
                        )
                        
                        knowledge.append(content.to_dict())
                        self.url_manager.mark_as_scraped(base_url)
                    else:
                        logger.warning(f"No main content found at {base_url}")

                    # Find and process additional pages
                    page_links = self.extractor.find_links(soup, base_url, config.avoid_urls)
                    for link in page_links[:topic_config["depth"]]:
                        try:
                            time.sleep(random.uniform(*self.url_manager.get_delay_for_domain(link)))
                            
                            # Skip if already processed
                            should_skip, reason = self.url_manager.should_skip(link)
                            if should_skip:
                                logger.info(f"Skipping {link}: {reason}")
                                continue
                                
                            page_content = self.scrape_page(link, topic)
                            if page_content and page_content.is_valid():
                                knowledge.append(page_content.to_dict())
                                self.url_manager.mark_as_scraped(link)
                        except Exception as e:
                            logger.error(f"Error scraping {link}: {str(e)}")
                            self.url_manager.mark_as_bad(link)

                except Exception as e:
                    logger.error(f"Error scraping {topic} from {source_name}: {str(e)}")

        return knowledge

class PlaywrightScraper(BaseScraper):
    """Playwright-based scraper for JavaScript-heavy pages"""
    
    def __init__(self, url_manager: URLManager, content_cleaner: ContentCleaner, 
                 extractor: ContentExtractor, detector: BaseDetector):
        super().__init__(url_manager, content_cleaner, extractor, detector)
        
        if async_playwright is None:
            raise ImportError("Playwright is required but not installed. Run 'pip install playwright' and 'playwright install'")
        self.playwright = async_playwright
        
    async def _handle_cookie_popups(self, page) -> bool:
        """Handle cookie consent popups"""
        # Common consent button selectors
        consent_selectors = [
            "button[id*='cookie']", "button[class*='cookie']",
            "button:has-text('Accept')", "button:has-text('Agree')",
            "button:has-text('Accept all')", "a:has-text('Accept cookies')",
            "[id*='cookie'] button", "[class*='cookie'] button",
            "button:has-text('OK')", "button:has-text('Got it')"
        ]
        
        for selector in consent_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    await page.wait_for_timeout(1000)
                    return True
            except Exception:
                continue
        return False
    
    async def _is_paywall_present_with_playwright(self, url: str, timeout: int = 10) -> bool:
        """Wrapper method to handle exceptions gracefully during paywall detection"""
        try:
            return await self._is_paywall_present_async(url, timeout)
        except Exception as e:
            logger.error(f"Error checking paywall with Playwright for {url}: {str(e)}")
            return True

    async def _is_paywall_present_async(self, url: str, timeout: int = 10) -> bool:
        """Check if a URL has a paywall using Playwright (async implementation)"""
        if not self.playwright:
            logger.error("Playwright is not available")
            return None
        
        try:
            async with self.playwright() as p:
                if not p:
                    logger.error(f"Failed to initialize playwright for {url}")
                    return None
                    
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent=self.headers["User-Agent"]
                )

                # Avoid detection
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                """)

                page = await context.new_page()
                page.set_default_timeout(timeout * 1000)

                response = await page.goto(url, wait_until="networkidle")
                await page.wait_for_timeout(2000)

                # Handle cookies
                await self._handle_cookie_popups(page)

                if response.status in [401, 402, 403]:
                    await browser.close()
                    return True

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                text = soup.get_text().lower()

                paywall_count = sum(text.count(kw) for kw in self.detector.paywall_patterns)

                modal_selectors = [
                    ".paywall", ".modal", ".popup", ".subscription", ".subscribe",
                    "[id*='paywall']", "[id*='modal']", "[id*='popup']",
                    "[id*='subscribe']", "[class*='paywall']", "[class*='subscribe']"
                ]

                has_modal = False
                for selector in modal_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for el in elements:
                            if await el.is_visible():
                                has_modal = True
                                break
                        if has_modal:
                            break
                    except Exception:
                        continue

                floating_elements = await page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('div, section, aside');
                        return Array.from(elements).some(el => {
                            const style = window.getComputedStyle(el);
                            return (style.position === 'fixed' || style.position === 'absolute') &&
                                parseInt(style.zIndex || 0) > 10 &&
                                el.offsetWidth > window.innerWidth * 0.5 &&
                                el.offsetHeight > window.innerHeight * 0.3;
                        });
                    }
                """)

                await browser.close()
                return has_modal or floating_elements or paywall_count > 3

        except Exception as e:
            logger.error(f"Error in async paywall check for {url}: {str(e)}")
            return True
    
    async def scrape_page(self, url: str, topic: str = "") -> Optional[ScrapedContent]:
        """Scrape content from a JavaScript-heavy page using Playwright and return ScrapedContent"""       
        if not self.playwright:
            logger.error("Playwright is not available")
            return None
        
        try:
            async with self.playwright() as p:
                if not p:
                    logger.error(f"Failed to initialize playwright for {url}")
                    return None
                
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent=self.headers["User-Agent"]
                )

                # Add stealth script to avoid detection
                await context.add_init_script(""" 
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                """)

                page = await context.new_page()
                await page.set_default_timeout(15000)

                # Navigate to the URL
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_timeout(2000)  # Wait for dynamic content

                # Handle cookie popups
                await self._handle_cookie_popups(page)

                # Get page content and parse it
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")

                # Extract title and content
                title = self.extractor.get_title(soup)
                main_content = self.extractor.extract_main_content(soup)
                if not main_content:
                    return None

                # Clean the text
                text = self.cleaner.clean_text(main_content.get_text())

                # Extract code examples
                code_examples = self.extractor.extract_code_examples(soup)

                # Create ScrapedContent instance
                scraped = ScrapedContent(
                    title=title,
                    text=text,
                    code=code_examples,
                    url=url,
                    topic=topic,
                    source="web_search",
                    level=self.extractor.determine_level(text, url)
                )
                
                await browser.close()
                return scraped if scraped.is_valid() else None

        except Exception as e:
            logger.error(f"Playwright scraping error at {url}: {str(e)}")
            return None
    
    async def search_and_scrape(self, query: str, max_results: int = 10) -> List[Dict]:
        """Proper async implementation"""
        knowledge = []
        try:
            results = DDGS().text(query, max_results=max_results * 2)
            processed_count = 0
            
            for result in results:
                if processed_count >= max_results:
                    break

                url = result['href']
                skip, reason = self.url_manager.should_skip(url)
                if skip:
                    continue

                try:
                    delay_range = self.url_manager.get_delay_for_domain(url)
                    await asyncio.sleep(random.uniform(*delay_range))
                    
                    # Try Playwright first for JS-heavy sites
                    content = await self.scrape_page(url, query)
                    
                    if content and content.text.strip():
                        knowledge.append(content.to_dict())
                        self.url_manager.mark_as_scraped(url)
                        processed_count += 1
                    else:
                        self.url_manager.mark_as_bad(url)
                        
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Search error: {e}")