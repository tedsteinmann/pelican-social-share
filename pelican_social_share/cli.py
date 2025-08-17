#!/usr/bin/env python3
"""
Standalone CLI tool for testing social card generation.

Usage:
    python -m pelican_social_share.cli --html input.html --output output.png
"""

import argparse
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate social share images from HTML files"
    )
    parser.add_argument(
        "--html",
        required=True,
        help="Path to HTML file to screenshot"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output PNG file path"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1200,
        help="Screenshot width (default: 1200)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=675,
        help="Screenshot height (default: 675)"
    )
    parser.add_argument(
        "--wait-until",
        default="networkidle",
        choices=["networkidle", "load", "domcontentloaded"],
        help="Wait condition (default: networkidle)"
    )
    
    args = parser.parse_args()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("ERROR: Playwright not installed.", file=sys.stderr)
        print("Install with: pip install playwright && playwright install chromium", file=sys.stderr)
        return 1
    
    html_path = Path(args.html)
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}", file=sys.stderr)
        return 1
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                viewport={"width": args.width, "height": args.height}
            )
            
            # Load HTML file
            file_url = html_path.absolute().as_uri()
            page.goto(file_url, wait_until=args.wait_until, timeout=15000)
            
            # Take screenshot
            page.screenshot(path=str(output_path), full_page=False)
            
            browser.close()
            
        print(f"Screenshot saved to: {output_path}")
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to generate screenshot: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
