# Optimize Media for Web

## Goal
Convert and optimize images and videos for web usage, reducing file size while maintaining quality.

## Inputs
- Media files placed in `media_optimization/media_optimization_input/` directory
- Supported formats:
  - **Images**: JPG, JPEG, PNG, GIF, BMP, TIFF
  - **Videos**: MP4, MOV, AVI, MKV, WEBM

## Execution Script
`execution/optimize_media.py`

## Process

### For Images:
1. Convert to WebP format (best compression for web)
2. Optimize with quality setting of 85 (configurable)
3. Generate multiple sizes for responsive images:
   - Original size
   - 1920px wide (desktop)
   - 1024px wide (tablet)
   - 640px wide (mobile)
4. Preserve aspect ratio

### For Videos:
1. Convert to MP4 with H.264 codec (universal compatibility)
2. Optimize settings:
   - CRF 23 (constant rate factor - good quality/size balance)
   - Max width 1920px for desktop
   - Audio: AAC codec, 128kbps
3. Optional: Generate WebM version for modern browsers
4. Create thumbnail (first frame as WebP)

## Output
- Optimized files saved to `media_optimization/Media_optimization_output/` directory
- Naming convention:
  - Images: `{original_name}.webp`, `{original_name}_1920.webp`, etc.
  - Videos: `{original_name}_optimized.mp4`
  - Thumbnails: `{original_name}_thumb.webp`
- Terminal report showing:
  - Original file size
  - Optimized file size
  - Percentage reduction
  - Processing time

## Usage
```bash
# Place files in media_optimization/media_optimization_input/ folder
cp /path/to/image.jpg media_optimization/media_optimization_input/
cp /path/to/video.mp4 media_optimization/media_optimization_input/

# Run optimization
python execution/optimize_media.py

# Optional: specify quality (1-100, default 85)
python execution/optimize_media.py --quality 90

# Optional: skip responsive sizes (only optimize original)
python execution/optimize_media.py --no-responsive

# Optional: generate WebM for videos
python execution/optimize_media.py --webm
```

## Edge Cases & Error Handling

1. **Empty input folder**
   - Script prints warning and exits gracefully

2. **Unsupported file format**
   - Skip file with warning message
   - Continue processing other files

3. **FFmpeg not installed** (for video)
   - Print clear error message with installation instructions
   - Process images only

4. **Corrupted/unreadable file**
   - Log error for specific file
   - Continue with remaining files

5. **Output already exists**
   - Overwrite with confirmation
   - Or skip if `--skip-existing` flag is used

6. **Insufficient disk space**
   - Check available space before processing
   - Warn if less than 2x input size available

## Dependencies
- Python 3.7+
- Pillow (PIL) - image processing
- ffmpeg-python - video processing
- FFmpeg binary (system dependency)

## Installation
```bash
# Python packages
pip install -r requirements.txt

# FFmpeg (macOS)
brew install ffmpeg

# FFmpeg (Linux)
sudo apt-get install ffmpeg
```

## Performance Notes
- Images: ~0.5-2 seconds per file
- Videos: Depends on length and resolution (estimate: 1x realtime for 1080p)
- Process runs single-threaded (can be parallelized if needed)

## Common Issues

**Issue**: WebP images not displaying in older browsers
**Solution**: Provide fallback using `<picture>` element with JPEG

**Issue**: Video file size still too large
**Solution**: Lower CRF value (higher = smaller file but lower quality), or reduce resolution

**Issue**: Colors look different after optimization
**Solution**: Ensure color profile is preserved (script handles this automatically)

## Future Enhancements
- [ ] Batch processing with progress bar
- [ ] Auto-generate `<picture>` HTML snippets
- [ ] AVIF format support (newer, better compression)
- [ ] Parallel processing for multiple files
- [ ] Custom preset profiles (e.g., "high-quality", "small-size")
- [ ] Integration with cloud storage (S3, CloudFlare R2)
