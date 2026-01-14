import argparse
import asyncio
import sys
import logging
import math
from tqdm import tqdm
from webbinder.crawler import AsyncCrawler
from webbinder.exporter import save_markdown, generate_pdf
from webbinder.utils import setup_logging
import validators

# Configure TQDM to work with logging if needed, or just standard
# For now standard tqdm

async def main():
    parser = argparse.ArgumentParser(description="Download a URL and its first-level links into a single PDF (Async version).")
    parser.add_argument('-u', '--url', required=True, help="The starting URL to process.")
    parser.add_argument('-o', '--output', default='output.pdf', help="The name of the output PDF file. (default: output.pdf)")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output.")
    parser.add_argument('--pdf', action='store_true', help="Generate PDF output.")
    parser.add_argument('--links-per-pdf', type=int, default=25, help="Number of links to include in each PDF. (default: 25)")
    parser.add_argument('--rate-limit', type=float, default=0.5, help="Delay between requests in seconds. (default: 0.5)")
    parser.add_argument('--max-urls', type=int, default=100, help="Maximum number of URLs to process. (default: 100)")
    parser.add_argument('--depth', type=int, default=1, help="Crawling depth. (default: 1)")
    parser.add_argument('--concurrency', type=int, default=5, help="Number of concurrent requests. (default: 5)")
    parser.add_argument('--skip-urls', nargs='*', default=[], help="List of URL patterns to skip.")
    
    args = parser.parse_args()

    # Setup Logging
    logger = setup_logging(args.debug)

    if not validators.url(args.url):
        logger.error(f"Invalid URL: {args.url}")
        sys.exit(1)

    # Initialize Crawler
    crawler = AsyncCrawler(
        start_url=args.url,
        max_urls=args.max_urls,
        depth=args.depth,
        skip_urls=args.skip_urls,
        rate_limit=args.rate_limit,
        concurrency=args.concurrency
    )

    # Run Crawler with simple progress indication via tqdm manually if we wanted, 
    # but since crawler runs implicitly, we just wait.
    # To start, we just run it.
    print("Starting crawl... please wait.")
    await crawler.run()
    
    url_cache, processed_urls = crawler.get_results()
    print(f"Crawl finished. Found {len(processed_urls)} URLs.")

    # Process Results
    main_content = url_cache.get(args.url)
    if not main_content:
        logger.error("Failed to retrieve main page content.")
        sys.exit(1)

    all_links_to_process = [link for link in list(processed_urls) if link != args.url]
    
    # Sort for deterministic output
    all_links_to_process.sort()

    output_dir = 'output'
    name_base = args.output.rsplit('.', 1)[0]
    ext = ".pdf" if args.pdf else "" # Extension handling is a bit loose in original, fixing here implies .pdf for pdfs

    # Logic: if no links, just main page
    if not all_links_to_process:
        md_filename = f"{name_base}.md"
        saved_md = save_markdown(main_content, md_filename, output_dir)
        if args.pdf:
            generate_pdf(md_filename, args.output, output_dir)
        return

    # Batches
    total_links = len(all_links_to_process)
    num_batches = math.ceil(total_links / args.links_per_pdf)
    
    with tqdm(total=total_links, desc="Generating Documents") as pbar:
        for i in range(0, total_links, args.links_per_pdf):
            batch_links = all_links_to_process[i:i + args.links_per_pdf]
            pdf_index = (i // args.links_per_pdf) + 1
            
            # Naming
            current_output_filename = f"{name_base}-{pdf_index}.pdf" if args.pdf else f"{name_base}-{pdf_index}" # logic slightly differs
            # Original: name + -index + ext. 
            # If output is "out.pdf", name="out", ext=".pdf". -> "out-1.pdf".
            # If output is "out.md", name="out", ext=".md" -> "out-1.md".
            
            _, out_ext = args.output.rsplit('.', 1) if '.' in args.output else ("", "")
            if not out_ext: out_ext = ".pdf" if args.pdf else ".md"
            
            current_output_filename = f"{name_base}-{pdf_index}.{out_ext.lstrip('.')}"
            md_filename = f"{name_base}-{pdf_index}.md"

            # Construct content
            batch_content = [main_content] # Always start with main
            
            for link in batch_links:
                content = url_cache.get(link)
                if content:
                    batch_content.append(f"<hr><h1>{link}</h1>")
                    batch_content.append(content)
                pbar.update(1)
            
            # Join and Save
            full_html = "".join(batch_content)
            save_markdown(full_html, md_filename, output_dir)
            
            if args.pdf:
                 # Ensure PDF extension
                if not current_output_filename.lower().endswith('.pdf'):
                    current_output_filename += ".pdf"
                generate_pdf(md_filename, current_output_filename, output_dir)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)