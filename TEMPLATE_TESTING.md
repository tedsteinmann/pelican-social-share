# Social Card Template Testing

This directory contains tools for testing and developing the social card template.

## Quick Start

Generate a sample social card to test your template design:

```bash
python generate_sample.py
```

This creates `sample_output/social_card_sample.html` which you can open in your browser.

### Add Your Own Portrait

To test with your own photo instead of the fallback placeholder:

1. Add your portrait to the `examples/` directory with one of these names:
   - `examples/portrait.jpg`
   - `examples/portrait.png` 
   - `examples/portrait.svg`
   - `examples/my_portrait.jpg`
   - `examples/my_portrait.png`

2. Run the generator - it will automatically detect and use your photo:
   ```bash
   python generate_sample.py
   ```

The script checks for portraits in the order listed above and uses the first one found. If none exist, it falls back to an embedded SVG placeholder.

**Note**: Portrait files are ignored by git, so contributors can add their own without affecting the repository.

## Debug Mode

To see the mobile-safe zone (630x630 square) outlined in red:

```bash
python generate_sample.py --debug
```

Or add `?debug` to any generated HTML file URL.

### Check Portrait Status

To see which portrait files are being checked and which exist:

```bash
python generate_sample.py --list-portraits
```

## Files

- `generate_sample.py` - Sample generator script
- `examples/social_card.html` - Template file
- `examples/test_portrait.svg` - Test portrait image
- `sample_output/` - Generated samples (created when you run the script)

## Template Design Guidelines

The template uses a 1200x630 canvas with a centered 630x630 safe zone:

- **Canvas**: 1200x630 (optimal for Facebook, Twitter, LinkedIn)
- **Safe Zone**: 630x630 centered square (everything important goes here)
- **Mobile**: Many mobile apps crop to a square, so the safe zone ensures your content is always visible

### Design Tips

1. Keep all critical text and logos within the safe zone
2. The safe zone is outlined in red when using debug mode
3. Test with very long taglines to ensure proper wrapping
4. Portrait images are unconstrained but positioned within the safe zone

## Testing Your Changes

1. Edit `examples/social_card.html`
2. Run `python generate_sample.py --debug`
3. Open the generated file in your browser
4. Verify all important content is within the red dashed outline
5. Test on mobile or with browser developer tools in mobile view

## Integration

When you're happy with your template design, copy it to your Pelican theme's templates directory and configure the plugin in your `pelicanconf.py`.
