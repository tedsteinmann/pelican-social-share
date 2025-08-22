#!/usr/bin/env python3
"""Quick test script to generate a sample social card."""

import os
import tempfile
from unittest.mock import MagicMock
from pelican_social_share.plugin import build_social_pages

# Create a mock generator with sample settings
class MockGenerator:
    def __init__(self):
        self.settings = {
            "SOCIAL_TEMPLATE_NAME": "social_card.html",
            "SOCIAL_CARD_HTML_DIR": "content/social",
            "OUTPUT_PATH": "test_output",
            "SOCIAL_PORTRAIT_PATH": "static/images/portrait.jpg",
            "SITEURL": "https://example.com",
            "SITENAME": "Test Site",
            "SOCIAL_SAMPLE_TAGLINE": "This is a very long sample tagline to test how the text wraps within the safe zone boundaries and looks good on mobile",
        }
        self.env = MagicMock()
        
        # Mock template that returns our example template content
        mock_template = MagicMock()
        with open("examples/social_card.html", "r") as f:
            template_content = f.read()
        mock_template.render.return_value = template_content
        self.env.get_template.return_value = mock_template

if __name__ == "__main__":
    # Create output directory
    os.makedirs("test_output/social", exist_ok=True)
    
    # Generate sample
    generator = MockGenerator()
    build_social_pages(generator, [])  # Empty content list, just generate sample
    
    print("Sample generated! Check test_output/social/_sample.html")
    print("Open in browser with ?debug to see safe zone")
