# Development Guide

## Project Architecture

WebBinder is structured as a modular Python package:

-   `main.py`: The async entry point. Handles argument parsing and orchestrates the crawl.
-   `webbinder/`:
    -   `crawler.py`: The `AsyncCrawler` class. Manages the crawl queue, concurrency (semaphore), and rate limiting.
    -   `parser.py`: Link extraction logic using `BeautifulSoup`.
    -   `exporter.py`: Handles saving content to Markdown and converting to PDF using `xhtml2pdf`.
    -   `utils.py`: Shared utilities like logging.

## Setting Up Environment

We use Conda for dependency management.

```bash
conda env create -f environment.yml
conda activate webbinder
```

## Running Tests

Tests are located in `tests/` and use `pytest`.

```bash
python -m pytest tests
```

## Adding New Features

### Adding a new output format
Modify `webbinder/exporter.py` to add a new saving function, and update `main.py` to call it.

### Changing the crawling strategy
`AsyncCrawler` in `webbinder/crawler.py` uses a simple iterative batching approach. You can modify `_process_url` to implement different traversal strategies (DFS vs BFS default).
