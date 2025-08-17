#!/bin/bash
# Development setup script for pelican-social-share

set -e

echo "Setting up pelican-social-share development environment..."

# Install package in development mode
echo "Installing package in development mode..."
pip install -e ".[dev]"

# Install Playwright and Chromium
echo "Installing Playwright browsers..."
playwright install chromium

echo "Running tests..."
pytest tests/ -v

echo "Running linting..."
flake8 pelican_social_share/
black --check pelican_social_share/

echo "Development setup complete!"
echo ""
echo "To test the plugin:"
echo "1. Copy examples/social_card.html to your theme's templates directory"
echo "2. Add the plugin to your pelicanconf.py PLUGINS list"
echo "3. Add SOCIAL_* configuration to pelicanconf.py"
echo "4. Add 'tagline:' metadata to your articles"
echo "5. Run 'pelican content'"
