# Pelican Social Share

A Pelican plugin that generates social share images (Open Graph/Twitter cards) using Playwright and your site's existing theme CSS.

## Features

- **Theme-consistent**: Uses your site's existing CSS for consistent branding
- **Fast batch processing**: Single Chromium instance for efficient screenshot capture
- **Smart caching**: Hash-based regeneration skipping for faster incremental builds
- **Configurable scope**: Generate cards for articles, pages, or both
- **Graceful fallbacks**: Build continues on errors with detailed logging

## Installation

```bash
pip install pelican-social-share
playwright install chromium
```

## Quick Start

1. Add the plugin to your `pelicanconf.py`:

```python
PLUGINS = ['pelican_social_share']

# Basic configuration
SOCIAL_TEMPLATE_NAME = "social_card.html"
SOCIAL_PORTRAIT_PATH = "static/images/portrait.jpg"
```

2. Create a `social_card.html` template in your theme's templates directory:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="{{ SITEURL }}/theme/css/style.css">
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
</html>
```

3. Add `tagline` metadata to your articles:

```markdown
Title: My Article
Date: 2023-01-01
Tagline: This is a compelling tagline for social sharing

Article content here...
```

4. Build your site:

```bash
pelican content
```

Social share images will be generated at `content/static/images/social/<slug>.png`.

## Configuration

All configuration options for `pelicanconf.py`:

```python
# Required
SOCIAL_TEMPLATE_NAME = "social_card.html"  # Template in your theme
SOCIAL_PORTRAIT_PATH = "static/images/portrait.jpg"  # Path to portrait image

# Optional directories
SOCIAL_CARD_HTML_DIR = "content/social"  # Where HTML files are saved
SOCIAL_IMAGE_DIR = "content/static/images/social"  # Where PNGs are saved

# Scope control
SOCIAL_SCOPE = "articles"  # "articles", "pages", or "both"

# Screenshot settings
SOCIAL_VIEWPORT = (1200, 675)  # Screenshot dimensions
SOCIAL_DEVICE_SCALE_FACTOR = 1
SOCIAL_WAIT_UNTIL = "networkidle"  # Playwright wait condition
SOCIAL_WAIT_SELECTOR = None  # Optional CSS selector to wait for

# Performance
SOCIAL_HASH_SKIP = True  # Skip unchanged content
SOCIAL_HASH_VERSION = "v1"  # Bump to force regeneration

# Development
SOCIAL_DISABLE_SCREENSHOT = False  # Generate HTML only
```

## Template Integration

Add social meta tags to your theme's `<head>`:

```html
{% if article and article.metadata.social_image %}
    <meta property="og:image" content="{{ SITEURL }}{{ article.metadata.social_image }}">
    <meta name="twitter:image" content="{{ SITEURL }}{{ article.metadata.social_image }}">
    <meta name="twitter:card" content="summary_large_image">
{% elif page and page.metadata.social_image %}
    <meta property="og:image" content="{{ SITEURL }}{{ page.metadata.social_image }}">
    <meta name="twitter:image" content="{{ SITEURL }}{{ page.metadata.social_image }}">
    <meta name="twitter:card" content="summary_large_image">
{% endif %}
```

## Development

```bash
git clone https://github.com/tedsteinmann/pelican-social-share.git
cd pelican-social-share
pip install -e ".[dev]"
playwright install chromium
pytest
```

## Requirements

- Python 3.8+
- Pelican 4.5+
- Playwright 1.40+
- Chromium (installed via `playwright install chromium`)

## License

MIT License. See LICENSE file for details.
