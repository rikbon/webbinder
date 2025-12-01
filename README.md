# WebBinder

WebBinder is a command-line utility, containerized with Docker and using a Conda environment, that crawls a given URL, downloads its content and the content of its links, and compiles them into well-structured PDF documents and Markdown files.

## Features

-   **Web Crawling**: Starts from a single URL and can crawl to a specified depth, discovering hyperlinks.
-   **Content Aggregation**: Fetches the HTML content of the initial page and all discovered pages.
-   **Domain Scoping**: Restricts crawling to the same domain as the initial URL to prevent crawling the entire internet.
-   **PDF Generation (Optional)**: Combines the collected HTML content (converted from Markdown) into PDF files using `xhtml2pdf`. This is now optional for faster Markdown-only output.
-   **Markdown Output**: Always generates Markdown files for each batch of links, useful for debugging or further processing.
-   **Containerized**: Packaged in a Docker container with a Conda environment for easy and consistent execution across different environments.
-   **Improved Error Handling**: Gracefully handles malformed URLs and validates the starting URL.
-   **Performance Enhancements**:
    *   **Rate Limiting**: Configurable delay between requests to avoid overwhelming servers.
    *   **URL Caching**: Caches fetched content to avoid redundant requests.
    *   **URL Limiting**: Configurable maximum number of URLs to process.
-   **Configurable Batches**: Processes links in configurable batches, generating separate PDFs/Markdown files for each.
-   **Overall Progress**: A progress bar shows the overall crawling and processing status.
-   **Link Deduplication**: Automatically deduplicates links to avoid processing the same URL multiple times.
-   **Depth Limiting**: Configurable crawling depth to control how deep into the website the crawler goes.
-   **URL Skipping**: Option to skip specific URL patterns.
-   **Clean Output**: Each page's content in the generated documents is separated by a horizontal rule and a heading indicating the URL of the page.

## Requirements

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd webbinder
    ```

2.  **Build the Docker image:**
    This command builds the Docker image and sets up the Conda environment with all necessary dependencies.
    ```bash
    docker compose build
    ```
    *(Note: The first build might take some time as it sets up the Conda environment.)*

## Usage

To run WebBinder, use the `docker compose run` command. You need to provide the starting URL, and you can use various optional flags to control its behavior.

```bash
UID=$(id -u) GID=$(id -g) docker compose run --rm webbinder -u <your_url> [OPTIONS]
```

The `UID=$(id -u) GID=$(id -g)` part ensures that the files created by the Docker container have the correct permissions on your host machine. The `--rm` flag ensures that the container is removed after it finishes its task, keeping your system clean.

### Command-Line Options

*   `-u`, `--url` (required): The starting URL to process.
*   `-o`, `--output` (default: `output.pdf`): The base name of the output PDF files. Markdown files will use this base name with a `.md` extension.
*   `-d`, `--debug`: Enable debug output for more verbose logging.
*   `--pdf`: Generate PDF output in addition to Markdown files. If omitted, only Markdown files are generated.
*   `--links-per-pdf` (default: `25`): Number of links to include in each PDF/Markdown batch.
*   `--rate-limit` (default: `0.5`): Delay between requests in seconds to prevent overwhelming servers.
*   `--max-urls` (default: `100`): Maximum number of URLs to process in total.
*   `--depth` (default: `1`): Crawling depth. A depth of 1 means only the initial URL and its direct links will be processed.
*   `--skip-urls` (list of patterns): Space-separated list of URL patterns to skip during crawling.

### Example

To download `https://www.gemini.com/` with a crawling depth of 2, generate both PDF and Markdown, and save as `gemini_content.pdf` (and `gemini_content-*.md`):

```bash
UID=$(id -u) GID=$(id -g) docker compose run --rm webbinder -u https://www.gemini.com/ -o gemini_content.pdf --pdf --depth 2
```

To generate only Markdown files for `https://example.com/` skipping any URLs containing 'privacy':

```bash
UID=$(id -u) GID=$(id -g) docker compose run --rm webbinder -u https://example.com/ -o example_content.md --skip-urls privacy
```

## Output

The application will generate Markdown (`.md`) files for each batch of processed links in the `output` directory. If the `--pdf` flag is used, corresponding PDF files (`.pdf`) will also be generated in the same directory. The output directory is created on your host machine and contains all generated files.

## How It Works

1.  **Conda Environment**: The application runs within a Conda environment defined in `environment.yml`, ensuring consistent dependency management.
2.  **URL Input & Validation**: Receives a URL and validates its format.
3.  **Main Page Fetch**: Fetches the HTML content of the provided URL, respecting rate limits and using an in-memory cache.
4.  **Link Extraction & Crawling**: Recursively extracts hyperlinks from fetched pages up to the specified `--depth`, filtering by domain and skipping specified patterns.
5.  **Deduplication & Limiting**: Deduplicates all discovered links and respects the `--max-urls` limit.
6.  **Content Fetching (Batched)**: Iterates through the filtered and limited links in batches (`--links-per-pdf`), fetching their content, adhering to rate limits, and caching responses.
7.  **Markdown Conversion**: Combines the HTML content of each batch into a single string, converts it to Markdown, and saves it as an `.md` file in the `output` directory.
8.  **PDF Rendering (Conditional)**: If the `--pdf` flag is set, the Markdown content is converted to HTML and then rendered into a PDF using `xhtml2pdf`.
9.  **File Saving & Permissions**: Both Markdown and PDF files are saved to the `output` directory on your host machine, with ownership adjusted to your user's UID/GID for easy access.

## Dockerization

The application is containerized for portability and ease of use. The `Dockerfile` uses a Miniconda base image to create a isolated and reproducible environment. The `docker-compose.yml` file simplifies the build and run process, manages the volume mapping for the persistent `output` directory, and passes your host UID/GID to the container for correct file permissions.
