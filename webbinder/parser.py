from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import validators
from typing import Set, List
import logging

logger = logging.getLogger("webbinder.parser")

def extract_links(html_content: str, base_url: str) -> Set[str]:
    """
    Parses HTML content and extracts all valid links pointing to the same domain.
    """
    links = set()
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        base_domain = urlparse(base_url).netloc

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            try:
                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                
                # Validation checks
                if not validators.url(full_url):
                    continue
                
                # Check domain strictness
                if urlparse(full_url).netloc != base_domain:
                    continue
                
                # Remove fragment identifiers for uniqueness
                full_url = full_url.split('#')[0]

                links.add(full_url)
                
            except Exception as e:
                logger.debug(f"Error parsing specific link '{href}': {e}")
                
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        
    return links
