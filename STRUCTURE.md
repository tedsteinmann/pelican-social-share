# Project Structure

```
pelican-social-share/
├── README.md                       # Main documentation
├── LICENSE                         # MIT license
├── pyproject.toml                  # Package configuration
├── Makefile                        # Development commands
├── setup_dev.sh                    # Development setup script
├── .gitignore                      # Git ignore rules
├── pelican_social_share/           # Main package
│   ├── __init__.py                 # Package initialization
│   ├── plugin.py                   # Core plugin implementation
│   └── cli.py                      # Standalone CLI tool
├── examples/                       # Example files
│   ├── social_card.html            # Example template
│   ├── pelicanconf.py              # Example configuration
│   └── example-article.md          # Example article with tagline
├── tests/                          # Test suite
│   ├── conftest.py                 # Test configuration
│   └── test_plugin.py              # Plugin tests
└── docs/                           # Documentation
    ├── requirements.md             # Updated requirements
    └── integration.md              # Integration guide
```

## Quick Start Summary

1. **Install**: `pip install pelican-social-share && playwright install chromium`
2. **Configure**: Add plugin to `PLUGINS` in `pelicanconf.py`
3. **Template**: Copy `examples/social_card.html` to your theme
4. **Meta tags**: Add social meta tags to your theme's `<head>`
5. **Content**: Add `tagline:` metadata to articles
6. **Build**: Run `pelican content`

## Key Features Implemented

✅ **Pure Python**: No Node.js dependencies, uses Python Playwright  
✅ **Theme Integration**: Uses existing theme CSS for consistency  
✅ **Smart Caching**: Hash-based regeneration skipping  
✅ **Configurable Scope**: Articles, pages, or both  
✅ **Error Handling**: Graceful failures with detailed logging  
✅ **Batch Processing**: Single Chromium instance for performance  
✅ **Standalone Testing**: CLI tool for manual template testing  
✅ **Comprehensive Tests**: Unit tests for core functionality  
✅ **Documentation**: Complete integration guide and examples  

## Development Ready

- Package structure follows Python best practices
- Comprehensive test suite with pytest
- Development tooling (linting, formatting)
- Example templates and configurations
- Integration documentation
- CLI tool for standalone testing

The plugin is now ready for development, testing, and integration with any Pelican site!
