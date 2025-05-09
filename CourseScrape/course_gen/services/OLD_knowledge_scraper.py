from course_gen.core.globals import (
    requests, logger, urljoin, BeautifulSoup, time, json, logging,
    re, Dict, random, List, os, DDGS, urllib, Optional, asyncio, lazy
) 

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("knowledge_scraper")

class KnowledgeScraper:
    """Advanced web scraper for educational content"""
    def __init__(self, scraped_urls_file: str = "scraped_urls.json", 
                 bad_urls_file: str = "bad_urls.json"):
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.scraped_urls_file = scraped_urls_file
        self.bad_urls_file = bad_urls_file
        self.scraped_urls = self._load_urls_file(self.scraped_urls_file)
        self.bad_urls = self._load_urls_file(self.bad_urls_file)
        
        self.sources = {
            "w3schools": {
                "base_url": "https://www.w3schools.com/",
                "topics": {
                    "python": {"url": "python/default.asp", "depth": 3},
                    "javascript": {"url": "js/default.asp", "depth": 3},
                    "sql": {"url": "sql/default.asp", "depth": 2}
                },
                "content_selectors": ["#main", ".w3-example"],
                "code_selectors": [".w3-code"],
                "avoid_urls": ["tryit.asp", "exercise.asp"]
            },
            "geeksforgeeks": {
                "base_url": "https://www.geeksforgeeks.org/",
                "topics": {
                    "python": {"url": "python-programming-language/", "depth": 3},
                    "data structures": {"url": "data-structures/", "depth": 2},
                    "algorithms": {"url": "fundamentals-of-algorithms/", "depth": 2}
                },
                "content_selectors": [".content", "article"],
                "code_selectors": [".code-container pre"],
                "avoid_urls": ["practice/", "quiz/"]
            },
            "realpython": {
                "base_url": "https://realpython.com/",
                "topics": {
                    "python": {"url": "tutorials/", "depth": 2},
                    "django": {"url": "django/", "depth": 2}
                },
                "content_selectors": [
                    "article#article-body",
                    ".article-body",
                    ".article-content"],
                "code_selectors": ["div.highlight pre", "pre code"],
                "avoid_urls": ["/courses/", "/quiz/"]
            }
        }

        # Trusted domains and their delay configurations
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
        self.default_delay = (2, 4)
        
        # Domains to avoid completely
        self.avoid_domains = [
            "pinterest", "facebook.com", "twitter.com", "instagram.com",
            "youtube.com", "medium.com", "quora.com", "linkedin.com",
            "reddit.com", "courses.com", "udemy.com", "coursera.org"
        ]
        
        # Paywall detection patterns
        self.paywall_patterns = [
            "subscribe", "subscription", "sign in to continue", 
            "continue reading", "create an account", "premium content",
            "paid member", "unlock", "free trial", "register to read",
            "remaining free articles", "remaining articles", "for full access",
            "join now", "become a member", "sign up today"
        ]
    
    def _load_urls_file(self, file_path: str) -> set:
        """Load URLs from JSON file into a set"""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except json.JSONDecodeError:
                logger.warning(f"Could not parse {file_path}. Creating a new file.")
                return set()
        return set()

    def _save_urls_file(self, file_path: str, urls: set):
        """Save URLs set to JSON file"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(list(urls), f, indent=2)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urllib.parse.urlparse(url)
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
    
    def _should_skip(self, url: str, domain: str, max_results: int) -> bool:
        """Checks if the URL should be skipped due to various conditions."""
        
        # Skip if domain should be avoided
        if self._should_avoid_domain(url):
            logger.info(f"⚠️ Skipping URL from avoided domain: {url}")
            return True
        
        # Skip if URL or its domain is already in bad_urls
        if url in self.bad_urls or domain in self.bad_urls:
            logger.info(f"⚠️ Skipping previously identified bad URL: {url}")
            return True
        
        # Skip if already scraped
        if url in self.scraped_urls:
            logger.info(f"⚠️ Skipping previously scraped URL: {url}")
            return True
        
        # Check for login/paywall
        if self._is_login_required(url):
            logger.info(f"⚠️ Skipping login-required site: {url}")
            self.bad_urls.add(domain)  # Add domain to bad URLs
            self._save_urls_file(self.bad_urls_file, self.bad_urls)
            return True

        if self._is_paywall_present(url):
            logger.info(f"⚠️ Skipping paywalled site: {url}")
            self.bad_urls.add(domain)  # Add domain to bad URLs
            self._save_urls_file(self.bad_urls_file, self.bad_urls)
            return True

        return False
    
    def _get_delay_for_domain(self, url: str) -> tuple:
        """Get appropriate delay range for a domain"""
        domain = self._extract_domain(url)
        for trusted, delay in self.trusted_domains.items():
            if trusted in domain:
                return delay
        return self.default_delay
            
    def search_and_scrape(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for content using DuckDuckGo and scrape results"""
        knowledge = []
        results = DDGS().text(query, max_results=max_results * 2)  # Fetch more results than needed to account for skipped URLs
        
        processed_count = 0
        for result in results:
            if processed_count >= max_results:
                break
                
            url = result['href']
            
            # Extract base domain for bad URL checking
            domain = self._extract_domain(url)
            
            if self._should_skip(url, domain, max_results):
                continue
            
            try:
                # Apply delay based on domain
                delay_range = self._get_delay_for_domain(url)
                time.sleep(random.uniform(*delay_range))
                
                if self._should_skip(url, domain, max_results):
                    continue
                
                # Scrape content
                content = self._scrape_page(url)
                if content and content["text"].strip():
                    knowledge.append({
                        "topic": query,
                        "title": result['title'] if result['title'] else content["title"],
                        "content": content["text"],
                        "code_examples": content["code"],
                        "source": "web_search",
                        "url": url,
                        "level": self._determine_level(content["text"], url)
                    })
                    self.scraped_urls.add(url)
                    self._save_urls_file(self.scraped_urls_file, self.scraped_urls)
                    processed_count += 1
                else:
                    logger.info(f"⚠️ No useful content found at: {url}")
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                self.bad_urls.add(domain)  # Add domain to bad URLs
                self._save_urls_file(self.bad_urls_file, self.bad_urls)
        
        return knowledge
    
    def _scrape_configured_sources(self) -> List[Dict]:
        """Scrape content from pre-configured sources"""
        knowledge = []
        
        for source_name, config in self.sources.items():
            for topic, topic_config in config["topics"].items():
                logger.info(f"Scraping {topic} from {source_name}")

                try:
                    base_url = urljoin(config["base_url"], topic_config["url"])
                    
                    delay_range = self._get_delay_for_domain(base_url)
                    time.sleep(random.uniform(*delay_range))
                    
                    response = self.session.get(base_url, timeout=15)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                    main_content = self._extract_content_with_selectors(soup, source_name)
                
                    if main_content and main_content.get("text"):
                        knowledge.append({
                            "topic": topic,
                            "title": self._get_title(soup) or f"{topic.capitalize()} Tutorial",
                            "content": main_content["text"],
                            "code_examples": main_content.get("code", []),
                            "source": source_name,
                            "url": base_url,
                            "level": self._determine_level(topic, source_name)
                        })
                        self.scraped_urls.add(base_url)
                    else:
                        logger.warning(f"No main content found at {base_url}")

                    # Find and process additional pages
                    page_links = self._find_links(soup, base_url, source_name)
                    for link in page_links[:topic_config["depth"]]:
                        try:
                            time.sleep(random.uniform(*self._get_delay_for_domain(link)))
                            
                            page_content = self._scrape_page(link)
                            if page_content and page_content.get("text"):
                                knowledge.append({
                                    "topic": topic,
                                    "title": page_content.get("title", "Untitled"),
                                    "content": page_content["text"],
                                    "code_examples": page_content.get("code", []),
                                    "source": source_name,
                                    "url": link,
                                    "level": self._determine_level(topic, source_name)
                                })
                                self.scraped_urls.add(link)
                        except Exception as e:
                            logger.error(f"Error scraping {link}: {str(e)}")

                except Exception as e:
                    logger.error(f"Error scraping {topic} from {source_name}: {str(e)}")
        
        return knowledge
    
    def _extract_content_with_selectors(self, soup: BeautifulSoup, source_name: str) -> Dict:
        """Source-specific content extraction using configured selectors"""
        config = self.sources.get(source_name, {})
        content = {"text": "", "code": []}
        
        # Try all content selectors
        for selector in config.get("content_selectors", []):
            elements = soup.select(selector)
            for element in elements:
                text = self._clean_text(element.get_text())
                if text and len(text) > 100:  # Minimum content threshold
                    content["text"] += f"\n{text}"
        
        # Try all code selectors
        for selector in config.get("code_selectors", []):
            code_blocks = soup.select(selector)
            for block in code_blocks:
                code = self._clean_code(block.get_text())
                if code and len(code.strip()) > 10:
                    content["code"].append(code)
        
        return content if content["text"] else None
    
    def _find_links(self, soup: BeautifulSoup, base_url: str, source_name: str) -> List[str]:
        """Find relevant links on a page"""
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.lower().startswith("javascript:"):
                continue

            full_url = urljoin(base_url, href)
            if not any(p in full_url for p in self.sources[source_name]["avoid_urls"]):
                links.add(full_url)

        return list(links)
    
    

    def _is_login_required(self, url: str) -> bool:
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

    def _is_paywall_present(self, url: str) -> bool:
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

    def _scrape_page(self, url: str) -> Dict:
        """Scrape content from a single page"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract title
            title = self._get_title(soup)
            
            # Extract main content
            main_content = self._extract_main_content(soup)
            if not main_content:
                return None
                
            # Clean text content
            text = self._clean_text(main_content.get_text())
            
            # Extract code examples
            code_examples = self._extract_code_examples(soup)
            
            return {
                "title": title, 
                "text": text, 
                "code": code_examples
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def _extract_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Extract main content from a page"""
        # Try common content selectors in order of likelihood
        content_selectors = [
            "main", "article", "#content", ".content", 
            "#main", ".main", "#article", ".article",
            ".post-content", ".entry-content", ".page-content",
            "#post-content", "#entry-content", "#page-content"
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content and len(content.get_text(strip=True)) > 200:  # Ensure there's meaningful content
                return content
        
        # Fallback: look for the largest div with substantial content
        divs = soup.find_all("div")
        largest_div = None
        max_length = 0
        
        for div in divs:
            text = div.get_text(strip=True)
            if len(text) > max_length:
                max_length = len(text)
                largest_div = div
        
        if largest_div and max_length > 500:  # Only return if meaningful content found
            return largest_div
            
        return None

    def _extract_code_examples(self, soup: BeautifulSoup) -> List[str]:
        """Extract code examples from a page"""
        code_examples = []
        
        # Look for code blocks in pre and code tags
        code_selectors = [
            "pre code", "pre", "code", ".code", "#code",
            ".highlight", ".syntax", ".codeblock", ".code-block",
            "[class*='code']", "[class*='syntax']", "[class*='highlight']"
        ]
        
        for selector in code_selectors:
            for code_block in soup.select(selector):
                code = self._clean_code(code_block.get_text())
                if code and len(code.strip()) > 10:  # Ignore very short snippets
                    code_examples.append(code)
        
        return code_examples

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
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

    def _clean_code(self, code: str) -> str:
        """Clean code examples"""
        # Remove shell prompts ($ or > at the beginning of lines)
        code = re.sub(r'^\s*[$>]\s*', '', code, flags=re.MULTILINE)
        
        # Remove extra line breaks and normalize whitespace
        code = re.sub(r'\s+\n', '\n', code)
        code = re.sub(r'\n\s+\n', '\n\n', code)
        
        return code.strip()

    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        if soup.title:
            title = soup.title.string
        else:
            # Try to find h1
            h1 = soup.find('h1')
            title = h1.get_text() if h1 else "Untitled"
            
        return self._clean_text(title)

    def _determine_level(self, content: str, url: str) -> str:
        """Determine content difficulty level based on content and URL"""
        # Check URL for level indicators
        domain = self._extract_domain(url)
        
        if "beginner" in url or "basics" in url or "tutorial" in url:
            return "beginner"
        elif "advanced" in url or "expert" in url:
            return "advanced"
        
        # Check for beginner-focused domains
        if any(domain in url for domain in ["w3schools.com", "tutorialspoint.com"]):
            return "beginner"
        
        # Check content for complexity indicators
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
        
# Subclass of KnowledgeScraper
class KnowledgeScraperWithPlaywright(KnowledgeScraper):
    """KnowledgeScraper with enhanced Playwright capabilities for handling JavaScript pages"""
    
    async def _is_paywall_present_with_playwright(self, url: str, timeout: int = 10) -> bool:
        """Check if a URL has a paywall using Playwright"""
        try:
            # Use synchronous Playwright
            return await self._is_paywall_present_async(url, timeout)
        except Exception as e:
            logger.error(f"Error checking paywall with Playwright for {url}: {str(e)}")
            return True  # Skip if error occurs
    
    async def _is_paywall_present_async(self, url: str, timeout: int = 10) -> bool:
        """Check if a URL has a paywall using Playwright (async implementation)"""
        try:
            playwright = lazy.playwright_async
            async with await playwright() as p:
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
                page.set_default_timeout(timeout * 1000)
                
                # Navigate to the URL
                response = await page.goto(url, wait_until="networkidle")
                await page.wait_for_timeout(2000)  # Wait for dynamic content
                
                # Handle cookie popups
                await self._handle_cookie_popups_async(page)
                
                # Check HTTP status
                if response.status in [401, 402, 403]:
                    await browser.close()
                    return True
                    
                # Check for paywall indicators in the page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text().lower()
                
                # Check for paywall-related text
                paywall_count = sum(text.count(keyword) for keyword in self.paywall_patterns)
                
                # Check for modal/overlay elements
                modal_selectors = [
                    ".paywall", ".modal", ".popup", ".subscription", ".subscribe",
                    "[id*='paywall']", "[id*='modal']", "[id*='popup']", 
                    "[id*='subscribe']", "[class*='paywall']", "[class*='subscribe']"
                ]
                
                has_modal = False
                for selector in modal_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements:
                            if await element.is_visible():
                                has_modal = True
                                break
                        if has_modal:
                            break
                    except:
                        continue
                
                # Check for floating elements that might be paywalls
                floating_elements = await page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('div, section, aside');
                        return Array.from(elements).filter(el => {
                            const style = window.getComputedStyle(el);
                            return (style.position === 'fixed' || style.position === 'absolute') && 
                                parseInt(style.zIndex || 0) > 10 &&
                                el.offsetWidth > window.innerWidth * 0.5 &&
                                el.offsetHeight > window.innerHeight * 0.3;
                        }).length > 0;
                    }
                """)
                
                await browser.close()
                return has_modal or floating_elements or paywall_count > 3
                
        except Exception as e:
            logger.error(f"Error in async paywall check for {url}: {str(e)}")
            return True  # Skip if error occurs
    
    async def _handle_cookie_popups_async(self, page) -> bool:
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
    
    async def _scrape_page_with_playwright(self, url: str) -> Optional[Dict]:
        """Scrape content from a JavaScript-heavy page using Playwright"""
        try:
            return await self._scrape_page_async(url)
        except Exception as e:
            logger.error(f"Error scraping with Playwright for {url}: {str(e)}")
            return None
    
    async def _scrape_page_async(self, url: str) -> Optional[Dict]:
        """Scrape content from a JavaScript-heavy page using Playwright (async)"""
        try:
            playwright = lazy.playwright_async
            async with await playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent=self.headers["User-Agent"]
                )
                
                # Add stealth script
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                """)
                
                page = await context.new_page()
                page.set_default_timeout(15000)
                
                # Navigate to the URL
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_timeout(2000)  # Wait for dynamic content
                
                # Handle cookie popups
                await self._handle_cookie_popups_async(page)
                
                # Get page title
                title = await page.title()
                
                # Get page content
                content = await page.content()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, "html.parser")
                
                # Extract main content
                main_content = self._extract_main_content(soup)
                if not main_content:
                    await browser.close()
                    return None
                
                # Clean text
                text = self._clean_text(main_content.get_text())
                
                # Extract code examples
                code_examples = self._extract_code_examples(soup)
                
                await browser.close()
                return {
                    "title": title, 
                    "text": text, 
                    "code": code_examples
                }
        except Exception as e:
            logger.error(f"Error in async page scraping for {url}: {str(e)}")
            return None
    
    async def search_and_scrape(self, query: str, max_results: int = 10) -> List[Dict]:
        """Enhanced search and scrape using both regular requests and Playwright"""
        knowledge = []
        results = DDGS().text(query, max_results=max_results * 2)  # Fetch extra results
        
        processed_count = 0
        for result in results:
            if processed_count >= max_results:
                break
                
            url = result['href']
            domain = self._extract_domain(url)
            
            if self._should_skip(url, domain, max_results):
                continue
            
            try:
                # Apply delay based on domain
                delay_range = self._get_delay_for_domain(url)
                await asyncio.sleep(random.uniform(*delay_range))
                
                # First try standard requests approach
                content = None
                
                # Try standard request first for speed
                if not self._is_login_required(url) and not self._is_paywall_present(url):
                    content = self._scrape_page(url)
                
                # If standard request fails, try with Playwright for JS-heavy sites
                if not content or not content.get("text"):
                    logger.info(f"🔄 Trying Playwright for: {url}")
                    
                    # Check for paywall with Playwright
                    if await self._is_paywall_present_with_playwright(url):
                        logger.info(f"⚠️ Playwright detected paywall at: {url}")
                        self.bad_urls.add(domain)
                        self._save_urls_file(self.bad_urls_file, self.bad_urls)
                        continue
                    
                    # Try scraping with Playwright
                    content = await self._scrape_page_with_playwright(url)
                
                # Process content if found
                if content and content["text"].strip():
                    knowledge.append({
                        "topic": query,
                        "title": result['title'] if result['title'] else content["title"],
                        "content": content["text"],
                        "code_examples": content["code"],
                        "source": "web_search",
                        "url": url,
                        "level": self._determine_level(content["text"], url)
                    })
                    self.scraped_urls.add(url)
                    self._save_urls_file(self.scraped_urls_file, self.scraped_urls)
                    processed_count += 1
                    logger.info(f"✅ Successfully scraped: {url}")
                else:
                    logger.info(f"⚠️ No useful content found at: {url}")
                    self.bad_urls.add(domain)
                    self._save_urls_file(self.bad_urls_file, self.bad_urls)
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                self.bad_urls.add(domain)
                self._save_urls_file(self.bad_urls_file, self.bad_urls)
        
        return knowledge