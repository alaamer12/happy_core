"""Real-world example of using Asyn for web scraping."""

import asyncio
import aiohttp
import logging
import sys
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Dict, List, Set
from true.asyn import Asyn, TaskState

# Create separate loggers
diagnostic_logger = logging.getLogger('diagnostic')
progress_logger = logging.getLogger('progress')

@dataclass
class PageResult:
    """Results from scraping a single page."""
    url: str
    title: str
    links: List[str]
    success: bool
    error: str = None

class WebScraper:
    """Asynchronous web scraper using Asyn for task management."""
    
    def __init__(self, max_depth: int = 2, max_pages: int = 10):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        self.results: Dict[str, PageResult] = {}
        self._running = True
        
        # Common headers to avoid 403 errors
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def scrape_page(self, url: str, depth: int, session: aiohttp.ClientSession) -> PageResult:
        """Scrape a single page and extract links."""
        try:
            # Skip if we've reached limits
            if depth > self.max_depth or len(self.visited) >= self.max_pages:
                return None
            
            # Skip if already visited
            if url in self.visited:
                return None
            
            self.visited.add(url)
            
            # Only scrape python.org domain
            if not url.startswith('https://www.python.org'):
                return None
            
            # Fetch page with timeout and headers
            async with session.get(url, headers=self.headers, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                html = await response.text()
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else "No title"
            
            # Extract links
            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = f"https://www.python.org{href}"
                    # Only include python.org links
                    if href.startswith('https://www.python.org'):
                        links.append(href)
            
            progress_logger.info(f"Scraped {url}")
            progress_logger.info(f"Title: {title}")
            progress_logger.info(f"Found {len(links)} links")
            return PageResult(url, title, links, True)
            
        except asyncio.TimeoutError:
            diagnostic_logger.error(f"Timeout scraping {url}")
            return PageResult(url, "", [], False, "Request timeout")
        except aiohttp.ClientError as e:
            diagnostic_logger.error(f"Network error scraping {url}: {e}")
            return PageResult(url, "", [], False, str(e))
        except Exception as e:
            diagnostic_logger.error(f"Error scraping {url}: {e}")
            return PageResult(url, "", [], False, str(e))

    async def process_page(self, url: str, depth: int, session: aiohttp.ClientSession, 
                         task: Asyn) -> None:
        """Process a page and create tasks for its links."""
        result = await self.scrape_page(url, depth, session)
        if not result:
            return
        
        self.results[url] = result
        
        # Create tasks for links
        if result.success and depth < self.max_depth:
            for link in result.links:
                if link not in self.visited and len(self.visited) < self.max_pages:
                    # Create subtask for each link
                    async with await task.create_task(
                        self.process_page(link, depth + 1, session, None),
                        name=f"page_{len(self.visited)}"
                    ) as subtask:
                        await subtask.run(
                            self.process_page(link, depth + 1, session, subtask)
                        )

    async def scrape_site(self, start_url: str) -> Dict[str, PageResult]:
        """Start scraping from a URL."""
        print(f"\n=== Starting Web Scraper ===")
        print(f"Start URL: {start_url}")
        print(f"Max Depth: {self.max_depth}")
        print(f"Max Pages: {self.max_pages}\n")
        
        # Create session with custom timeout
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=5)  # Limit concurrent connections
        
        async with Asyn(name="scraper") as manager:
            async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.headers
            ) as session:
                # Start with the first page
                async with await manager.create_task(
                    self.process_page(start_url, 0, session, None),
                    name="root_page"
                ) as root_task:
                    await root_task.run(
                        self.process_page(start_url, 0, session, root_task)
                    )
        
        return self.results

async def main():
    """Run the web scraper example."""
    scraper = WebScraper(max_depth=2, max_pages=5)
    start_url = "https://www.python.org"
    
    try:
        results = await scraper.scrape_site(start_url)
        
        # Print results
        print("\n=== Scraping Results ===")
        for url, result in results.items():
            print(f"\nPage: {url}")
            print(f"Title: {result.title}")
            print(f"Success: {result.success}")
            if not result.success:
                print(f"Error: {result.error}")
            else:
                print(f"Links found: {len(result.links)}")
                
    except Exception as e:
        diagnostic_logger.error(f"Scraper error: {e}")

if __name__ == "__main__":
    # Configure diagnostic logging to stderr
    diagnostic_handler = logging.StreamHandler(sys.stderr)
    diagnostic_handler.setFormatter(logging.Formatter(
        '%(levelname)s:%(name)s: %(message)s'
    ))
    diagnostic_logger.addHandler(diagnostic_handler)
    diagnostic_logger.setLevel(logging.WARNING)
    
    # Configure progress logging to stdout
    progress_handler = logging.StreamHandler(sys.stdout)
    progress_handler.setFormatter(logging.Formatter(
        '%(message)s'  # Simpler format for progress
    ))
    progress_logger.addHandler(progress_handler)
    progress_logger.setLevel(logging.INFO)
    
    # Run the scraper
    asyncio.run(main())
