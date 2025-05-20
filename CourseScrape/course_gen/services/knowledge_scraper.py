from course_gen.core.globals import (
    requests, logger, urljoin, urlparse, BeautifulSoup, time, json, logging,
    ABC, re, random, copy, random, sys,
    Dict, List, Optional, Set, Tuple, os, DDGS, asyncio
)

from playwright.async_api import async_playwright
from course_gen.core import ScrapedContent
from course_gen.core import (
    USER_AGENTS, BASE_HEADERS, CODE_SELECTORS, ADVANCED_INDICATORS, 
    BASIC_INDICATORS, ELEMENTS_TO_REMOVE, NON_CONTENT_CASES, PAYWALL_PATTERNS, 
    CONSENT_SELECTORS, MODAL_SELECTORS, COMMON_CONTENT_SELECTORS
)
from course_gen.utils.file_manager import FileManager

# Configure logging
logger = logging.getLogger("knowledge_scraper")

# Windows fixes for python3.11+ and playwright 
if sys.platform == "win32":
    # Required for Playwright subprocess handling
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Disable Windows-specific memory protections
    os.environ['PLAYWRIGHT_DISABLE_ISOLATED_HEAP'] = '1'
    os.environ['PLAYWRIGHT_NO_PROXY'] = '1'


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

# Global headers function
def get_random_headers():
        """Return headers with a random user agent"""
        return {
            **BASE_HEADERS,
            "User-Agent": random.choice(USER_AGENTS)
        }


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
            "tutorialspoint.com": (1, 2),
            "codecademy.com": (1, 2), 
            "tutorialspoint.com": (1, 2),
            "simplilearn.com": (1, 2),
            "freecodecamp.org": (1, 2),
            "javatpoint.com": (1, 2)
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
            "/watch", "/signin", "/login", "/video"
        ]
    
    def _load_urls_file(self, file_path: str) -> Set[str]:
        """Load URLs from JSON file using the generic loader."""
        try:
            data = FileManager.load_json(file_path)
            return set(data) if isinstance(data, list) else set()
        except Exception:
            logger.warning(f"Falling back to empty set for {file_path}")
            return set()
    
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
        return any(avoid in domain for avoid in self.avoid_domains)\
            
    def should_avoid_pattern(self, url: str) -> bool:
        if any(pattern in url for pattern in self.skip_patterns):
            return False
    
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
        
        if url in self.trusted_domains.keys():
            return False, ""
        
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
        try:
            self.scraped_urls.add(url)
            
            if not isinstance(self.scraped_urls_file, (str, os.PathLike)):
                logger.error(f"Invalid output_file: {self.scraped_urls_file}")
                raise ValueError("Scraped urls output path must be a string")
            
            FileManager.save_json(self.scraped_urls, self.scraped_urls_file)
        except Exception as e:
            logger.error(f"Scraped urls save failed: {e}")
            raise
    
    def mark_as_bad(self, url: str) -> None:
        """Mark URL or domain as bad"""
        try:
            domain = self.extract_domain(url)
            self.bad_urls.add(domain)
            
            if not isinstance(self.bad_urls_file, (str, os.PathLike)):
                logger.error(f"Invalid output_file: {self.bad_urls_file}")
                raise ValueError("Bad urls output path must be a string")
            
            FileManager.save_json(self.bad_urls, self.bad_urls_file)
        except Exception as e:
            logger.error(f"Bad urls save failed: {e}")
            raise

# In course_gen/core/knowledge_scraper.py

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
        
        # Remove citations like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Enhanced removal patterns for ads, cookies, and legal notices
        remove_patterns = [
            r'accept\s*(all)?\s*cookies?', 
            r'we\s*use\s*cookies?',
            r'(this\s*)?website\s*uses?\s*cookies?',
            r'cookie\s*(policy|notice|banner|consent|preferences)',
            r'privacy\s*(policy|notice|statement)',
            r'terms\s*(of\s*service|and\s*conditions)',
            r'all\s*rights\s*reserved',
            r'copyright\s*©?\s*\d{4}',
            r'advertisement|sponsored\s*content',
            r'please\s*(enable|accept)\s*cookies',
            r'(sign\s*up|subscribe)\s*(for\s*free)?\s*(newsletter|updates)',
            r'continue\s*(reading|with)\s*(a\s*subscription|free\s*trial)',
            r'(enable|disable)\s*notifications?',
            r'this\s*content\s*is\s*(protected|locked)',
            r'read\s*more\s*(with|by)\s*(subscription|membership)',
            r'you\s*have\s*\d+\s*free\s*articles?\s*left',
            r'register\s*(to|for)\s*(read|view|access)',
            r'log\s*in\s*to\s*(view|read|access)',
            r'create\s*(a\s*)?free\s*account',
            r'join\s*(now|today)\s*for\s*free',
            r'your\s*email\s*(address)?\s*(is|will be)\s*required',
            r'this\s*site\s*is\s*protected\s*by\s*recaptcha',
            r'continue\s*to\s*site|read\s*more\s*below',
            r'close\s*(this|ad|popup|notification)',
            r'dismiss\s*(this|message|notification)',
            r'by\s*continuing\s*you\s*agree\s*to',
            r'we\s*value\s*your\s*privacy',
            r'manage\s*(your)?\s*(cookie|privacy)\s*settings',
            r'essential\s*cookies\s*only',
            r'accept\s*(all|necessary)\s*cookies',
            r'customize\s*your\s*settings',
            r'learn\s*more\s*about\s*how\s*we\s*use\s*cookies',
            r'allow\s*(all|necessary)\s*cookies',
            r'necessary\s*cookies\s*only',
            r'only\s*essential\s*cookies',
            r'strictly\s*necessary\s*cookies',
            r'functional\s*cookies',
            r'performance\s*cookies',
            r'targeting\s*cookies',
            r'advertising\s*cookies',
            r'analytics\s*cookies',
            r'social\s*media\s*cookies'
        ]
        
        # Remove all patterns case-insensitively
        for pattern in remove_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove any remaining standalone cookie-related words
        cookie_words = ['cookie', 'cookies', 'gdpr', 'ccpa', 'consent', 'banner']
        for word in cookie_words:
            text = re.sub(rf'\b{word}\b', '', text, flags=re.IGNORECASE)
        
        # Remove empty parentheses/brackets that might remain after cleaning
        text = re.sub(r'\([\s]*\)', '', text)
        text = re.sub(r'\[[\s]*\]', '', text)
        
        # Final whitespace normalization
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

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
        self.code_selectors = CODE_SELECTORS
        self.advanced_indicators = ADVANCED_INDICATORS
        self.basic_indicators = BASIC_INDICATORS
        self.elements_to_remove = ELEMENTS_TO_REMOVE # This is a list of tags like 'script', 'style'
        self.non_content_cases = NON_CONTENT_CASES # This is a list of patterns for class/id names

        # --- NEW/UPDATED SELECTORS FOR MORE ROBUST CLEANING ---
        self.ad_and_cookie_selectors = [
            ".cookie-consent", "#cookie-notice", ".gdpr-banner", ".ad",
            ".advertisement", "[id*='ad-container']", "[class*='ad-slot']",
            ".banner-ad", ".popup", ".modal", ".overlay", "[id*='cookie-']",
            "[class*='cookie-']", ".consent", "[aria-label*='cookie']",
            "footer", "header", "nav", "aside", ".sidebar", ".navigation",
            ".related-posts", ".social-share", ".comments", ".comment-form",
            ".pagination", ".breadcrumbs", ".widget", ".promo", ".upsell",
            "[class*='js-consent']", "[id*='adblock']"
        ]
        # Combining with existing lists from globals if they are suitable
        self.elements_to_remove.extend(['iframe', 'form', 'button', 'input', 'select', 'textarea']) # Add more tags to remove
        self.non_content_cases.extend(['ad', 'cookie', 'banner', 'nav', 'footer', 'header', 'sidebar', 'social', 'popup', 'modal', 'overlay', 'consent', 'promo', 'widget'])
        # --- END NEW/UPDATED SELECTORS ---

    # ... (get_title, extract_main_content, extract_code_examples, find_links, determine_level remain the same) ...

    def _clean_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove non-content elements from the soup"""
        # Make a copy to avoid modifying the original
        clean_soup = copy(soup)
        
        # Remove unwanted elements by tag name (from self.elements_to_remove)
        for tag in self.elements_to_remove:
            for element in clean_soup.find_all(tag):
                element.decompose()
        
        # --- ENHANCEMENT START ---
        # Remove elements with specific ad/cookie/non-content selectors
        for selector in self.ad_and_cookie_selectors:
            for element in clean_soup.select(selector):
                element.decompose()
        # --- ENHANCEMENT END ---

        # Remove elements with non-content classes/IDs (from self.non_content_cases)
        for class_name in self.non_content_cases:
            # Match class or ID containing the pattern
            for element in clean_soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()
            for element in clean_soup.find_all(id=re.compile(class_name, re.I)):
                element.decompose()
        
        # Remove empty elements
        for element in clean_soup.find_all():
            # Check if element is truly empty or contains only whitespace
            if not element.get_text(strip=True) and not element.find(lambda tag: tag.get_text(strip=True)):
                element.decompose()
        
        return clean_soup

    def extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract clean main content with enhanced filtering"""
        try:
            # First clean the soup of non-content elements
            clean_soup = self._clean_content(soup)
            
            # Enhanced content detection with scoring
            containers = []
            for selector in ["main", "article", "#content", ".content", 
                            "#main", ".main", "div.content", "div.main",
                            "section", ".post", ".article", ".entry"]:
                elements = clean_soup.select(selector)
                for el in elements:
                    text = el.get_text(strip=True)
                    # Score based on text length and quality indicators
                    score = len(text)
                    
                    # Penalize elements that contain ad/cookie related text
                    if any(keyword in text.lower() for keyword in ['cookie', 'privacy', 'terms', 'advertisement']):
                        score -= 1000
                    
                    # Bonus for educational content indicators
                    if any(keyword in text.lower() for keyword in ['example', 'tutorial', 'learn', 'guide', 'how to']):
                        score += 500
                    
                    if score > 50:  # Minimum score threshold
                        containers.append((el, score))
            
            if containers:
                # Sort by score and take top 3 containers
                containers.sort(key=lambda x: x[1], reverse=True)
                top_containers = [c[0] for c in containers[:3]]
                
                # Combine all matching containers
                combined = BeautifulSoup("", "html.parser")
                for container in top_containers:
                    combined.append(container)
                return combined
            
            # Fallback: find paragraphs with substantial text and good indicators
            paragraphs = []
            for p in clean_soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 40:  # Minimum paragraph length
                    # Skip paragraphs with ad/cookie text
                    if not any(keyword in text.lower() for keyword in ['cookie', 'privacy', 'terms', 'advertisement']):
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
            for selector in self.code_selectors:
                for code_block in soup.select(selector):
                    code = self.cleaner.clean_code(code_block.get_text(strip=True))
                    if code:
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
            # Clean the soup first
            clean_soup = self._clean_content(soup)
            
            # Try all content selectors
            for selector in content_selectors:
                elements = clean_soup.select(selector)
                for element in elements:
                    text = self.cleaner.clean_text(element.get_text())
                    if text and len(text) > 100:  # Minimum content threshold
                        content["text"] += f"\n{text}"
            
            # Try all code selectors (from original soup)
            for selector in self.code_selectors:
                code_blocks = soup.select(selector)
                for block in code_blocks:
                    code = self.cleaner.clean_code(block.get_text())
                    if code:
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
            
            # Count indicators
            advanced_count = sum(lower_content.count(indicator) for indicator in self.advanced_indicators)
            basic_count = sum(lower_content.count(indicator) for indicator in self.basic_indicators)
            
            if advanced_count > basic_count * 2:
                return "advanced"
            elif basic_count > advanced_count * 2:
                return "beginner"
            else:
                return "intermediate"
        except Exception as e:
            logger.error(f"Error determining level: {e}")
            return "any level"
        
    def _clean_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove non-content elements from the soup"""
        # Make a copy to avoid modifying the original
        clean_soup = copy(soup)
        
        # Remove unwanted elements by tag name
        for tag in self.elements_to_remove:
            for element in clean_soup.find_all(tag):
                element.decompose()
        
        # Remove elements with non-content classes/IDs
        for class_name in self.non_content_cases:
            # Match class or ID containing the pattern
            for element in clean_soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()
            for element in clean_soup.find_all(id=re.compile(class_name, re.I)):
                element.decompose()
        
        # Remove empty elements
        for element in clean_soup.find_all():
            if not element.get_text(strip=True) and not element.find_all():
                element.decompose()
        
        return clean_soup

class BaseDetector:
    """Base class for detecting paywalls, logins, etc."""
    
    def __init__(self):
        # Paywall detection patterns
        self.paywall_patterns = PAYWALL_PATTERNS

class StandardDetector(BaseDetector):
    """Standard detector using regular HTTP requests"""
    
    def __init__(self):
        super().__init__()
        self.headers = get_random_headers()
    
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
        
        self.headers = get_random_headers()
        
        self.code_selectors = CODE_SELECTORS
        self.consent_selectors = CONSENT_SELECTORS
        self.modal_selectors = MODAL_SELECTORS
        self.common_content_selectors = COMMON_CONTENT_SELECTORS
        
        # Sources configuration
        self.sources = {}

class StandardScraper(BaseScraper):
    """Standard scraper using regular HTTP requests"""
    
    def __init__(self, url_manager: URLManager, content_cleaner: ContentCleaner, 
                 extractor: ContentExtractor, detector: StandardDetector):
        super().__init__(url_manager, content_cleaner, extractor, detector)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _scrape_page(self, url: str) -> Dict:
        """Scrape content from a single page"""
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
            
            return {
                "title": title, 
                "text": text, 
                "code": code_examples
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

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
                                
                            page_content = self._scrape_page(link, topic)
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
        
        self.headers = get_random_headers()
        
        self.last_search_time = 0
        self.search_delay = (3, 6)  # Random delay between 3-6 seconds
        self.max_retries = 3
        
        self.visited_urls = set()  # Track visited URLs
        self.current_domain = None  # Track current domain being scraped
        
        self.pagination_selectors = [
            "a:has-text('Next')", "a:has-text('Next ❯')", 
            "a:has-text('Continue')", ".next a", 
            ".pagination a:last-child", "#nextbtn"
        ]
    
    async def _handle_cookie_popups(self, page) -> bool:
        """Handle cookie consent popups""" 
        for selector in self.consent_selectors:
            try:
                element = await page.query_selector(selector)
                if element is not None and await element.is_visible():
                    await element.click()
                    await page.wait_for_timeout(1000)
                    return True
            except Exception:
                continue
        return False
    
    async def _is_paywall_present_with_playwright(self, url: str, timeout: int = 10) -> bool:
        """Wrapper method to handle exceptions gracefully during paywall detection"""
        if self.url_manager.is_trusted_domain(url):
            return False
        
        try:
            return await self._is_paywall_present_async(url, timeout)
        except Exception as e:
            logger.error(f"Error checking paywall with Playwright for {url}: {str(e)}")
            return False

    async def _is_paywall_present_async(self, url: str, timeout: int = 10) -> bool:
        """Check if a URL has a paywall using Playwright (async implementation)"""    
        try:
            async with async_playwright() as p:
                if not p:
                    logger.error(f"Failed to initialize playwright for {url}")
                    return False
                    
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent=get_random_headers()["User-Agent"],
                    extra_http_headers={
                        k: v for k, v in self.headers.items() 
                        if k.lower() not in ['user-agent']
                    }
                )

                # Avoid detection
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                """)

                page = await context.new_page()
                page.set_default_timeout(timeout * 1000)

                try:
                    # Use a more flexible approach with timeout handling
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
                    # Wait a bit for potential dynamic content
                    await page.wait_for_timeout(2000)
                except Exception as nav_error:
                    logger.warning(f"Navigation issue for {url}: {str(nav_error)}")
                    await browser.close()
                    return False  # Don't mark as paywall just because of navigation issues

                # Handle cookies
                await self._handle_cookie_popups(page)

                if response.status in [401, 402, 403]:
                    await browser.close()
                    return True

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                text = soup.get_text().lower()

                paywall_keywords = ['subscribe', 'subscription', 'premium', 'paid membership', 'paywall']
                paywall_count = sum(text.count(kw) for kw in paywall_keywords)

                has_modal = False
                for selector in self.modal_selectors:
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

                # Specifically look for text that suggests free content
                free_indicators = ["free", "tutorial", "learn", "documentation", "guide", "how to"]
                has_free_indicator = any(indicator in text for indicator in free_indicators)

                await browser.close()
                
                # Only mark as paywall if we have multiple strong indicators
                # and no free content indicators
                if has_free_indicator:
                    return False
                    
                return has_modal and paywall_count > 5

        except Exception as e:
            logger.error(f"Error in async paywall check for {url}: {str(e)}")
            return False
    
    async def scrape_page_async(self, url: str, topic: str = "", depth=0, max_depth=8) -> Optional[ScrapedContent]:
        """Scrape content from a JavaScript-heavy page using Playwright and return ScrapedContent"""
        self.headers = get_random_headers()
        
        # Initialize domain tracking if this is the first page
        if depth == 0:
            self.current_domain = urlparse(url).netloc
            self.visited_urls = set()  # Reset for new scraping session
        
        # Check if we've already visited this URL
        if url in self.visited_urls:
            logger.info(f"Skipping already visited URL: {url}")
            return None
            
        self.visited_urls.add(url)
        
        if depth >= max_depth:
            return None
        
        browser = None
        context = None
        page = None
        
        try:
            # Initialize Playwright
            async with async_playwright() as p:
                if p is None:
                    logger.error(f"Failed to initialize Playwright for {url}")
                    return None
                
                try:
                    # Launch browser with null checks
                    browser = await p.chromium.launch(headless=True)
                    if browser is None:
                        logger.error(f"Failed to launch browser for {url}")
                        return None
                    
                    # Create context with null checks
                    context = await browser.new_context(
                        viewport={"width": 1280, "height": 800},
                        user_agent=self.headers["User-Agent"]
                    )
                    if context is None:
                        logger.error(f"Failed to create context for {url}")
                        await self._safe_close_browser(browser)
                        return None

                    # Add stealth script
                    try:
                        await context.add_init_script(""" 
                            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                        """)
                    except Exception as e:
                        logger.warning(f"Could not add init script for {url}: {str(e)}")

                    # Create page with null checks
                    page = await context.new_page()
                    if page is None:
                        logger.error(f"Failed to create page for {url}")
                        await self._safe_close_context(context)
                        await self._safe_close_browser(browser)
                        return None

                    if page is not None:
                        try:
                            page.set_default_timeout(20000)
                        except Exception as e:
                            logger.warning(f"Could not set timeout for {url}: {str(e)}")
                            
                    # Navigation with response checking
                    response = None
                    try:
                        response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                        if response is None:
                            logger.warning(f"Navigation to {url} returned no response")
                        await page.wait_for_timeout(2000)
                    except Exception as e:
                        logger.warning(f"Navigation issue for {url}, but continuing: {str(e)}")

                    # Handle cookie popups
                    try:
                        if page is not None:
                            await self._handle_cookie_popups(page)
                    except Exception as e:
                        logger.warning(f"Could not handle cookie popups for {url}: {str(e)}")

                    # Get page content with null checks
                    html_content = None
                    try:
                        if page is not None:
                            html_content = await page.content()
                    except Exception as e:
                        logger.error(f"Could not get page content for {url}: {str(e)}")
                        await self._safe_close_page(page)
                        await self._safe_close_context(context)
                        await self._safe_close_browser(browser)
                        return None

                    if html_content is None:
                        logger.error(f"No content retrieved for {url}")
                        await self._safe_close_page(page)
                        await self._safe_close_context(context)
                        await self._safe_close_browser(browser)
                        return None

                    # Parse content
                    soup = BeautifulSoup(html_content, "html.parser")
                    if soup is None:
                        logger.error(f"Could not parse HTML for {url}")
                        await self._safe_close_page(page)
                        await self._safe_close_context(context)
                        await self._safe_close_browser(browser)
                        return None

                    # Extract title with null check
                    title = self.extractor.get_title(soup) or "No title found"
                    
                    # Extract main content with fallbacks
                    main_content = self.extractor.extract_main_content(soup)
                    if main_content is None or not main_content.get_text().strip(): 
                        for selector in self.common_content_selectors:
                            try:
                                elements = soup.select(selector)
                                if elements and elements[0].get_text().strip():
                                    main_content = elements[0]
                                    break
                            except Exception:
                                continue
                    
                    if main_content is None or not main_content.get_text().strip():
                        logger.warning(f"Could not extract main content from {url}")
                        await self._safe_close_page(page)
                        await self._safe_close_context(context)
                        await self._safe_close_browser(browser)
                        return None

                    # Clean and validate text
                    text = self.cleaner.clean_text(main_content.get_text())
                    if len(text.split()) < 50:
                        logger.warning(f"Content from {url} is too short ({len(text.split())} words)")
                        await self._safe_close_page(page)
                        await self._safe_close_context(context)
                        await self._safe_close_browser(browser)
                        return None
                    
                    # Extract code examples with fallbacks
                    code_examples = self.extractor.extract_code_examples(soup) or []
                    if (any(keyword in url.lower() for keyword in ["tutorial", "learn", "guide", "howto"]) and 
                        any(tech in url.lower() for tech in ["python", "javascript", "java", "sql", "code"]) and 
                        not code_examples):
                        
                        for selector in self.code_selectors:
                            try:
                                elements = soup.select(selector)
                                if elements:
                                    code_examples = [el.get_text() for el in elements]
                                    break
                            except Exception:
                                continue

                    # Create and return scraped content
                    scraped = ScrapedContent(
                        title=title,
                        text=text,
                        code=code_examples,
                        url=url,
                        topic=topic,
                        level=self.extractor.determine_level(text, url)
                    )
                    
                    # Check for pagination/next links (W3Schools-specific and general patterns)
                    next_links = []
                    
                    for selector in self.pagination_selectors:
                        try:
                            next_link = await page.query_selector(selector)
                            if next_link:
                                href = await next_link.get_attribute("href")
                                if href and not href.startswith("#"):
                                    next_url = urljoin(url, href)
                                    next_links.append(next_url)
                        except Exception:
                            continue

                    # Follow the first valid next link found
                    if next_links:
                        next_url = next_links[0]
                        parsed_next = urlparse(next_url)
                        
                        # Only follow if same domain and not visited
                        if (parsed_next.netloc == self.current_domain and 
                            next_url not in self.visited_urls and
                            depth < max_depth):
                            
                            logger.info(f"Following next page link: {next_url}")
                            next_content = await self.scrape_page_async(
                                next_url, topic, depth + 1, max_depth
                            )
                            if next_content:
                                scraped.text += f"\n\n{next_content.text}"
                                scraped.code.extend(next_content.code)
                        else:
                            logger.info(f"Skipping next link (domain/visited/depth): {next_url}")
        
                    # Validate scraped content
                    if not hasattr(scraped, 'is_valid') or not scraped.is_valid():
                        logger.warning(f"Scraped content validation failed for {url}")
                        await self._safe_close_page(page)
                        await self._safe_close_context(context)
                        await self._safe_close_browser(browser)
                        return None

                    await self._safe_close_page(page)
                    await self._safe_close_context(context)
                    await self._safe_close_browser(browser)
                    return scraped
                except Exception as e:
                    print(e)
                    
        except Exception as e:
            logger.error(f"Playwright scraping error at {url}: {str(e)}")
            await self._safe_close_page(page)
            await self._safe_close_context(context)
            await self._safe_close_browser(browser)
            return None
        
    def scrape_page(self, url: str, topic: str = "") -> Optional[ScrapedContent]:
        """Synchronous wrapper for the async scrape_page method"""
        return asyncio.run(self.scrape_page_async(url, topic))

    async def _safe_close_page(self, page):
        """Safely close a page with error handling"""
        if page is not None:
            try:
                await page.close()
            except Exception as e:
                logger.warning(f"Error closing page: {str(e)}")

    async def _safe_close_context(self, context):
        """Safely close a context with error handling"""
        if context is not None:
            try:
                await context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {str(e)}")

    async def _safe_close_browser(self, browser):
        """Safely close a browser with error handling"""
        if browser is not None:
            try:
                await browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {str(e)}")
    
    async def search_and_scrape_async(self, query: str, level = "any level", max_results: int = 10) -> List[Dict]:
        """Async implementation of search and scrape"""
        knowledge = []
        try:
            # Implement delay between searches to prevent ratelimiting
            current_time = time.time()
            time_since_last = current_time - self.last_search_time
            if time_since_last < random.uniform(*self.search_delay):
                delay = random.uniform(*self.search_delay) - time_since_last
                await asyncio.sleep(delay)
            
            enhanced_query = f"{query} for {level} course OR tutorial OR guide OR learn"
            results_list = []
            
            # Retry mechanism
            for attempt in range(self.max_retries):
                try:
                    results = DDGS(headers=get_random_headers()).text(enhanced_query, max_results=max_results * 2)
                    results_list = list(results)
                    self.last_search_time = time.time()
                    break
                except Exception as search_error:
                    if "Ratelimit" in str(search_error) or "429" in str(search_error):
                        wait_time = (attempt + 1) * 5  # Exponential backoff
                        logger.warning(f"Hit rate limit, waiting {wait_time} seconds (attempt {attempt + 1})")
                        await asyncio.sleep(wait_time)
                        continue
                    logger.error(f"Search engine error: {str(search_error)}")
                    # Fall back to a simplified query on final attempt
                    if attempt == self.max_retries - 1:
                        try:
                            results = DDGS(headers=get_random_headers()).text(enhanced_query, max_results=max_results * 3)
                            results_list = list(results)
                            self.last_search_time = time.time()
                        except Exception as fallback_error:
                            logger.error(f"Fallback search failed: {str(fallback_error)}")
                            return knowledge
                    continue
                
            # Sort results to prioritize educational sites
            def domain_priority(url):
                domain = urlparse(url).netloc
                for i, edu_domain in enumerate(self.url_manager.trusted_domains.keys()):
                    if edu_domain in domain:
                        return i
                return len(self.url_manager.trusted_domains.keys())
                
            results_list.sort(key=lambda x: domain_priority(x['href']))
            
            processed_count = 0
            attempted_count = 0
                
            for result in results_list:
                if processed_count >= max_results or attempted_count >= max_results * 2:
                    break
                
                attempted_count += 1
                url = result['href']
                
                # Skip certain problematic URLs
                if self.url_manager.should_avoid_pattern(url):
                    logger.info(f"Skipping problematic URL: {url}")
                    continue

                skip, reason = self.url_manager.should_skip(url)
                if skip:
                    logger.info(f"Skipping {url}: {reason}")
                    continue
                
                try:
                    delay_range = self.url_manager.get_delay_for_domain(url)
                    await asyncio.sleep(random.uniform(*delay_range))
                        
                    # Skip paywall check for most educational sites to improve speed
                    should_check_paywall = not self.url_manager.is_trusted_domain(url)
                    
                    if should_check_paywall:
                        # Check for paywall, but be less strict
                        has_paywall = await self._is_paywall_present_with_playwright(url)
                        if has_paywall:
                            logger.info(f"Skipping {url}: Paywall detected")
                            self.url_manager.mark_as_bad(url)
                            continue
                        
                    # Try Playwright scraping
                    content = await self.scrape_page_async(url, query)
                    
                    if content:
                        if isinstance(content, ScrapedContent):
                            # Convert ScrapedContent to dict
                            content_dict = content.to_dict()
                            word_count = len(content.text.split())
                        elif isinstance(content, dict):
                            # Already a dictionary
                            content_dict = content
                            word_count = len(content.get('text', '').split())
                        else:
                            logger.info(f"Unexpected content type from {url}")
                            continue
                        
                        if word_count < 25:
                            logger.info(f"Skipping {url}: Content too short ({word_count} words)")
                            continue
                            
                        knowledge.append(content_dict)
                        self.url_manager.mark_as_scraped(url)
                        processed_count += 1
                        logger.info(f"Successfully scraped {url} ({word_count} words)")
                    else:
                        logger.info(f"No useful content found at {url}")
                        self.url_manager.mark_as_bad(url)
                        
                except Exception as e:
                    logger.error(f"Error processing {url}: {str(e)}")
                    self.url_manager.mark_as_bad(url)
                    continue
                    
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            
        return knowledge

    def search_and_scrape(self, query: str, level = "any level", max_results: int = 10) -> List[Dict]:
        """Synchronous wrapper for the async search_and_scrape method"""
        return asyncio.run(self.search_and_scrape_async(query, level, max_results))