# Example Pelican Configuration

# Basic Pelican settings
SITENAME = 'Example Blog'
SITEURL = 'https://example.com'
AUTHOR = 'Your Name'

# Plugin configuration
PLUGINS = ['pelican_social_share']

# Social Share Plugin Settings
SOCIAL_TEMPLATE_NAME = "social_card.html"
SOCIAL_PORTRAIT_PATH = "static/images/portrait.jpg"

# Optional settings with defaults
SOCIAL_CARD_HTML_DIR = "content/social"
SOCIAL_IMAGE_DIR = "content/static/images/social"
SOCIAL_SCOPE = "articles"  # "articles", "pages", or "both"

# Screenshot settings
SOCIAL_VIEWPORT = (1200, 675)
SOCIAL_DEVICE_SCALE_FACTOR = 1
SOCIAL_WAIT_UNTIL = "networkidle"
SOCIAL_WAIT_SELECTOR = None  # e.g., "#ready" if you add a ready indicator

# Performance settings
SOCIAL_HASH_SKIP = True
SOCIAL_HASH_VERSION = "v1"

# Development setting
SOCIAL_DISABLE_SCREENSHOT = False  # Set to True to skip screenshot generation

# Standard Pelican settings
TIMEZONE = 'UTC'
DEFAULT_LANG = 'en'
DEFAULT_PAGINATION = 10

# Paths
PATH = 'content'
OUTPUT_PATH = 'output'
STATIC_PATHS = ['images', 'static']

# URL settings
ARTICLE_URL = '{slug}.html'
ARTICLE_SAVE_AS = '{slug}.html'
PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'
