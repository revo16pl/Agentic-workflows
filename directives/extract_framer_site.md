# Extract Framer Site

## Purpose
Extract and download a complete Framer website (or any website) including all HTML pages, assets (CSS, JS, images, fonts, videos), and rewrite all references to work locally.

## When to Use
- User provides a Framer website URL and wants to extract it
- User says "extract this Framer site", "download Framer website", "export from Framer"
- User wants a local copy of any website with all assets

## Inputs Required
- **url** (required): The starting URL of the Framer site (e.g., `https://example.framer.website`)
- **max_pages** (optional): Maximum number of pages to crawl (default: 40)

## Execution Tool
Use: `execution/extract_framer_site.py`

```bash
python execution/extract_framer_site.py --url <url> [--max-pages <number>]
```

## Output
- **Location**: `framer_extracts/<sanitized-domain-name>/`
- **Contents**:
  - `index.html` and other page HTML files
  - `__assets/` folder with all downloaded resources organized by domain
  - All references rewritten to relative paths
- **Summary**: The script reports number of pages and assets saved

## Process Flow
1. Validate the URL is accessible
2. Create output directory: `framer_extracts/<domain-name>/`
3. Run the Node.js extraction script (`execution/framer-extract.mjs`)
4. Crawl pages starting from the provided URL (respects max-pages limit)
5. Download and save all assets (images, CSS, JS, fonts, videos, etc.)
6. Rewrite all HTML/CSS references to use relative paths
7. Report completion with statistics

## Edge Cases & Known Issues

### Common Errors
**"Invalid URL"**:
- Ensure URL includes protocol (https://)
- Example: `https://example.framer.website` not `example.framer.website`

**"HTTP 403/404"**:
- Site may be password-protected or taken down
- Verify URL in browser first

**"Expected HTML, got..."**:
- URL points to a file (PDF, image) not a webpage
- Use the homepage URL instead

**Rate limiting/timeouts**:
- Some sites may block rapid requests
- The script includes user-agent: "framer-extract/1.0"
- If needed, reduce max-pages or add delays between requests

### Limitations
- **Max pages default**: 40 pages (configurable via --max-pages)
- **Authentication**: Does not handle password-protected sites
- **Dynamic content**: JavaScript-rendered content may not be fully captured (uses fetch, not a browser)
- **Cross-origin assets**: Only downloads assets from the same origin or explicitly linked

### Asset Handling
- **Supported formats**: HTML, CSS, JS, images (PNG, JPG, WebP, SVG, etc.), fonts (WOFF, TTF, etc.), videos (MP4, WebM), audio, PDFs
- **CSS url() rewriting**: Automatically rewrites CSS background images and fonts
- **srcset handling**: Properly handles responsive image srcset attributes
- **Query parameters**: Preserved via hash in filename (e.g., `image__q8a7f3b2.png`)

## Output Structure Example
```
framer_extracts/
└── example-framer-website/
    ├── index.html
    ├── about/
    │   └── index.html
    ├── contact/
    │   └── index.html
    └── __assets/
        ├── example.framer.website/
        │   ├── images/
        │   ├── styles.css
        │   └── main.js
        └── fonts.googleapis.com/
            └── css2__q1a2b3c4.css
```

## Success Criteria
- Output directory created in `framer_extracts/`
- All pages saved as HTML files
- All assets downloaded to `__assets/`
- Summary shows pages and assets count
- User can open `index.html` in browser and site displays correctly

## User Communication
After completion, provide:
1. Path to the extracted site
2. Number of pages extracted
3. Number of assets downloaded
4. Instructions: "Open `index.html` in your browser to view the site"

## Self-Annealing Notes
- **2025-02-12**: Initial directive created. Node.js script (`framer-extract.mjs`) already exists and is well-structured.
