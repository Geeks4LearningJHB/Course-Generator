from course_gen.core.globals import (
    requests, logger, urljoin, BeautifulSoup, time, json, 
    re, Dict, random, List
) 

class KnowledgeScraper:
    """Advanced web scraper for educational content"""
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Configured sources with updated selectors
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
                "content_selectors": [".article-body"],
                "code_selectors": [".highlight pre"],
                "avoid_urls": ["/courses/", "/quiz/"]
            }
        }

        self.delays = {
            "w3schools": (1, 2),
            "geeksforgeeks": (2, 3),
            "realpython": (2, 4)
        }

    def scrape_knowledge_base(self, output_file: str = "knowledge_base.json") -> List[Dict]:
        """Scrape educational content from configured sources"""
        knowledge = []

        for source_name, config in self.sources.items():
            for topic, topic_config in config["topics"].items():
                logger.info(f"Scraping {topic} from {source_name}")

                try:
                    base_url = urljoin(config["base_url"], topic_config["url"])
                    response = self.session.get(base_url, timeout=15)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, "html.parser")

                    # Process main page
                    main_content = self._extract_content(soup, source_name)
                    if main_content:
                        knowledge.append({
                            "topic": topic,
                            "title": self._get_title(soup),
                            "content": main_content["text"],
                            "code_examples": main_content["code"],
                            "source": source_name,
                            "url": base_url,
                            "level": self._determine_level(topic, source_name)
                        })

                    # Find and process additional pages
                    page_links = self._find_links(soup, base_url, source_name)
                    for link in page_links[:topic_config["depth"]]:
                        time.sleep(random.uniform(*self.delays[source_name]))

                        try:
                            page_content = self._scrape_page(link, source_name)
                            if page_content:
                                knowledge.append({
                                    "topic": topic,
                                    "title": page_content["title"],
                                    "content": page_content["text"],
                                    "code_examples": page_content["code"],
                                    "source": source_name,
                                    "url": link,
                                    "level": self._determine_level(topic, source_name)
                                })
                        except Exception as e:
                            logger.error(f"Error scraping {link}: {str(e)}")

                except Exception as e:
                    logger.error(f"Error scraping {topic} from {source_name}: {str(e)}")

        # Save the knowledge base
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)

        logger.info(f"Scraped {len(knowledge)} knowledge items")
        return knowledge

    def _extract_content(self, soup: BeautifulSoup, source_name: str) -> Dict:
        """Extract content from BeautifulSoup object"""
        content_selectors = self.sources[source_name]["content_selectors"]
        code_selectors = self.sources[source_name]["code_selectors"]

        # Find main content
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            return None

        # Clean text content
        text = self._clean_text(main_content.get_text())

        # Extract code examples
        code_examples = []
        for selector in code_selectors:
            for code_block in soup.select(selector):
                code = self._clean_code(code_block.get_text())
                if code:
                    code_examples.append(code)

        return {"text": text, "code": code_examples, "title": self._get_title(soup)}

    def _scrape_page(self, url: str, source_name: str) -> Dict:
        """Scrape content from a single page"""
        if any(p in url for p in self.sources[source_name]["avoid_urls"]):
            return None

        response = self.session.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        return self._extract_content(soup, source_name)

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

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'\[\d+\]', '', text)  # Remove citations
        return text

    def _clean_code(self, code: str) -> str:
        """Clean code examples"""
        code = re.sub(r'^\s*\$\s*', '', code, flags=re.MULTILINE)  # Remove shell prompts
        code = re.sub(r'\s+\n', '\n', code)
        return code.strip()

    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title = soup.title.string if soup.title else "Untitled"
        return self._clean_text(title)

    def _determine_level(self, topic: str, source: str) -> str:
        """Determine content difficulty level"""
        if source == "w3schools":
            return "beginner"
        elif "data structure" in topic.lower() or "algorithm" in topic.lower():
            return "advanced"
        return "intermediate"