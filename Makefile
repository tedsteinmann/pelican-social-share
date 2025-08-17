# Makefile for pelican-social-share development

.PHONY: help install install-dev test lint format clean build upload

help:
	@echo "Available commands:"
	@echo "  install      Install package"
	@echo "  install-dev  Install package in development mode"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  upload       Upload to PyPI"

install:
	pip install .

install-dev:
	pip install -e ".[dev]"
	playwright install chromium

test:
	pytest tests/ -v

lint:
	flake8 pelican_social_share/
	mypy pelican_social_share/

format:
	black pelican_social_share/ tests/ examples/
	isort pelican_social_share/ tests/ examples/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

# Development helpers
dev-setup: install-dev
	@echo "Development environment ready!"

test-example:
	@echo "Testing with example template..."
	python -m pelican_social_share.cli \
		--html examples/social_card.html \
		--output test_output.png
	@echo "Test screenshot saved to test_output.png"
