"""Test configuration for pytest."""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_content_dir():
    """Create a temporary content directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_pelican_settings(temp_content_dir, temp_output_dir):
    """Mock Pelican settings for testing."""
    return {
        'SOCIAL_TEMPLATE_NAME': 'social_card.html',
        'SOCIAL_PORTRAIT_PATH': 'static/images/portrait.jpg',
        'SOCIAL_CARD_HTML_DIR': str(temp_content_dir / 'social'),
        'SOCIAL_IMAGE_DIR': str(temp_content_dir / 'static' / 'images' / 'social'),
        'OUTPUT_PATH': str(temp_output_dir),
        'SITEURL': 'https://example.com',
        'SOCIAL_SCOPE': 'articles',
        'SOCIAL_VIEWPORT': (1200, 675),
        'SOCIAL_DEVICE_SCALE_FACTOR': 1,
        'SOCIAL_WAIT_UNTIL': 'networkidle',
        'SOCIAL_WAIT_SELECTOR': None,
        'SOCIAL_HASH_SKIP': True,
        'SOCIAL_HASH_VERSION': 'v1',
        'SOCIAL_DISABLE_SCREENSHOT': False,
    }


@pytest.fixture
def sample_template_content():
    """Sample social card template content."""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; width: 1200px; height: 675px; overflow: hidden; }
        .social-card { display: flex; height: 100%; padding: 60px; gap: 40px; }
        .tagline { flex: 1; font-size: 72px; font-weight: bold; line-height: 1.1; }
        .portrait { width: 300px; }
        .portrait img { width: 100%; height: auto; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="social-card">
        <div class="tagline">{{ tagline }}</div>
        <div class="portrait">
            <img src="{{ SITEURL }}{{ portrait_url }}" alt="Portrait">
        </div>
    </div>
</body>
</html>"""
