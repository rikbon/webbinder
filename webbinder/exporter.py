import os
import markdown
from markdownify import markdownify as md
from xhtml2pdf import pisa
import logging
from typing import Optional, Union

logger = logging.getLogger("webbinder.exporter")

def set_permissions(file_path: str):
    """Sets file ownership to match UID/GID env vars (for Docker)."""
    try:
        uid = int(os.environ.get('UID', -1))
        gid = int(os.environ.get('GID', -1))
        if uid != -1 and gid != -1:
            os.chown(file_path, uid, gid)
    except Exception as e:
        logger.warning(f"Failed to set permissions for {file_path}: {e}")

def save_markdown(html_content: Union[str, bytes], output_filename: str, output_dir: str) -> Optional[str]:
    """Saves HTML content as a Markdown file."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        # Ensure string
        if isinstance(html_content, bytes):
            html_content = html_content.decode('utf-8', errors='ignore')
            
        text_content = md(html_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        set_permissions(output_path)
        logger.info(f"Created Markdown: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error converting to Markdown {output_filename}: {e}")
        return None

def generate_pdf(md_filename: str, output_filename: str, output_dir: str) -> Optional[str]:
    """Generates a PDF from a Markdown file using xhtml2pdf."""
    logger.info(f"Converting to PDF: {output_filename}...")
    try:
        os.makedirs(output_dir, exist_ok=True)
        md_path = os.path.join(output_dir, md_filename)
        
        if not os.path.exists(md_path):
            logger.error(f"Markdown file not found: {md_path}")
            return None

        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content)
        
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "w+b") as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_file
            )

        if not pisa_status.err:
            set_permissions(output_path)
            logger.info(f"Successfully created PDF: {output_path}")
            return output_path
        else:
            logger.error(f"Error converting to PDF {output_filename}: {pisa_status.err}")
            return None

    except Exception as e:
        logger.error(f"Exception during PDF generation {output_filename}: {e}")
        return None
