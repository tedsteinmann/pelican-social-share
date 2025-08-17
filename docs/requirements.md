# Pelican Social Card Plugin — Requirements (Playwright Implementation)

## 1) Overview
A Pelican plugin that generates **Open Graph / Twitter social share images** during local builds.  
For each selected article or page (configurable) with a `tagline:` metadata field:

1. Renders an HTML card using the site’s existing Pelican **theme CSS only** via a dedicated template `social_card.html`.
2. Saves that HTML (versionable) to `content/social/<slug>.html`.
3. Uses **Python Playwright (Chromium)** to screenshot the HTML at **1200×675** into `content/static/images/social/<slug>.png`.
4. Exposes the path (`article.metadata["social_image"]`) so templates set `og:image` / `twitter:image`.

No Node / Puppeteer. No additional CSS file: layout relies solely on the active theme’s CSS (the template may use existing utility classes / structure provided by the theme).

---

## 2) Goals / Non‑Goals
**Goals**
- Deterministic, theme‑consistent OG images.
- Single Chromium session; fast batch capture.
- Versionable HTML + PNG artifacts under `content/`.
- Configurable scope: articles, pages, or both.

**Non‑Goals**
- Runtime/on‑demand cloud generation.
- Custom inline/standalone CSS (beyond what theme already ships).
- Complex dynamic art beyond text + portrait.

---

## 3) User Stories
- **As a site owner,** I want OG images created at build time so I can preview and version them before publishing.
- **As a social media viewer,** I want a clear, branded card with a recognizable photo and a concise answer to the post’s question so I immediately understand the value.
- **As a developer,** I want the plugin to fail gracefully and fall back to defaults without breaking the build.

---

## 4) Acceptance Criteria
- For each selected content object with `tagline:` a PNG `content/static/images/social/<slug>.png` (1200×675) exists after build (unless skipped by hash).
- Corresponding HTML source at `content/social/<slug>.html` reflects the rendered card using `social_card.html`.
- `metadata["social_image"] == "/static/images/social/<slug>.png"`.
- Build continues on failures; logs warnings.

---

## 5) Architecture & Components

### 5.1 Inputs
- Front‑matter: `tagline: "<short tagline>"`.
- Config (pelicanconf.py) controlling:
  - Directories
  - Scope (articles/pages)
  - Template name
  - Portrait image path
  - Hash‑based regeneration skipping
  - Optional wait selector

### 5.2 Processing
1. During `article_generator_finalized` (and page generator if enabled):
   - Select objects (articles/pages) per scope.
   - For each with `tagline`, Jinja‑render `social_card.html` with context into `content/social/<slug>.html`.
   - Set `metadata["social_image"]` (relative path to eventual PNG).
2. After Pelican write (`signals.finalized`):
   - Start lightweight HTTP server rooted at **output** (ensures theme CSS/assets resolve as in final site).
   - Launch single headless Chromium via Playwright.
   - For each generated `content/social/<slug>.html`:
     - Build URL: `http://127.0.0.1:<port>/social/<slug>.html` (the file gets copied to output by normal content processing on next build cycle OR optionally we can render a parallel copy directly into `output/social/`; see Implementation Note).
     - Set viewport 1200×675; wait for network idle (and optional selector).
     - Screenshot to `content/static/images/social/<slug>.png`.
     - Store/update hash sidecar if enabled for skip logic.

### 5.3 Outputs
- HTML: `content/social/<slug>.html`
- PNG: `content/static/images/social/<slug>.png`
- Hash sidecar: `content/static/images/social/<slug>.png.hash` (optional)
- Metadata key: `social_image` (value: `/static/images/social/<slug>.png`)

---

## 6) Configuration (pelicanconf.py)
```python
SOCIAL_CARD_HTML_DIR = "content/social"
SOCIAL_IMAGE_DIR = "content/static/images/social"
SOCIAL_TEMPLATE_NAME = "social_card.html"   # must exist in theme templates
SOCIAL_PORTRAIT_PATH = "content/static/images/social/ted-portrait.png"

# Scope: "articles", "pages", or "both"
SOCIAL_SCOPE = "articles"

# Screenshot
SOCIAL_VIEWPORT = (1200, 675)
SOCIAL_DEVICE_SCALE_FACTOR = 1
SOCIAL_WAIT_UNTIL = "networkidle"   # passed to page.goto
SOCIAL_WAIT_SELECTOR = None         # e.g. "#social-card-ready" if used

# Regeneration control
SOCIAL_HASH_SKIP = True
SOCIAL_HASH_VERSION = "v1"

# Toggle (set True to disable screenshot step, leaving only metadata + HTML)
SOCIAL_DISABLE_SCREENSHOT = False
```

---

## 7) HTML Card Template (`social/card_template.html`)
- Canvas 1200×675, neutral background (#fff or off‑white).
- Left: `.tagline` uses large, bold type (e.g., 72px, 1.1 line-height).
- Right: fixed‑width column (~420px) with portrait image.
- Small meta/footer line for domain (e.g., `ted.steinmann.me`).

> Inline CSS only; no external assets to keep Puppeteer rendering deterministic.

---

## 8) Playwright Renderer (`social/render.py`)
- CLI: `python social/render.py --html=<in.html> --out=<out.png>`
- Launch with viewport 1200×675; wait for network idle.
- `page.screenshot(path=<out.png>)` to write PNG.
- Exit non‑zero on hard failures; plugin catches and logs warnings.

---

## 9) Pelican Plugin (`plugins/social_share/__init__.py`)
**Responsibilities**
- On `article_generator_finalized`:
  - For each article with `tagline` metadata:
    - Write **HTML** file to `SOCIAL_CARD_HTML_DIR`.
    - Screenshot to PNG in `SOCIAL_IMAGE_DIR` via Python Playwright.
    - Set `article.metadata["social_image"]`.

**Error handling**
- If Playwright render fails:
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
	python social/render.py --html=$(HTML) --out=$(OUT)

# Full local build (plugin runs automatically)
build:
	pelican content -o output -s pelicanconf.py
```

---

## 13) Security & Privacy
- Portrait photo is a local file path resolved to `file://` URI for Playwright.
- No dynamic user input exposed to the renderer.

---

## 14) Performance
- Typical overhead: launching Chromium per image.  
  - Optimization: reuse a single Playwright browser for batch runs (future enhancement).  
- Keep HTML self‑contained; avoid external fonts to prevent network waits.

---

## 15) Testing Plan
- **Unit**: string truncation, prompt formatting, metadata detection.
- **Integration**: generate for a sample article, assert PNG exists, dimensions are 1200×675.
- **Manual**: open PNG locally; run Twitter/X Card Validator and LinkedIn Post Inspector.
- **Failure modes**: simulate missing model, missing photo, Playwright crash—build must complete with logged warnings.

---

## 16) Risks & Mitigations
- **Font differences** → use system fonts or bundle a tested font set.
- **Playwright install** → document Python/Chromium prerequisites; pin versions.

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
│  └─ render.py           # Playwright renderer
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
