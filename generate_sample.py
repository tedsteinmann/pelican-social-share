#!/usr/bin/env python3
"""Generate a sample social card HTML for testing the template design.

This script allows you to quickly test the social card template without
setting up a full Pelican build. Perfect for iterating on design.

Usage:
    python generate_sample.py
    python generate_sample.py --debug  # Shows safe zone outline
    python generate_sample.py --list-portraits  # Check portrait options
"""

import argparse
import os
import shutil
import sys
from jinja2 import Environment, FileSystemLoader

# Ensure output is flushed immediately
sys.stdout.reconfigure(line_buffering=True)

def generate_sample(show_debug=False):
    """Generate sample social card HTML."""
    
    print("🚀 Generating sample social card...")
    
    # Ensure old sample is removed so we always regenerate fresh output
    sample_output_file = "sample_output/social_card_sample.html"
    if os.path.exists(sample_output_file):
        try:
            os.remove(sample_output_file)
            print(f"🧹 Removed existing sample: {sample_output_file}")
        except Exception as e:
            print(f"⚠️  Could not remove existing sample ({sample_output_file}): {e}")
    
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader("."))
    
    try:
        # Load the template
        template = env.get_template("examples/social_card.html")
        print("✅ Template loaded successfully")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    
    # Sample data for testing
    # Check for local portrait file first, then fall back to data URL
    portrait_files = [
        "examples/portrait.webp",
        "examples/portrait.jpg",
        "examples/portrait.png",
        "examples/portrait.svg",
        "examples/my_portrait.webp",
        "examples/my_portrait.jpg",
        "examples/my_portrait.png",
    ]
    
    portrait_url = None
    local_portrait_file = None
    for portrait_file in portrait_files:
        if os.path.exists(portrait_file):
            local_portrait_file = portrait_file
            # Copy the portrait to sample_output for relative path access
            os.makedirs("sample_output/examples", exist_ok=True)
            filename = os.path.basename(portrait_file)
            dest_path = f"sample_output/examples/{filename}"
            shutil.copy2(portrait_file, dest_path)
            portrait_url = f"./examples/{filename}"
            print(f"📸 Using local portrait: {portrait_file} (copied to sample_output)")
            break
    
    if not portrait_url:
        # Use embedded SVG as fallback
        portrait_url = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8ZGVmcz4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iZ3JhZCIgeDE9IjAlIiB5MT0iMCUiIHgyPSIxMDAlIiB5Mj0iMTAwJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiM2NjdlZWE7c3RvcC1vcGFjaXR5OjEiIC8+CiAgICAgIDxzdG9wIG9mZnNldD0iMTAwJSIgc3R5bGU9InN0b3AtY29sb3I6Izc2NGJhMjtzdG9wLW9wYWNpdHk6MSIgLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgPC9kZWZzPgogIDxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWxsPSJ1cmwoI2dyYWQpIiByeD0iMjAiLz4KICA8dGV4dCB4PSIxNTAiIHk9IjE3MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9InN5c3RlbS11aSwgLWFwcGxlLXN5c3RlbSwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSI3MiIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IndoaXRlIiBvcGFjaXR5PSIwLjkiPkVCPC90ZXh0Pgo8L3N2Zz4K"
        print("📸 Using fallback embedded portrait (add your own to examples/portrait.jpg)")
    
    sample_data = {
        "tagline": "This is a very long sample tagline to test how the text wraps within the safe zone boundaries and looks good on mobile devices",
        "SITENAME": "Example Blog",
        "SITEURL": "https://example.com", 
        "portrait_url": portrait_url
    }
    
    # Render the template
    try:
        html = template.render(**sample_data)
        print("✅ Template rendered successfully")
    except Exception as e:
        print(f"❌ Error rendering template: {e}")
        return False
    
    # Create output directory and write file
    os.makedirs("sample_output", exist_ok=True)
    output_file = "sample_output/social_card_sample.html"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ File written successfully")
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False
    
    abs_path = os.path.abspath(output_file)
    debug_suffix = "?debug" if show_debug else ""
    
    print(f"✅ Sample HTML generated: {abs_path}")
    print(f"🌐 Open in browser: file://{abs_path}{debug_suffix}")
    
    if show_debug:
        print("🔍 Debug mode: Red dashed outline shows the mobile-safe zone")
    else:
        print("💡 Add --debug flag or ?debug to URL to see safe zone outline")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Generate sample social card HTML")
    parser.add_argument("--debug", action="store_true", 
                       help="Add debug parameter to show safe zone outline")
    parser.add_argument("--list-portraits", action="store_true",
                       help="List portrait files that will be checked")
    
    args = parser.parse_args()
    
    if args.list_portraits:
        portrait_files = [
            "examples/portrait.webp",
            "examples/portrait.jpg",
            "examples/portrait.png",
            "examples/portrait.svg",
            "examples/my_portrait.webp",
            "examples/my_portrait.jpg",
            "examples/my_portrait.png",
        ]
        print("📸 Portrait files checked (in order):")
        for i, portrait_file in enumerate(portrait_files, 1):
            exists = "✅" if os.path.exists(portrait_file) else "❌"
            print(f"  {i}. {portrait_file} {exists}")
        print("\nTo add your own portrait, create one of the files above.")
        print("The first existing file will be used.")
        return
    
    if not generate_sample(args.debug):
        exit(1)

if __name__ == "__main__":
    main()
