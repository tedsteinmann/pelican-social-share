# Pelican Social Card Plugin — Requirements

## 1) Overview
A Pelican plugin that generates **social share images (OG/Twitter)** during local builds.  
For any article with a `tagline:` field in front‑matter, the plugin:

1. Renders an **HTML card** (tagline text on the left, author photo on the right).  
2. Screenshots the card via **Puppeteer** to a **1200×675 PNG**.  
3. Exposes the path so templates set `og:image` / `twitter:image` automatically.

Fits a minimalist site (no hero images). Keeps **branding** consistent and **SEO** intact (title/description remain in metadata).

---

## 2) Goals / Non‑Goals
**Goals**
- Generate **local**, versionable OG images during `pelican content`.
- Consistent **layout**: answer left, portrait photo right; minimal, readable typography.
- Easy integration with **Pelican** templates and Makefile tasks.

**Non‑Goals**
- Server-side/on-demand OG generation (edge functions, Workers).
- AI image generation for complex illustrations.
- Modifying article titles/SEO `<title>` tags.

---

## 3) User Stories
- **As a site owner,** I want OG images created at build time so I can preview and version them before publishing.
- **As a social media viewer,** I want a clear, branded card with a recognizable photo and a concise answer to the post’s question so I immediately understand the value.
- **As a developer,** I want the plugin to fail gracefully and fall back to defaults without breaking the build.

---

## 4) Acceptance Criteria
- For any article with `tagline:` metadata, a PNG is generated at **1200×675** in `content/static/images/social/<slug>.png`.
- Card layout: **tagline text** on left; **portrait** on right; white/neutral background; high contrast.
---

## 5) Architecture & Components
### 5.1 Inputs
- Article front‑matter field: `tagline: "<short tagline here>"`.
- Site configuration in `pelicanconf.py` (dirs, model name, photo path, limits).

### 5.2 Processing
1. **HTML Card Generation** — Jinja‑free static HTML template with inline CSS:
   - Replaces `{{TAGLINE}}` and `{{SOCIAL_PHOTO}}` placeholders.
3. **Rasterization** — Headless Chromium via Puppeteer:
   - Loads HTML content and screenshots exactly at **1200×675** to PNG.

### 5.3 Outputs
- HTML preview page in `content/social/<slug>.html` (for debugging).
- Rasterized PNG in `content/static/images/social/<slug>.png`.
- `article.metadata["social_image"]` set to `/static/images/social/<slug>.png` for Jinja templates.

---

## 6) Configuration (pelicanconf.py)
```python
SOCIAL_IMAGE_DIR = "content/static/images/social"
SOCIAL_CARD_HTML_DIR = "content/social"
SOCIAL_PHOTO_PATH = "content/static/images/social/ted-portrait.png"
SOCIAL_SITE_URL = "https://ted.steinmann.me"
```

---

---

## 7) HTML Card Template (`social/card_template.html`)
- Canvas 1200×675, neutral background (#fff or off‑white).
- Left: `.tagline` uses large, bold type (e.g., 72px, 1.1 line-height).
- Right: fixed‑width column (~420px) with portrait image.
- Small meta/footer line for domain (e.g., `ted.steinmann.me`).

> Inline CSS only; no external assets to keep Puppeteer rendering deterministic.

---

## 8) Puppeteer Renderer (`social/render.js`)
- CLI: `node social/render.js --html=<in.html> --out=<out.png>`
- Launch with viewport 1200×675; `page.setContent(html, { waitUntil: "networkidle0" })`.
- `page.screenshot({ path })` to write PNG.
- Exit non‑zero on hard failures; plugin catches and logs warnings.

---

## 9) Pelican Plugin (`plugins/social_share/__init__.py`)
**Responsibilities**
- On `article_generator_finalized`:
  - For each article with `tagline` metadata:
    - Write **HTML** file to `SOCIAL_CARD_HTML_DIR`.
    - Screenshot to PNG in `SOCIAL_IMAGE_DIR` via Node script.
    - Set `article.metadata["social_image"]`.

**Error handling**
- If Puppeteer render fails:
  - Log per‑slug error; continue build.

**Extensibility**
- Allow different layouts (left/right swap; background color; badge text).

---

## 11) Theme Integration (Jinja `<head>`)
```jinja
{% if article %}
  {% set ogimg = article.metadata.social_image if article.metadata and article.metadata.social_image else '/static/images/social/' ~ article.slug ~ '.png' %}
{% else %}
  {% set ogimg = '/static/images/social/default.png' %}
{% endif %}
<meta property="og:image" content="{{ SITEURL }}{{ ogimg }}">
<meta name="twitter:image" content="{{ SITEURL }}{{ ogimg }}">
<meta name="twitter:card" content="summary_large_image">
```

---

## 12) Makefile Targets (Optional)
```make
# Debug one HTML → PNG
social-one:
	node social/render.js --html=$(HTML) --out=$(OUT)

# Full local build (plugin runs automatically)
build:
	pelican content -o output -s pelicanconf.py
```

---

## 13) Security & Privacy
- Portrait photo is a local file path resolved to `file://` URI for Puppeteer.
- No dynamic user input exposed to the renderer.

---

## 14) Performance
- Typical overhead: launching Chromium per image.  
  - Optimization: reuse a single Puppeteer browser for batch runs (future enhancement).  
- Keep HTML self‑contained; avoid external fonts to prevent network waits.

---

## 15) Testing Plan
- **Unit**: string truncation, prompt formatting, metadata detection.
- **Integration**: generate for a sample article, assert PNG exists, dimensions are 1200×675.
- **Manual**: open PNG locally; run Twitter/X Card Validator and LinkedIn Post Inspector.
- **Failure modes**: simulate missing model, missing photo, Puppeteer crash—build must complete with logged warnings.

---

## 16) Risks & Mitigations
- **Font differences** → use system fonts or bundle a tested font set.
- **Puppeteer install** → document Node/Chromium prerequisites; pin versions.

---

## 17) Rollout Plan
1. Build on a small set of posts; validate visuals.
2. Add to CI build; commit generated PNGs.
3. Monitor social previews; iterate on prompt/typography.
4. Optional: add a CLI flag to skip generation in CI if desired.

---

## 18) Future Enhancements
- Multi‑theme card layouts (dark/light, accent color per category).
- Batch browser reuse for faster runs.
- Toggle to include/exclude logo watermark.
- Switchable right/left portrait placement.
- Cloud/edge social generation parity for dynamic routes.

---

## 19) Directory Structure (proposed)
```
project/
├─ content/
│  ├─ static/images/social/                 # generated PNGs
│  ├─ social/           # generated HTML (debug)
│  └─ static/images/ted-portrait.jpg
├─ social/
│  ├─ card_template.html  # HTML template
│  └─ render.js           # Puppeteer renderer
├─ plugins/
│  └─ social_generator/__init__.py  # Pelican plugin
├─ pelicanconf.py
└─ Makefile
```

---

## 20) Definition of Done (DoD)
- Running the local build produces PNGs for all articles with `tagline:`.
- Preview looks correct for at least three sample posts.
- Meta tags reference the generated images.
- README updated with prerequisites and usage.
- All tasks in this doc completed and reviewed.
