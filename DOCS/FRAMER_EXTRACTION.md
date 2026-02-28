# Framer Site Extraction - User Guide

## Quick Start

To extract a Framer website (or any website), simply tell the agent:

```
"Extract this Framer site: https://example.framer.website"
```

The agent will automatically:
1. Download all HTML pages
2. Download all assets (images, CSS, JS, fonts, videos)
3. Rewrite all references to work locally
4. Save everything to `framer_extracts/<site-name>/`

## What Gets Extracted

### Pages
- All HTML pages discovered by following links from the starting URL
- Default limit: 40 pages (can be increased)

### Assets
- **Images**: PNG, JPG, JPEG, GIF, WebP, SVG, ICO, AVIF
- **Styles**: CSS files (with url() references rewritten)
- **Scripts**: JavaScript files (.js, .mjs)
- **Fonts**: WOFF, WOFF2, TTF, OTF, EOT
- **Media**: MP4, WebM, MP3, WAV videos and audio
- **Other**: PDF, JSON, XML, source maps

### What's Rewritten
- All `src`, `href`, `poster` attributes
- `srcset` for responsive images
- CSS `url()` references
- Query parameters preserved via filename hashing

## Examples

### Basic extraction
```
"Extract https://mysite.framer.website"
```

### With more pages
```
"Extract https://mysite.framer.website with max 100 pages"
```

### Shorthand
```
"Download this Framer site: mysite.framer.website"
```
(Protocol will be added automatically)

## Output Location

```
framer_extracts/
└── mysite-framer-website/
    ├── index.html          # Homepage
    ├── about/
    │   └── index.html      # Other pages
    └── __assets/           # All downloaded resources
        ├── mysite.framer.website/
        │   ├── images/
        │   ├── styles.css
        │   └── main.js
        └── fonts.googleapis.com/
            └── fonts/
```

## Viewing the Extracted Site

After extraction completes, open the local site in your browser:

```bash
open framer_extracts/<site-name>/index.html
```

Or double-click `index.html` in Finder.

## Limitations

### What Works
- ✅ Static HTML content
- ✅ CSS, images, fonts, videos
- ✅ JavaScript files
- ✅ Multiple pages (follows links)
- ✅ Responsive images (srcset)
- ✅ Google Fonts and external assets

### What Doesn't Work
- ❌ Password-protected sites
- ❌ Content requiring login
- ❌ Heavily JavaScript-rendered content (uses fetch, not a browser)
- ❌ Forms that submit to backend APIs
- ❌ Real-time features (websockets, etc.)

### Why?
The extractor uses Node.js `fetch()` to download pages, not a full browser. This means:
- Fast and lightweight
- Works great for static/mostly-static sites like Framer exports
- Won't execute JavaScript to render content

## Technical Details

### Architecture
This workflow follows the 3-layer system:
- **Directive**: `directives/extract_framer_site.md`
- **Orchestration**: Agent reads directive and calls execution script
- **Execution**:
  - `execution/extract_framer_site.py` (Python wrapper)
  - `execution/framer-extract.mjs` (Node.js crawler)

### How It Works
1. Python script validates URL and creates output directory
2. Node.js script crawls pages starting from provided URL
3. For each page:
   - Download HTML
   - Parse and extract all resource URLs
   - Download resources asynchronously
   - Rewrite references to relative paths
   - Save to disk
4. Continue until max pages reached or no more links found

### Requirements
- Node.js (v16+) - automatically checked
- No additional npm packages needed (uses built-in modules)

## Troubleshooting

### "Invalid URL"
Make sure to include the full URL with protocol:
- ✅ `https://example.framer.website`
- ❌ `example.framer.website` (will be auto-fixed by adding https://)

### "HTTP 403/404"
- Site may be down or protected
- Try opening URL in browser first to verify it's accessible

### "Expected HTML, got..."
- URL points to a file (PDF, image, etc.) not a webpage
- Use the homepage URL instead

### Site looks broken locally
- Check browser console for errors
- Some sites use absolute URLs that can't be rewritten
- API calls won't work without backend
- Check if JavaScript is enabled

### Too slow
- Reduce max pages: "Extract with max 10 pages"
- Large sites with many assets take time

## Advanced Usage

### Direct Script Usage
If you need to bypass the agent:

```bash
# Python wrapper (recommended)
python3 execution/extract_framer_site.py --url https://example.com --max-pages 50

# Direct Node.js (advanced)
node execution/framer-extract.mjs https://example.com ./output --max-pages 50
```

### Custom Output Location
The Python wrapper always uses `framer_extracts/<domain>/`. To use a custom location, run the Node.js script directly:

```bash
node execution/framer-extract.mjs https://example.com /path/to/output --max-pages 40
```

## Best Practices

1. **Start small**: Test with `--max-pages 5` first for large sites
2. **Check the source**: Open site in browser to verify it's accessible
3. **Review output**: Check `index.html` to ensure content looks correct
4. **Cleanup**: Delete `framer_extracts/` folder when done (it's gitignored)

## Version History

- **2025-02-12**: Initial workflow created with directive, Python wrapper, and documentation
