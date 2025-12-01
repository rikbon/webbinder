import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import urljoin, urlparse
import os
import time
import argparse
from markdownify import markdownify as md
from tqdm import tqdm
from xhtml2pdf import pisa
import markdown
import validators

class WebBinder:
    def __init__(self, start_url, output_filename, debug_mode, generate_pdf, links_per_pdf, rate_limit, max_urls, depth, skip_urls):
        self.start_url = start_url
        self.base_output_filename = output_filename
        self.debug_mode = debug_mode
        self.generate_pdf = generate_pdf
        self.links_per_pdf = links_per_pdf
        self.rate_limit = rate_limit
        self.max_urls = max_urls
        self.depth = depth
        self.skip_urls = skip_urls

        self.processed_urls = set()
        self.url_cache = {}

        self.name, self.ext = os.path.splitext(self.base_output_filename)

    def _fetch_url(self, url):
        """Fetches a URL with a single retry on connection errors."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            if self.debug_mode:
                print(f"Connection error for {url}: {e}. Retrying in 3 seconds...")
            time.sleep(3)
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e2:
                print(f"Failed to fetch {url} on retry: {e2}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _get_content(self, url):
        """Fetches the HTML content of a URL."""
        if self.debug_mode:
            print(f"Fetching content from: {url}")
        response = self._fetch_url(url)
        if not response:
            return None
        return response.content

    def _get_links_from_html(self, html_content, base_url, current_depth):
        """Parses HTML to extract links from the same domain, with depth limiting."""
        if current_depth == 0:
            return
        
        soup = BeautifulSoup(html_content, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            try:
                href = a_tag['href']
                full_url = urljoin(base_url, href)
                if validators.url(full_url) and urlparse(full_url).netloc == urlparse(base_url).netloc \
                        and full_url not in self.processed_urls:
                    
                    if len(self.processed_urls) >= self.max_urls:
                        if self.debug_mode:
                            print(f"URL limit of {self.max_urls} reached during crawling. Stopping further link discovery.")
                        break
                    
                    self.processed_urls.add(full_url)
                    # Fetch content for recursive call
                    if full_url in self.url_cache:
                        link_content = self.url_cache[full_url]
                    else:
                        time.sleep(self.rate_limit)
                        link_content = self._get_content(full_url)
                        self.url_cache[full_url] = link_content
                    
                    if link_content and current_depth > 0:
                        # Recursively get links
                        self._get_links_from_html(link_content, full_url, current_depth - 1)
            except Exception as e:
                print(f"Error processing link {a_tag.get('href')}: {e}")

    def _save_as_markdown(self, html_content, output_filename, output_dir):
        """Saves the text content of a page as a markdown file."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)
            text_content = md(html_content)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            uid = int(os.environ.get('UID', -1))
            gid = int(os.environ.get('GID', -1))
            if uid != -1 and gid != -1:
                os.chown(output_path, uid, gid)

            print(f"Successfully created {output_path}")
        except Exception as e:
            print(f"Error converting to Markdown {output_filename}: {e}")

    def _generate_pdf(self, md_filename, output_filename, output_dir):
        """Generates a PDF from a markdown file."""
        print(f"Converting to PDF: {output_filename}...")
        try:
            os.makedirs(output_dir, exist_ok=True)
            md_path = os.path.join(output_dir, md_filename)
            if not os.path.exists(md_path):
                print(f"Error: Markdown file not found at {md_path}")
                return

            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = markdown.markdown(md_content)

            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w+b") as pdf_file:
                pisa_status = pisa.CreatePDF(
                    html_content,                # the HTML to convert
                    dest=pdf_file)           # file handle to receive result

            if not pisa_status.err:
                uid = int(os.environ.get('UID', -1))
                gid = int(os.environ.get('GID', -1))
                if uid != -1 and gid != -1:
                    os.chown(output_path, uid, gid)
                print(f"Successfully created {output_path}")
            else:
                print(f"Error converting to PDF {output_filename}: {pisa_status.err}")

        except Exception as e:
            print(f"Error converting to PDF {output_filename}: {e}")

    def run(self):
        if self.debug_mode:
            print("Debug mode is ENABLED.")
        print(f"Starting with URL: {self.start_url}")

        # Get the main page content first
        main_content_response = self._get_content(self.start_url)
        if not main_content_response:
            sys.exit(1)
        
        self.processed_urls.add(self.start_url) # Add start_url to processed_urls
        self.url_cache[self.start_url] = main_content_response # Cache main content
        
        # Now, get the links from the content we already fetched
        # The get_links_from_html function will recursively populate processed_urls
        self._get_links_from_html(main_content_response, self.start_url, self.depth)
        
        # Filter out the start_url from all_links_to_process, as it's handled separately
        all_links_to_process = [link for link in list(self.processed_urls) if link != self.start_url]

        # Deduplicate links (already handled by set, but good to ensure list conversion)
        all_links_to_process = list(set(all_links_to_process))

        # Filter out skipped URLs
        all_links_to_process = [link for link in all_links_to_process if not any(pattern in link for pattern in self.skip_urls)]

        if self.debug_mode:
            print(f"Found {len(all_links_to_process)} links to process.")

        # If there are no links, just generate a single PDF of the main page
        if not all_links_to_process:
            md_filename = f"{self.name}.md"
            self._save_as_markdown(main_content_response, md_filename, 'output')
            if self.generate_pdf:
                self._generate_pdf(md_filename, self.base_output_filename, 'output')
            print("No additional links to process.")
            return

        # Process links in batches
        with tqdm(total=len(all_links_to_process), desc="Overall Progress") as pbar:
            for i in range(0, len(all_links_to_process), self.links_per_pdf):
                batch_links = all_links_to_process[i:i + self.links_per_pdf]
                
                pdf_index = (i // self.links_per_pdf) + 1
                current_output_filename = f"{self.name}-{pdf_index}{self.ext}"
                md_filename = f"{self.name}-{pdf_index}.md"

                if self.debug_mode:
                    print(f"\n--- Processing batch {pdf_index} for {current_output_filename} ---")

                # Each PDF starts with the main page content
                batch_contents_list = [main_content_response.decode('utf-8')]
                links_processed_in_batch = 0
                for link in tqdm(batch_links, desc="Processing links", leave=False):
                    # The 'if link not in processed_urls' check is already handled by `get_links_from_html` filling the global `processed_urls`
                    # so we can directly access from url_cache, or fetch if not in cache (shouldn't happen much with max_urls check)
                    if link in self.url_cache:
                        link_content = self.url_cache[link]
                    else:
                        time.sleep(self.rate_limit)
                        link_content = self._get_content(link)
                        self.url_cache[link] = link_content
                    
                    if link_content:
                        batch_contents_list.append(f'<hr><h1>{link}</h1>')
                        batch_contents_list.append(link_content.decode('utf-8'))
                        links_processed_in_batch += 1
                
                batch_content_final = "".join(batch_contents_list)
                self._save_as_markdown(batch_content_final.encode('utf-8'), md_filename, 'output')
                if self.debug_mode:
                    print(f"Successfully processed {links_processed_in_batch} additional link(s) for {current_output_filename}.")
                if self.generate_pdf:
                    self._generate_pdf(md_filename, current_output_filename, 'output')
                pbar.update(len(batch_links))

def main():
    parser = argparse.ArgumentParser(description="Download a URL and its first-level links into a single PDF.")
    parser.add_argument('-u', '--url', required=True, help="The starting URL to process.")
    parser.add_argument('-o', '--output', default='output.pdf', help="The name of the output PDF file. (default: output.pdf)")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output.")
    parser.add_argument('--pdf', action='store_true', help="Generate PDF output.")
    parser.add_argument('--links-per-pdf', type=int, default=25, help="Number of links to include in each PDF. (default: 25)")
    parser.add_argument('--rate-limit', type=float, default=0.5, help="Delay between requests in seconds. (default: 0.5)")
    parser.add_argument('--max-urls', type=int, default=100, help="Maximum number of URLs to process. (default: 100)")
    parser.add_argument('--depth', type=int, default=1, help="Crawling depth. (default: 1)")
    parser.add_argument('--skip-urls', nargs='*', default=[], help="List of URL patterns to skip.")
    args = parser.parse_args()

    if not validators.url(args.url):
        print(f"Error: Invalid URL: {args.url}")
        sys.exit(1)

    webbinder = WebBinder(
        start_url=args.url,
        output_filename=args.output,
        debug_mode=args.debug,
        generate_pdf=args.pdf,
        links_per_pdf=args.links_per_pdf,
        rate_limit=args.rate_limit,
        max_urls=args.max_urls,
        depth=args.depth,
        skip_urls=args.skip_urls
    )
    webbinder.run()

if __name__ == "__main__":
    main()
