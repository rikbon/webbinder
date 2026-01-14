# WebBinder

WebBinder is a high-performance, asynchronous CLI web crawler and document generator. It fetches web pages, recursively discovers links, and compiles the content into structured PDF or Markdown documents.

## Features

-   **Async & Concurrent**: Uses `aiohttp` and `asyncio` for fast, concurrent crawling.
-   **Configurable Concurrency**: Control the number of parallel requests.
-   **Smart Crawling**: Depths limits, domain restriction, and URL skipping patterns.
-   **Document Generation**: Produces clean Markdown and optional PDFs (via `xhtml2pdf`).
-   **Batch Processing**: Splits large sites into manageable document batches.
-   **Robust**: Automatic retries, rate limiting, and caching.
-   **Dockerized**: Easy to run anywhere with no dependency headaches.

## Installation

### Using Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rikbon/webbinder
    cd webbinder
    ```

2.  **Build:**
    ```bash
    docker compose build
    ```

### Local Development

1.  **Install Conda environment:**
    ```bash
    conda env create -f environment.yml
    conda activate webbinder
    ```

## Usage

### Docker

```bash
# Basic Usage
UID=$(id -u) GID=$(id -g) docker compose run --rm webbinder -u https://example.com/

# Advanced Usage
UID=$(id -u) GID=$(id -g) docker compose run --rm webbinder \
  -u https://example.com/ \
  -o my_doc.pdf \
  --pdf \
  --depth 2 \
  --concurrency 10
```

### Command-Line Arguments

-   `-u, --url` (Required): Starting URL.
-   `-o, --output`: Output filename (default: `output.pdf`).
-   `--pdf`: Enable PDF generation.
-   `--links-per-pdf`: Links per document batch (default: 25).
-   `--rate-limit`: Delay between requests (default: 0.5s).
-   `--max-urls`: Max URLs to process (default: 100).
-   `--depth`: Crawl depth (default: 1).
-   `--concurrency`: Number of concurrent requests (default: 5).
-   `--debug`: Enable verbose logging.
-   `--skip-urls`: Patterns to skip (e.g. `--skip-urls "login" "admin"`).

## Development

-   [Architecture & Design](docs/development.md)
-   [Advanced Usage & Troubleshooting](docs/usage.md)
-   [Contributing Guide](docs/contributing.md)

## License

[WTFPL](LICENSE) - Do What The Fuck You Want To Public License.
