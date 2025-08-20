"""Tests for the pelican_social_share plugin."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pelican_social_share.plugin import (
    make_content_hash,
    save_content_hash,
    should_skip_generation,
)


class TestHashFunctions:
    """Test hash-related functions."""
    
    def test_make_content_hash(self):
        """Test hash generation."""
        hash1 = make_content_hash("test-slug", "Test tagline", "v1")
        hash2 = make_content_hash("test-slug", "Test tagline", "v1")
        hash3 = make_content_hash("test-slug", "Different tagline", "v1")
        hash4 = make_content_hash("test-slug", "Test tagline", "v2")
        
        # Same inputs should produce same hash
        assert hash1 == hash2
        # Different inputs should produce different hashes
        assert hash1 != hash3
        assert hash1 != hash4
        # Hash should be reasonable length
        assert len(hash1) == 16
    
    def test_save_and_check_hash(self, tmp_path):
        """Test saving and checking content hash."""
        png_path = tmp_path / "test.png"
        png_path.touch()  # Create the PNG file
        
        slug = "test-slug"
        tagline = "Test tagline"
        version = "v1"
        
        # Initially should not skip (no hash file)
        assert not should_skip_generation(str(png_path), slug, tagline, version)
        
        # Save hash
        save_content_hash(str(png_path), slug, tagline, version)
        
        # Now should skip (hash matches)
        assert should_skip_generation(str(png_path), slug, tagline, version)
        
        # Different tagline should not skip
        assert not should_skip_generation(str(png_path), slug, "Different", version)
        
        # Different version should not skip
        assert not should_skip_generation(str(png_path), slug, tagline, "v2")
    
    def test_should_skip_missing_files(self, tmp_path):
        """Test skip behavior when files are missing."""
        png_path = tmp_path / "missing.png"
        
        # Missing PNG file should not skip
        assert not should_skip_generation(str(png_path), "slug", "tagline", "v1")
        
        # Create PNG but no hash file
        png_path.touch()
        assert not should_skip_generation(str(png_path), "slug", "tagline", "v1")


class TestRegisterFunction:
    """Test plugin registration."""
    
    @patch('pelican_social_share.plugin.signals')
    def test_register(self, mock_signals):
        """Test that register connects the right signals."""
        from pelican_social_share.plugin import register
        
        register()
        
        # Check that all required signals are connected
        assert mock_signals.article_generator_finalized.connect.called
        assert mock_signals.page_generator_finalized.connect.called
        assert mock_signals.finalized.connect.called


class MockGenerator:
    """Mock generator for testing."""
    
    def __init__(self, settings, articles=None, pages=None):
        self.settings = settings
        self.articles = articles or []
        self.pages = pages or []
        self.logger = MagicMock()
        self.env = MagicMock()


class MockContent:
    """Mock content object for testing."""
    
    def __init__(self, slug, metadata=None):
        self.slug = slug
        self.metadata = metadata or {}


class TestBuildSocialPages:
    """Test social page building functionality."""
    
    @patch('pelican_social_share.plugin.logger')
    def test_build_social_pages_no_template(self, mock_logger, mock_pelican_settings):
        """Test behavior when template is missing."""
        generator = MockGenerator(mock_pelican_settings)
        generator.env.get_template.side_effect = Exception("Template not found")
        
        from pelican_social_share.plugin import build_social_pages
        
        # Should not raise exception
        build_social_pages(generator, [])
        
        # Should log warning
        mock_logger.warning.assert_called_once()
    
    def test_build_social_pages_no_tagline(self, mock_pelican_settings, sample_template_content):
        """Test that content without tagline is skipped."""
        # Setup mock generator
        generator = MockGenerator(mock_pelican_settings)
        mock_template = MagicMock()
        generator.env.get_template.return_value = mock_template
        
        # Create content without tagline
        content = MockContent("test-slug", {})
        
        from pelican_social_share.plugin import build_social_pages
        
        build_social_pages(generator, [content])
        
        # Template should not be rendered
        mock_template.render.assert_not_called()
    
    def test_build_social_pages_with_tagline(self, mock_pelican_settings, sample_template_content, tmp_path):
        """Test successful social page building."""
        # Setup directories
        social_dir = tmp_path / "social"
        output_social_dir = tmp_path / "output" / "social"
        social_dir.mkdir(parents=True)
        output_social_dir.mkdir(parents=True)
        
        # Update settings with real paths
        mock_pelican_settings["SOCIAL_CARD_HTML_DIR"] = str(social_dir)
        mock_pelican_settings["OUTPUT_PATH"] = str(tmp_path / "output")
        
        # Setup mock generator
        generator = MockGenerator(mock_pelican_settings)
        mock_template = MagicMock()
        mock_template.render.return_value = sample_template_content
        generator.env.get_template.return_value = mock_template
        
        # Create content with tagline
        content = MockContent("test-slug", {"tagline": "Test tagline"})
        
        from pelican_social_share.plugin import build_social_pages
        
        build_social_pages(generator, [content])
        
        # Check that template was rendered
        mock_template.render.assert_called_once()
        
        # Check that HTML files were created
        assert (social_dir / "test-slug.html").exists()
        assert (output_social_dir / "test-slug.html").exists()
        
        # Check that metadata was set
        expected_path = "/static/images/test-slug-social-share.png"
        assert content.metadata["social_image"] == expected_path
        assert content.metadata["image"] == expected_path

    def test_build_social_pages_skip_existing_image(self, mock_pelican_settings, sample_template_content, tmp_path):
        """Test that content with existing image metadata is skipped."""
        # Setup directories
        social_dir = tmp_path / "social"
        output_social_dir = tmp_path / "output" / "social"
        social_dir.mkdir(parents=True)
        output_social_dir.mkdir(parents=True)

        # Update settings with real paths
        mock_pelican_settings["SOCIAL_CARD_HTML_DIR"] = str(social_dir)
        mock_pelican_settings["OUTPUT_PATH"] = str(tmp_path / "output")

        # Setup mock generator
        generator = MockGenerator(mock_pelican_settings)
        mock_template = MagicMock()
        mock_template.render.return_value = sample_template_content
        generator.env.get_template.return_value = mock_template

        # Create content with tagline AND existing image
        content = MockContent("test-slug", {
            "tagline": "Test tagline",
            "image": "/existing/image.jpg"  # Has existing image
        })

        from pelican_social_share.plugin import build_social_pages

        build_social_pages(generator, [content])

        # Check that template was NOT rendered (content was skipped)
        mock_template.render.assert_not_called()

        # Check that HTML files were NOT created
        assert not (social_dir / "test-slug.html").exists()
        assert not (output_social_dir / "test-slug.html").exists()

        # Check that social_image metadata was NOT set
        assert "social_image" not in content.metadata
        
        # Check that the original image attribute is preserved
        assert content.metadata["image"] == "/existing/image.jpg"


# Integration test that requires manual verification
@pytest.mark.skip(reason="Requires Playwright and manual verification")
class TestScreenshotGeneration:
    """Test screenshot generation with Playwright."""
    
    def test_full_pipeline(self, tmp_path):
        """Test the full pipeline from HTML to PNG."""
        # This would require setting up a full Pelican environment
        # and running the actual screenshot generation
        pass


if __name__ == "__main__":
    pytest.main([__file__])
