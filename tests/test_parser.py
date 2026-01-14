import pytest
from webbinder.parser import extract_links

def test_extract_links_simple():
    html = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="https://example.com/page2">Page 2</a>
            <a href="https://google.com">External</a>
        </body>
    </html>
    """
    base_url = "https://example.com"
    links = extract_links(html, base_url)
    
    assert "https://example.com/page1" in links
    assert "https://example.com/page2" in links
    assert "https://google.com" not in links # Different domain
    assert len(links) == 2

def test_extract_links_invalid():
    html = """
    <a href="javascript:void(0)">JS</a>
    <a href="mailto:test@test.com">Mail</a>
    """
    base_url = "https://example.com"
    links = extract_links(html, base_url)
    assert len(links) == 0
