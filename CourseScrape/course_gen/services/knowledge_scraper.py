from course_gen.core.globals import (
    logger, urljoin, urlparse, BeautifulSoup, time, logging, random, requests,
    random, re, unicodedata, sys, Dict, List, Set, Tuple, Optional, os, DDGS, 
    asyncio, hashlib, extract
)

from playwright.async_api import async_playwright, Browser, BrowserContext
from course_gen.core import (
    USER_AGENTS, BASE_HEADERS, SKIP_PATTERNS, AVOID_DOMAINS, TRUSTED_DOMAINS, 
    CONSENT_SELECTORS, PAGINATION_SELECTORS, CODE_SELECTORS, NON_EDUCATIONAL_TEXT,
    PAYWALL_PATTERNS, BASIC_INDICATORS, ADVANCED_INDICATORS, PROMO_PATTERNS, BRAND_NAMES
)
from course_gen.utils.file_manager import FileManager
from course_gen.services.knowledge_enhancer import KnowledgeEnhancer

# Configure logging
logger = logging.getLogger("knowledge_scraper")

# Windows fixes for python3.11+ and playwright 
if sys.platform == "win32":
    # Required for Playwright subprocess handling
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Disable Windows-specific memory protections
    os.environ['PLAYWRIGHT_DISABLE_ISOLATED_HEAP'] = '1'
    os.environ['PLAYWRIGHT_NO_PROXY'] = '1'

# Global headers function
def get_random_headers():
        """Return headers with a random user agent"""
        return {
            **BASE_HEADERS,
            "User-Agent": random.choice(USER_AGENTS)
        }


class URLManager:
    """Manages URL processing, storage and retrieval"""
    @property
    def bad_urls(self) -> Set[str]:
        return self.get_bad_urls()

    @property
    def scraped_urls(self) -> Set[str]:
        return self.get_scraped_urls()
    
    def __init__(self, scraped_urls_file: str = "scraped_urls.json", 
                 bad_urls_file: str = "bad_urls.json"):
        self.scraped_urls_file = scraped_urls_file
        self.bad_urls_file = bad_urls_file
        self._scraped_urls_cache = None
        self._bad_urls_cache = None
        # Cache URL results to avoid redundant processing
        self.url_results_cache = {}
        # Configure trusted domains and their delay configurations
        self.trusted_domains = TRUSTED_DOMAINS
        # Domains to avoid completely
        self.avoid_domains = AVOID_DOMAINS
        # Patterns in urls to avoid
        self.skip_patterns = SKIP_PATTERNS
        # Level indicators
        self.advanced_indicators = ADVANCED_INDICATORS
        self.basic_indicators = BASIC_INDICATORS
        # Default delay for other sites
        self.default_delay = (5, 10)
        
    
    def _load_urls_file(self, file_path: str, cache_attr: str) -> Set[str]:
        """Load URLs from JSON file once and cache."""
        if getattr(self, cache_attr) is None:
            try:
                data = FileManager.load_json(file_path)
                setattr(self, cache_attr, set(data) if isinstance(data, list) else set())
            except Exception:
                logger.warning(f"Falling back to empty set for {file_path}")
                setattr(self, cache_attr, set())
        return getattr(self, cache_attr)

    def get_scraped_urls(self):
        return self._load_urls_file(self.scraped_urls_file, "_scraped_urls_cache")

    def get_bad_urls(self):
        return self._load_urls_file(self.bad_urls_file, "_bad_urls_cache")
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL safely"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return ""
    
    def _is_trusted_domain(self, url: str) -> bool:
        """Check if URL belongs to a trusted domain"""
        domain = self._extract_domain(url)
        return any(trusted in domain for trusted in self.trusted_domains.keys())
    
    def _should_avoid_domain(self, url: str) -> bool:
        """Check if URL belongs to a domain that should be avoided"""
        domain = self._extract_domain(url)
        return any(avoid in domain for avoid in self.avoid_domains)
            
    def _should_avoid_pattern(self, url: str) -> bool:
        if any(pattern in url for pattern in self.skip_patterns):
            return False
    
    def _get_delay_for_domain(self, url: str) -> Tuple[float, float]:
        """Get appropriate delay range for a domain"""
        domain = self._extract_domain(url)
        for trusted, delay in self.trusted_domains.items():
            if trusted in domain:
                return delay
        return self.default_delay
    
    def _should_skip(self, url: str) -> Tuple[bool, str]:
        """Check if URL should be skipped and return reason if so"""
        domain = self._extract_domain(url)
        
        # Skip if domain should be avoided
        if self._should_avoid_domain(url):
            return True, "Avoided domain"
        
        # Skip if URL or its domain is already in bad_urls
        if (url in self.bad_urls or domain in self.bad_urls) and not self._is_trusted_domain(url):
            return True, "Bad URL"
        
        # Skip if already scraped
        if url in self.scraped_urls:
            return True, "Already scraped"
            
        return False, ""
    
    def _mark_as_scraped(self, url: str) -> None:
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
    
    def _mark_as_bad(self, url: str) -> None:
        """Mark URL or domain as bad"""
        try:
            domain = self._extract_domain(url)
            self.bad_urls.add(domain)
            
            if not isinstance(self.bad_urls_file, (str, os.PathLike)):
                logger.error(f"Invalid output_file: {self.bad_urls_file}")
                raise ValueError("Bad urls output path must be a string")
            
            FileManager.save_json(self.bad_urls, self.bad_urls_file)
        except Exception as e:
            logger.error(f"Bad urls save failed: {e}")
            raise

    def _find_links(self, soup: BeautifulSoup, base_url: str, avoid_patterns: List[str]) -> List[str]:
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

    def _determine_level(self, content: str, url: str) -> str:
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

class Detector:
    """Standard detector using regular HTTP requests"""
    def __init__(self):
        self.url_manager = URLManager()
        # Paywall detection patterns
        self.paywall_patterns = PAYWALL_PATTERNS
        self.promo_keywords = PROMO_PATTERNS
        self.brand_names = BRAND_NAMES
        self.headers = get_random_headers()
    
    # def _is_promotional_or_low_quality(self, text: str) -> bool:
    #     lowered = text.lower()

    #     promo_hits = sum(kw in lowered for kw in self.promo_keywords)
    #     brand_hits = sum(lowered.count(brand) for brand in self.brand_names)

    #     # Check if content is mostly links or too short
    #     is_mostly_links = lowered.count("http") > 5 or lowered.count("click") > 3
    #     is_repetitive = brand_hits > 5
    #     too_short = len(text.split()) < 100

    #     # If too many hits or too short but marketing-heavy
    #     return promo_hits >= 5 or is_mostly_links or is_repetitive or (too_short and promo_hits >= 1)
        
    def is_login_required(self, url: str) -> bool:
        """Check if a URL requires login"""
        if self.url_manager._is_trusted_domain(url):
            return False
        else: 
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
        if self.url_manager._is_trusted_domain(url):
            return False
        else:
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

class PlaywrightWebScraper:
    """Web scraper using Playwright, DDGS, and Trafilatura"""
    
    def __init__(self):
        self.knowledge_enhancer = KnowledgeEnhancer()
        self.url_manager = URLManager()
        self.detector = Detector()
        self.consent_selectors = CONSENT_SELECTORS
        self.pagination_selectors = PAGINATION_SELECTORS
        self.code_selectors = CODE_SELECTORS
        self.non_educational_text = NON_EDUCATIONAL_TEXT
        self.visited_urls = set()  # Track visited URLs
        self.current_domain = None  # Track current domain being scraped
        self.headers = get_random_headers()
        self.last_search_time = 0
        self.search_delay = (3, 6)  # Random delay between 3-6 seconds
        self.max_retries = 3
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.visited_urls: Set[str] = set()
        self.content_hashes: Set[str] = set()  # Detect duplicate content
        self.semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        
    async def __aenter__(self):
        """Context manager for browser lifecycle"""
        await self._ensure_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._cleanup_browser()

    async def _ensure_browser(self):
        """Initialize browser if not already done"""
        if not self.browser:
            p = await async_playwright().start()
            self.browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800},
            )

    async def _cleanup_browser(self):
        """Clean up browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def search_and_scrape(self, query: str, thinking_mode, level: str = "any level", max_results: int = 10) -> List[Dict]:
        """Optimized version with concurrent processing"""
        results = await self._search(query, level, max_results=max_results)
        
        # Filter URLs upfront
        valid_urls = []
        for result in results[:max_results]:
            url = result['href']
            should_skip, reason = self.url_manager._should_skip(url)
            if not should_skip and not self.detector.is_login_required(url) and not self.detector.is_paywall_present(url):
                valid_urls.append((url, result))
            else:
                logger.info(f"Skipping {url}: {reason}")

        # Process URLs concurrently with rate limiting
        tasks = []
        for url, result in valid_urls:
            task = self._scrape_single_url(url, result, thinking_mode)
            tasks.append(task)

        # Execute with controlled concurrency
        scraped_data = []
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):  # Successful scraping
                scraped_data.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping failed: {result}")

        return scraped_data
    
    async def _search(self, query: str, level: str = "any level", max_results: int = 10) -> List[Dict]:
        # Enforce rate limit
        elapsed = time.time() - self.last_search_time
        delay = random.uniform(*self.search_delay)
        if elapsed < delay:
            await asyncio.sleep(delay - elapsed)

        self.headers = get_random_headers()  # Shuffle headers

        try:
            # Apply headers to DDGS request if needed
            enhanced_query = f"{query} for {level} course OR lessons OR tutorial"
            
            results = DDGS().text(enhanced_query, max_results=max_results)
            self.last_search_time = time.time()
            
            # Filter results using URLManager
            filtered_results = []
            for result in results:
                url = result.get('href', '')
                should_skip, reason = self.url_manager._should_skip(url)
                if not should_skip:
                    filtered_results.append(result)
                else:
                    logger.info(f"Filtered out {url}: {reason}")
            
            return filtered_results
        
        except Exception as e:
            logger.error(f"search error: {str(e)}")
            return []

    async def _scrape_single_url(self, url: str, result: dict, thinking_mode) -> Optional[Dict]:
        """Scrape a single URL with semaphore protection"""
        async with self.semaphore:
            # Apply domain-specific delay
            delay_range = self.url_manager._get_delay_for_domain(url)
            await asyncio.sleep(random.uniform(*delay_range))
            
            logger.info(f"Scraping: {url}")
            
            try:
                content = await self._scrape_website(url)
                raw_text = content["text"]
                
                if not raw_text.strip():
                    logger.info(f"Skipping {url}: Empty content.")
                    return None

                # Check for duplicate content
                content_hash = hashlib.md5(raw_text.encode()).hexdigest()
                if content_hash in self.content_hashes:
                    logger.info(f"Skipping {url}: Duplicate content detected")
                    return None
                self.content_hashes.add(content_hash)

                # Process content
                chunks = self.split_dom_content(raw_text)
                
                # Batch AI processing to reduce API calls
                ai_tasks = {
                    'classification': chunks[:1],
                    'topics': chunks[:1], 
                    'difficulty': chunks[:1],
                    'educational_content': chunks
                }
                
                ai_results = {}
                for task_name, task_chunks in ai_tasks.items():
                    ai_results[task_name] = self.knowledge_enhancer.parse_with_model(
                        task_chunks, task=task_name, thinking_mode=thinking_mode
                    )

                # Validate classification
                if ai_results['classification'].strip().lower() != "true":
                    logger.info(f"Skipping {url}: Classified as '{ai_results['classification']}'")
                    self.url_manager._mark_as_bad(url)
                    return None

                # Process results
                topics = [t.strip() for t in ai_results['topics'].split(",") if t.strip()]
                
                difficulty = ai_results['difficulty'].strip().lower()
                if difficulty not in ["beginner", "intermediate", "advanced"]:
                    difficulty = self.url_manager._determine_level(ai_results['educational_content'], url)

                code_snippets = self._extract_code_content(content["raw_html"])
                self.url_manager._mark_as_scraped(url)

                return {
                    "title": content["title"] or result.get('title', 'No title'),
                    "url": url,
                    "topics": topics,
                    "level": difficulty,
                    "cleaned_text": ai_results['educational_content'],
                    "code_snippets": code_snippets
                }

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                self.url_manager._mark_as_bad(url)
                return None

    async def _scrape_website(self, website: str, with_pagination: bool = True) -> Dict:
        """Optimized website scraping with reused browser"""
        should_skip, reason = self.url_manager._should_skip(website)
        if should_skip:
            raise Exception(f"URL skipped: {reason}")

        await self._ensure_browser()
        
        # Create new page for this URL
        page = await self.context.new_page()
        
        try:
            # Set headers and timeouts
            is_trusted = self.url_manager._is_trusted_domain(website)
            timeout = 15000 if is_trusted else 30000
            page.set_default_timeout(timeout)
            
            headers = get_random_headers()
            await page.set_extra_http_headers(headers)
            
            await page.goto(website, wait_until="domcontentloaded", timeout=timeout)
            await page.wait_for_timeout(2000)  # Reduced wait time
            await self._handle_cookie_popups(page)

            # Get HTML once
            html = await page.content()
            
            # Extract content once using trafilatura
            readable_text = extract(html, include_comments=False, include_tables=True, 
                                 no_fallback=True, favor_precision=True)
            
            combined_text = self._clean_educational_text(readable_text or "")
            
            # Handle pagination if enabled and content looks incomplete
            if with_pagination and self._should_check_pagination(combined_text):
                paginated_texts = await self._scrape_with_pagination(page, website)
                if paginated_texts:
                    combined_text = "\n\n".join([combined_text] + paginated_texts)

            return {
                "title": self._extract_title_from_html(html),
                "raw_html": html,
                "text": combined_text
            }

        finally:
            await page.close()

    def _should_check_pagination(self, text: str) -> bool:
        """Determine if pagination should be checked based on content"""
        # Skip pagination for very short or very long content
        word_count = len(text.split())
        return 100 < word_count < 5000

    async def _scrape_with_pagination(self, page, base_url: str, max_pages: int = 5) -> List[str]:
        """Optimized pagination with limits and duplicate detection"""
        texts = []
        pages_scraped = 0
        
        for selector in self.pagination_selectors:
            if pages_scraped >= max_pages:
                break
                
            try:
                while pages_scraped < max_pages:
                    next_link = await page.query_selector(selector)
                    if not next_link or not await next_link.is_visible():
                        break
                        
                    next_href = await next_link.get_attribute("href")
                    if not next_href or next_href.startswith("javascript"):
                        break
                        
                    next_url = urljoin(base_url, next_href)
                    
                    # Check if we've already visited this URL
                    if next_url in self.visited_urls:
                        break
                    self.visited_urls.add(next_url)
                    
                    # Check if URL should be skipped
                    should_skip, reason = self.url_manager._should_skip(next_url)
                    if should_skip:
                        break
                    
                    # Navigate to next page
                    delay_range = self.url_manager._get_delay_for_domain(next_url)
                    await asyncio.sleep(random.uniform(*delay_range))
                    
                    await page.goto(next_url, wait_until="domcontentloaded")
                    await asyncio.sleep(1)
                    
                    # Extract content
                    html = await page.content()
                    readable_text = extract(html, include_comments=False, include_tables=True,
                                          no_fallback=True, favor_precision=True)
                    
                    if readable_text:
                        cleaned_text = self._clean_educational_text(readable_text)
                        
                        # Check for duplicate content
                        content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
                        if content_hash not in self.content_hashes:
                            texts.append(cleaned_text)
                            self.content_hashes.add(content_hash)
                            pages_scraped += 1
                        else:
                            # Duplicate content found, stop pagination
                            break
                    else:
                        break
                        
            except Exception as e:
                logger.error(f"Pagination error: {e}")
                break
                
        return texts
    
    def _extract_code_content(self, html_content: str) -> List[str]:
        soup = BeautifulSoup(html_content, "html.parser")
        code_snippets = []
        
        for selector in self.code_selectors:
            elements = soup.select(selector)
            if elements:
                code_snippets = [el.get_text().strip() for el in elements if el.get_text().strip()]
                break
        
        return code_snippets

    def split_dom_content(self, dom_content: str, max_length: int = 6000) -> List[str]:
        """Split DOM content into chunks"""
        return [
            dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
        ]
    
    def _fallback_extract_body_content(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        body = soup.body
        return str(body) if body else ""

    def _fallback_clean_body_content(self, body_content: str) -> str:
        soup = BeautifulSoup(body_content, "html.parser")
        for tag in soup(["script", "style"]):
            tag.extract()
        cleaned = soup.get_text(separator="\n")
        return "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())
    
    def _extract_title_from_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        if soup.title:
            return soup.title.string.strip()
        return "No title found"

    def _clean_educational_text(self, text: str) -> str:
        lines = text.splitlines()
        cleaned_lines = [
            line.strip() for line in lines
            if line.strip() and not any(bad in line.lower() for bad in self.non_educational_text)
        ]
        clean_text = "\n".join(cleaned_lines)
        # Normalize text
        clean_text = unicodedata.normalize("NFKC", clean_text)
        # Remove non-ASCII or strange characters (optional)
        clean_text = re.sub(r'[^\x00-\x7F]+', ' ', clean_text)
        # Collapse multiple spaces or newlines
        clean_text = re.sub(r'[ \t]+', ' ', clean_text)
        clean_text = re.sub(r'\n\s*\n+', '\n\n', clean_text)
        
        return clean_text.strip()

    async def _handle_cookie_popups(self, page) -> bool:
        for selector in self.consent_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    await page.wait_for_timeout(1000)
                    return True
            except Exception:
                continue
        return False
        

    # Synchronious wrappers
    def scrape_website_sync(self, website: str) -> str:
        return asyncio.run(self._scrape_website(website))

    def search_sync(self, query: str, max_results: int = 10) -> List[Dict]:
        return asyncio.run(self._search(query, max_results))

    def search_and_scrape_sync(self, query: str, thinking_mode, level: str = "any level", max_results: int = 10) -> List[Dict]:
        return asyncio.run(self.search_and_scrape(query, thinking_mode, level, max_results))