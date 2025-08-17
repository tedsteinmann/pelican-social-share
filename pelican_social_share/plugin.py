"""Main plugin implementation for Pelican Social Share."""

import hashlib
import http.server
import logging
import os
import socketserver
import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from pelican import signals
from pelican.contents import Article, Page
from pelican.generators import ArticlesGenerator, PagesGenerator
from pelican.writers import Writer

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Use Pelican's logger instead of generator.logger
logger = logging.getLogger(__name__)

# Global storage for taglines (used for hash calculation)
_taglines = {}


def register() -> None:
    """Register plugin with Pelican."""
    signals.article_generator_finalized.connect(build_social_pages_articles)
    signals.page_generator_finalized.connect(build_social_pages_pages)
    signals.finalized.connect(capture_social_cards)


def build_social_pages_articles(generator: ArticlesGenerator) -> None:
    """Build social HTML pages for articles."""
    scope = generator.settings.get("SOCIAL_SCOPE", "articles")
    if scope in ("articles", "both"):
        build_social_pages(generator, generator.articles)


def build_social_pages_pages(generator: PagesGenerator) -> None:
    """Build social HTML pages for pages."""
    scope = generator.settings.get("SOCIAL_SCOPE", "articles")
    if scope in ("pages", "both"):
        build_social_pages(generator, generator.pages)


def build_social_pages(
    generator: Union[ArticlesGenerator, PagesGenerator],
    content_objects: List[Union[Article, Page]]
) -> None:
    """Render minimal social HTML pages using theme template."""
    settings = generator.settings
    template_name = settings.get("SOCIAL_TEMPLATE_NAME", "social_card.html")
    
    try:
        template = generator.env.get_template(template_name)
    except Exception as e:
        logger.warning(
            f"[social_share] Template '{template_name}' not found: {e}"
        )
        return

    # Setup directories
    html_dir = settings.get("SOCIAL_CARD_HTML_DIR", "content/social")
    output_path = settings.get("OUTPUT_PATH", "output")
    output_social_dir = os.path.join(output_path, "social")
    
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(output_social_dir, exist_ok=True)

    # Portrait path handling
    portrait_path = settings.get("SOCIAL_PORTRAIT_PATH", "")
    if portrait_path.startswith("content/"):
        portrait_url = "/" + portrait_path.replace("content/", "")
    else:
        portrait_url = "/" + portrait_path.lstrip("/")

    siteurl = settings.get("SITEURL", "")
    sitename = settings.get("SITENAME", "")
    
    processed = 0
    
    for content_obj in content_objects:
        tagline = content_obj.metadata.get("tagline")
        if not tagline:
            continue
            
        slug = content_obj.slug
        
        # Render template
        try:
            html_content = template.render(
                tagline=tagline,
                portrait_url=portrait_url,
                content_obj=content_obj,
                article=content_obj if isinstance(content_obj, Article) else None,
                page=content_obj if isinstance(content_obj, Page) else None,
                SITEURL=siteurl,
                SITENAME=sitename,
                SEO=settings.get("SEO", {}),  # Add SEO variable
            )
        except Exception as e:
            logger.warning(
                f"[social_share] Failed to render template for {slug}: {e}"
            )
            continue

        # Write to content directory (for versioning)
        content_html_path = os.path.join(html_dir, f"{slug}.html")
        try:
            with open(content_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        except Exception as e:
            logger.warning(
                f"[social_share] Failed to write HTML for {slug}: {e}"
            )
            continue

        # Also write to output directory for immediate screenshot availability
        output_html_path = os.path.join(output_social_dir, f"{slug}.html")
        try:
            with open(output_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        except Exception as e:
            logger.warning(
                f"[social_share] Failed to write output HTML for {slug}: {e}"
            )
            continue

        # Set metadata for template usage
        content_obj.metadata["social_image"] = f"/static/images/social/{slug}.png"
        
        # Store tagline globally for screenshot phase
        _taglines[slug] = tagline
        
        processed += 1

    if processed > 0:
        logger.info(f"[social_share] Generated {processed} social card HTML files")


def capture_social_cards(pelican_obj: Any) -> None:
    """Capture screenshots of social cards using Playwright."""
    settings = pelican_obj.settings
    
    # Check if screenshots are disabled
    if settings.get("SOCIAL_DISABLE_SCREENSHOT", False):
        logger.info("[social_share] Screenshots disabled")
        return
    
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning(
            "[social_share] Playwright not installed. Install with: "
            "pip install playwright && playwright install chromium"
        )
        return

    output_path = settings.get("OUTPUT_PATH", "output")
    image_dir = settings.get("SOCIAL_IMAGE_DIR", "content/static/images/social")
    
    os.makedirs(image_dir, exist_ok=True)

    # Find social HTML files to process
    social_pages = []
    social_html_dir = os.path.join(output_path, "social")
    
    if not os.path.isdir(social_html_dir):
        logger.debug("[social_share] No social HTML directory found")
        return
        
    for filename in os.listdir(social_html_dir):
        if filename.endswith(".html"):
            slug = filename[:-5]  # Remove .html extension
            social_pages.append(slug)

    if not social_pages:
        logger.debug("[social_share] No social pages to process")
        return

    # Collect taglines for hash calculation
    taglines = _taglines

    # Screenshot settings
    viewport = settings.get("SOCIAL_VIEWPORT", (1200, 675))
    device_scale_factor = settings.get("SOCIAL_DEVICE_SCALE_FACTOR", 1)
    wait_until = settings.get("SOCIAL_WAIT_UNTIL", "networkidle")
    wait_selector = settings.get("SOCIAL_WAIT_SELECTOR", "body.images-ready")  # Wait for images
    hash_skip = settings.get("SOCIAL_HASH_SKIP", True)
    hash_version = settings.get("SOCIAL_HASH_VERSION", "v1")

    # Start HTTP server and capture screenshots
    try:
        with serve_directory(output_path) as port:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    viewport={
                        "width": viewport[0],
                        "height": viewport[1],
                        "deviceScaleFactor": device_scale_factor
                    }
                )
                
                generated = 0
                skipped = 0
                errors = 0
                
                for slug in social_pages:
                    tagline = taglines.get(slug, "")
                    if not tagline:
                        continue
                        
                    png_path = os.path.join(image_dir, f"{slug}.png")
                    
                    # Check hash for skip logic
                    if hash_skip and should_skip_generation(
                        png_path, slug, tagline, hash_version
                    ):
                        skipped += 1
                        continue
                    
                    url = f"http://127.0.0.1:{port}/social/{slug}.html"
                    
                    try:
                        # Navigate and wait for network idle
                        page.goto(url, wait_until=wait_until, timeout=15000)
                        
                        # Wait for images to load (custom selector)
                        if wait_selector:
                            try:
                                page.wait_for_selector(wait_selector, timeout=10000)
                            except:
                                logger.warning(f"[social_share] Timeout waiting for selector {wait_selector} on {slug}")
                        
                        # Additional wait for images to render
                        page.wait_for_timeout(1000)  # 1 second additional wait
                        
                        # Take screenshot
                        page.screenshot(path=png_path, full_page=False)
                        
                        # Save hash for future skip logic
                        if hash_skip:
                            save_content_hash(png_path, slug, tagline, hash_version)
                        
                        generated += 1
                        
                    except Exception as e:
                        logger.warning(
                            f"[social_share] Failed to capture {slug}: {e}"
                        )
                        errors += 1
                        continue
                
                browser.close()
                
                logger.info(
                    f"[social_share] Screenshots: {generated} generated, "
                    f"{skipped} skipped, {errors} errors"
                )
                
    except Exception as e:
        logger.error(f"[social_share] Screenshot process failed: {e}")


@contextmanager
def serve_directory(directory: str, port: int = 0) -> Generator[int, None, None]:
    """Start a temporary HTTP server for the given directory."""
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        
        def log_message(self, format: str, *args: Any) -> None:
            # Suppress HTTP server logs
            pass
    
    with socketserver.TCPServer(("127.0.0.1", port), QuietHandler) as httpd:
        assigned_port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        
        try:
            # Give server a moment to start
            time.sleep(0.1)
            yield assigned_port
        finally:
            httpd.shutdown()
            thread.join(timeout=1.0)


def make_content_hash(slug: str, tagline: str, version: str) -> str:
    """Create a hash for content to detect changes."""
    hasher = hashlib.sha256()
    hasher.update(version.encode("utf-8"))
    hasher.update(slug.encode("utf-8"))
    hasher.update(tagline.encode("utf-8"))
    return hasher.hexdigest()[:16]


def should_skip_generation(
    png_path: str, slug: str, tagline: str, version: str
) -> bool:
    """Check if PNG generation should be skipped based on hash."""
    if not os.path.exists(png_path):
        return False
    
    hash_file = png_path + ".hash"
    if not os.path.exists(hash_file):
        return False
    
    try:
        with open(hash_file, "r", encoding="utf-8") as f:
            stored_hash = f.read().strip()
        
        current_hash = make_content_hash(slug, tagline, version)
        return stored_hash == current_hash
        
    except Exception:
        return False


def save_content_hash(png_path: str, slug: str, tagline: str, version: str) -> None:
    """Save content hash for future skip logic."""
    hash_file = png_path + ".hash"
    content_hash = make_content_hash(slug, tagline, version)
    
    try:
        with open(hash_file, "w", encoding="utf-8") as f:
            f.write(content_hash)
    except Exception:
        # Hash saving is optional, don't fail the build
        pass
