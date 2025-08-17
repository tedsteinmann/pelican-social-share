# Integration Guide

This guide shows how to integrate `pelican-social-share` with different Pelican themes and setups.

## Basic Integration

### 1. Install the Plugin

```bash
pip install pelican-social-share
playwright install chromium
```

### 2. Configure Pelican

Add to your `pelicanconf.py`:

```python
PLUGINS = ['pelican_social_share']

# Required settings
SOCIAL_TEMPLATE_NAME = "social_card.html"
SOCIAL_PORTRAIT_PATH = "static/images/portrait.jpg"

# Optional settings (with defaults)
SOCIAL_SCOPE = "articles"  # "articles", "pages", or "both"
SOCIAL_CARD_HTML_DIR = "content/social"
SOCIAL_IMAGE_DIR = "content/static/images/social"
SOCIAL_VIEWPORT = (1200, 675)
SOCIAL_HASH_SKIP = True
```

### 3. Create Template

Create `social_card.html` in your theme's templates directory. See `examples/social_card.html` for a complete example.

### 4. Add Meta Tags

Add to your theme's base template `<head>` section:

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

### 5. Add Taglines to Content

Add `tagline` metadata to your articles:

```markdown
Title: My Great Article
Date: 2025-01-01
Tagline: Discover the secrets of effective content creation

Content goes here...
```

## Theme-Specific Examples

### Bootstrap-based Themes

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { margin: 0; width: 1200px; height: 675px; overflow: hidden; }
    </style>
</head>
<body class="bg-white">
    <div class="container-fluid h-100">
        <div class="row h-100 align-items-center">
            <div class="col-8">
                <h1 class="display-3 fw-bold text-dark">{{ tagline }}</h1>
                <p class="lead text-muted">{{ SITEURL|replace('https://', '') }}</p>
            </div>
            <div class="col-4 text-center">
                <img src="{{ SITEURL }}{{ portrait_url }}" class="img-fluid rounded-3" alt="Portrait">
            </div>
        </div>
    </div>
</body>
</html>
```

### Tailwind CSS-based Themes

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; width: 1200px; height: 675px; overflow: hidden; }
    </style>
</head>
<body class="bg-white">
    <div class="flex h-full items-center p-16 gap-12">
        <div class="flex-1">
            <h1 class="text-6xl font-bold text-gray-900 leading-tight">{{ tagline }}</h1>
            <p class="text-2xl text-gray-600 mt-4">{{ SITEURL|replace('https://', '') }}</p>
        </div>
        <div class="w-80">
            <img src="{{ SITEURL }}{{ portrait_url }}" class="w-full rounded-xl shadow-lg" alt="Portrait">
        </div>
    </div>
</body>
</html>
```

## Advanced Configuration

### Custom Styling per Category

You can create category-specific social cards by using conditional logic in your template:

```html
<style>
    body { margin: 0; width: 1200px; height: 675px; overflow: hidden; }
    
    {% if article.category == 'tech' %}
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .tagline { color: white; }
    {% elif article.category == 'design' %}
        body { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .tagline { color: white; }
    {% else %}
        body { background: white; }
        .tagline { color: #1a1a1a; }
    {% endif %}
    
    .social-card { display: flex; height: 100%; padding: 60px; gap: 40px; align-items: center; }
    .tagline { flex: 1; font-size: 64px; font-weight: bold; line-height: 1.1; }
    .portrait { width: 320px; }
    .portrait img { width: 100%; border-radius: 12px; }
</style>
```

### Multiple Portrait Support

Support different portraits per content type:

```python
# In pelicanconf.py
SOCIAL_PORTRAIT_PATH = "static/images/portrait-default.jpg"
SOCIAL_PORTRAIT_TECH = "static/images/portrait-tech.jpg"
SOCIAL_PORTRAIT_DESIGN = "static/images/portrait-design.jpg"
```

```html
<!-- In template -->
{% set portrait_path = portrait_url %}
{% if article.category == 'tech' %}
    {% set portrait_path = "/static/images/portrait-tech.jpg" %}
{% elif article.category == 'design' %}
    {% set portrait_path = "/static/images/portrait-design.jpg" %}
{% endif %}

<img src="{{ SITEURL }}{{ portrait_path }}" alt="Portrait">
```

### Development Mode

For theme development, disable screenshots to speed up builds:

```python
# In pelicanconf.py for development
SOCIAL_DISABLE_SCREENSHOT = True
```

This generates the HTML files but skips Playwright screenshot generation.

### Custom Fonts

To ensure consistent fonts across different systems:

```html
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0; width: 1200px; height: 675px; overflow: hidden;
    }
</style>
```

Or include font files in your theme and reference them locally.

## Troubleshooting

### Common Issues

1. **Template not found**: Ensure `social_card.html` exists in your theme's templates directory
2. **Portrait not loading**: Check that `SOCIAL_PORTRAIT_PATH` is correct and the image exists
3. **Playwright errors**: Ensure Chromium is installed with `playwright install chromium`
4. **Font rendering differences**: Use web fonts or include font files in your theme
5. **Layout breaks**: Test your template at exactly 1200×675 dimensions

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('pelican.plugins.social_share').setLevel(logging.DEBUG)
```

### Manual Testing

Test your template manually:

```bash
# Generate a standalone screenshot
python -m pelican_social_share.cli \
    --html /path/to/your/social_card.html \
    --output test.png
```

## Performance Tips

1. **Use hash skipping**: Keep `SOCIAL_HASH_SKIP = True` to avoid regenerating unchanged images
2. **Optimize images**: Use optimized portrait images (WebP, appropriate size)
3. **Limit font loading**: Minimize external font requests
4. **Batch generation**: The plugin automatically batches all screenshots in a single Playwright session

## CI/CD Integration

For automated builds, ensure Playwright is available:

```yaml
# GitHub Actions example
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    playwright install chromium

- name: Build site
  run: pelican content
```

Add generated images to your repository or deploy them separately based on your workflow.
