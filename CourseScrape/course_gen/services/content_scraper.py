import os
import json
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from googlesearch import search

class ContentScraper:
    TRUSTED_SOURCES = [
        "wikipedia.org", "khanacademy.org", "edx.org",
        "coursera.org", "mit.edu", "stanford.edu",
        "openstax.org", "britannica.com"
    ]
    
    CACHE_DIR = "scraper_cache"
    
    def __init__(self):
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    async def fetch_content(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except Exception:
            return None
    
    async def scrape_topic(self, topic):
        cache_file = os.path.join(self.CACHE_DIR, f"{topic.replace(' ', '_')}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        query = f"{topic} site:" + " OR site:".join(self.TRUSTED_SOURCES)
        urls = self._google_search(query)
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_content(session, url) for url in urls]
            pages = await asyncio.gather(*tasks)
        
        scraped_data = []
        for url, page in zip(urls, pages):
            if page:
                cleaned = self._clean_page(page, url)
                if cleaned:
                    scraped_data.append(cleaned)
        
        with open(cache_file, 'w') as f:
            json.dump(scraped_data, f)
        
        return scraped_data
    
    def _google_search(self, query, num_results=5):
        return list(search(query, num_results=num_results))
    
    def _clean_page(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()
        
        main_content = soup.find('main') or soup.find('article') or soup
        content = []
        
        for element in main_content.find_all(['h1', 'h2', 'h3', 'p']):
            if element.name.startswith('h'):
                content.append(f"\n\n{element.get_text().upper()}\n")
            else:
                content.append(element.get_text())
        
        return {
            'url': url,
            'content': '\n'.join(content),
            'timestamp': datetime.utcnow().isoformat()
        }