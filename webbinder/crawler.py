import asyncio
import aiohttp
import logging
from typing import Set, Dict, List, Optional
from collections import deque
from .parser import extract_links

logger = logging.getLogger("webbinder.crawler")

class AsyncCrawler:
    def __init__(self, start_url: str, max_urls: int = 100, depth: int = 1, 
                 skip_urls: List[str] = None, rate_limit: float = 0.5, concurrency: int = 5):
        self.start_url = start_url
        self.max_urls = max_urls
        self.depth = depth
        self.skip_urls = skip_urls or []
        self.rate_limit = rate_limit
        self.concurrency = concurrency
        
        self.processed_urls: Set[str] = set()
        self.url_cache: Dict[str, str] = {}
        self.semaphore = asyncio.Semaphore(concurrency)

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetches URL content with retry logic."""
        if url in self.url_cache:
            return self.url_cache[url]

        async with self.semaphore:
            # Respect rate limit as a delay before fetch (simple throttling)
            if self.rate_limit > 0:
                await asyncio.sleep(self.rate_limit)
                
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                }
                logger.debug(f"Fetching: {url}")
                async with session.get(url, headers=headers, timeout=30) as response:
                    response.raise_for_status()
                    content = await response.text()
                    self.url_cache[url] = content
                    return content
            except Exception as e:
                logger.warning(f"Failed to fetch {url}: {e!r}") # Use !r to show repr(e) even if str(e) is empty
                return None

    def _should_skip(self, url: str) -> bool:
        """Checks if URL should be skipped based on patterns."""
        for pattern in self.skip_urls:
            if pattern in url:
                return True
        return False

    async def _process_url(self, session: aiohttp.ClientSession, url: str, current_depth: int, queue: deque):
        if len(self.processed_urls) >= self.max_urls:
            return

        if url in self.processed_urls or self._should_skip(url):
            return

        self.processed_urls.add(url)
        content = await self._fetch(session, url)
        
        if content and current_depth > 0:
            links = extract_links(content, url)
            for link in links:
                if link not in self.processed_urls and not self._should_skip(link):
                    queue.append((link, current_depth - 1))

    async def run(self):
        """Starts the crawling process."""
        logger.info(f"Starting crawl at {self.start_url} (Max URLs: {self.max_urls}, Depth: {self.depth})")
        
        async with aiohttp.ClientSession() as session:
            # Queue stores (url, depth_remaining)
            queue = deque([(self.start_url, self.depth)])
            
            # Since we want to respect max_urls strictly and maybe doing BFS, 
            # we can process queue.
            # However, simpler approach for async BFS is:
            # 1. Fetch current batch
            # 2. Extract links
            # 3. Add to next batch
            
            # But with a shared queue and workers it's complex. 
            # Let's stick to a simpler iterative approach for now to ensure we control the loop/max_urls easily.
            # While queue is not empty and count < max_urls:
            
            while queue and len(self.processed_urls) < self.max_urls:
                # We can run a batch of tasks from the queue
                # But to keep dependencies (depth) correct, we usually just take one.
                # To speed up, we can take N items.
                
                batch_size = min(self.concurrency, len(queue))
                tasks = []
                for _ in range(batch_size):
                    if not queue: break
                    url, d = queue.popleft()
                    
                    # Double check if already processed (could have been added multiple times)
                    if url in self.processed_urls:
                        continue
                        
                    tasks.append(self._process_url_step(session, url, d))
                
                if tasks:
                    # Execute batch
                    results = await asyncio.gather(*tasks)
                    # Extend queue with new findings
                    for new_links in results:
                        if new_links:
                            for link, link_depth in new_links:
                                if link not in self.processed_urls:
                                    queue.append((link, link_depth))

    async def _process_url_step(self, session, url, depth):
        """Helper to process one URL and return discovered links."""
        if len(self.processed_urls) >= self.max_urls:
            # Stop if limit reached
            return []
            
        if self._should_skip(url):
            return []

        self.processed_urls.add(url)
        content = await self._fetch(session, url)
        
        new_links = []
        if content and depth > 0:
            extracted = extract_links(content, url)
            for link in extracted:
                if link not in self.processed_urls and not self._should_skip(link):
                    new_links.append((link, depth - 1))
        return new_links

    def get_results(self):
        return self.url_cache, self.processed_urls
