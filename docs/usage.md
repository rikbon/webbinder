# Advanced Usage Guide

This guide covers advanced configurations and troubleshooting for WebBinder.

## Crawling Strategies

### Depth Control
The `--depth` parameter controls how far the crawler goes.
- `0`: Only the starting URL.
- `1`: Starting URL + links found on that page (default).
- `2`: Depth 1 + links found on those pages.

**Warning**: Increasing depth exponentially increases the number of pages. Always use `--max-urls` to prevent infinite loops or huge downloads.

```bash
# Deep crawl limited to 50 pages
docker compose run --rm webbinder -u https://example.com --depth 3 --max-urls 50
```

### Filtering
You can skip specific sections of a site using `--skip-urls`. This matches substrings in the URL.

```bash
# Skip login pages, admin panels, and tags
docker compose run --rm webbinder -u https://example.com --skip-urls "login" "admin" "/tag/"
```

## Performance Tuning
### Concurrency
The `--concurrency` flag (default: 5) determines how many parallel requests are made.
- **Low (1-3)**: Good for fragile servers or strict rate limits.
- **High (10-20)**: Good for fast servers and high-bandwidth connections.

### Rate Limiting
To be polite, use `--rate-limit` (seconds).
- `0`: No delay (aggressive).
- `1.0`: One second delay per slot.

## PDF Generation Tips
WebBinder uses `xhtml2pdf`.
- It supports basic CSS2.1.
- Complex layouts (Grid, Flexbox) might not render perfectly.
- **Recommendation**: Use the Markdown output (`.md`) if you need to feed LLMs or use other converters (like Pandoc).

## Troubleshooting

### "Temporary failure in name resolution"
This usually happens in Docker/WSL2 environments.
**Fix**: Ensure `docker-compose.yml` uses `network_mode: "host"`.

### "TimeoutError"
The server is slow responding.
**Fix**: The crawler has a 30s timeout. If this persists, the site might be blocking you or is down.

### "403 Forbidden"
The site might be blocking bots.
**Fix**: WebBinder sends a Chrome User-Agent header, but some sites have advanced bot detection (Cloudflare, etc.) which might still block it.
