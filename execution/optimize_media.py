#!/usr/bin/env python3
"""
Media Optimization Script
Optimizes images and videos for web usage.
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image
import time

# Try to import ffmpeg, but don't fail if not available
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

# Directories
INPUT_DIR = Path("media_optimization/media_optimization_input")
OUTPUT_DIR = Path("media_optimization/Media_optimization_output")

# Image settings
IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
VIDEO_FORMATS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

# Responsive image sizes (width in pixels)
RESPONSIVE_SIZES = {
    'desktop': 1920,
    'tablet': 1024,
    'mobile': 640
}


def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    if not FFMPEG_AVAILABLE:
        return False
    try:
        ffmpeg.probe('pipe:')
    except ffmpeg.Error:
        pass
    except FileNotFoundError:
        return False
    return True


def optimize_image(input_path, output_dir, quality=85, responsive=True):
    """
    Optimize an image file.

    Args:
        input_path: Path to input image
        output_dir: Directory to save optimized images
        quality: WebP quality (1-100)
        responsive: Generate multiple sizes
    """
    try:
        img = Image.open(input_path)

        # Convert RGBA to RGB if necessary (WebP can handle both, but we optimize)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        original_size = input_path.stat().st_size
        total_output_size = 0

        # Output filename (without extension)
        base_name = input_path.stem

        # Save original size as WebP
        output_path = output_dir / f"{base_name}.webp"
        img.save(output_path, 'WEBP', quality=quality, method=6)
        output_size = output_path.stat().st_size
        total_output_size += output_size

        print(f"\n✓ {input_path.name}")
        print(f"  Original: {format_size(original_size)}")
        print(f"  Optimized: {format_size(output_size)} ({output_path.name})")
        print(f"  Saved: {format_size(original_size - output_size)} ({((original_size - output_size) / original_size * 100):.1f}%)")

        # Generate responsive sizes
        if responsive and (img.width > RESPONSIVE_SIZES['mobile']):
            print(f"  Responsive versions:")
            for size_name, max_width in RESPONSIVE_SIZES.items():
                if img.width > max_width:
                    # Calculate new dimensions maintaining aspect ratio
                    ratio = max_width / img.width
                    new_width = max_width
                    new_height = int(img.height * ratio)

                    # Resize image
                    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Save
                    responsive_path = output_dir / f"{base_name}_{max_width}w.webp"
                    resized.save(responsive_path, 'WEBP', quality=quality, method=6)
                    responsive_size = responsive_path.stat().st_size
                    total_output_size += responsive_size

                    print(f"    - {size_name} ({max_width}px): {format_size(responsive_size)}")

        return original_size, total_output_size

    except Exception as e:
        print(f"✗ Error processing {input_path.name}: {e}")
        return 0, 0


def optimize_video(input_path, output_dir, generate_webm=False):
    """
    Optimize a video file.

    Args:
        input_path: Path to input video
        output_dir: Directory to save optimized video
        generate_webm: Also generate WebM version
    """
    if not FFMPEG_AVAILABLE:
        print(f"⚠ Skipping {input_path.name} - ffmpeg-python not installed")
        return 0, 0

    try:
        original_size = input_path.stat().st_size
        base_name = input_path.stem

        # Output path for MP4
        output_path = output_dir / f"{base_name}_optimized.mp4"

        # Probe input to get video info
        probe = ffmpeg.probe(str(input_path))
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])

        print(f"\n⏳ Processing {input_path.name} (this may take a while)...")

        # Build ffmpeg command
        stream = ffmpeg.input(str(input_path))

        # Scale down if wider than 1920px
        if width > 1920:
            stream = ffmpeg.filter(stream, 'scale', 1920, -2)

        # Output settings
        stream = ffmpeg.output(
            stream,
            str(output_path),
            vcodec='libx264',
            crf=23,
            preset='medium',
            acodec='aac',
            audio_bitrate='128k',
            **{'movflags': '+faststart'}  # Enable streaming
        )

        # Run conversion
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        output_size = output_path.stat().st_size
        total_output_size = output_size

        print(f"✓ {input_path.name}")
        print(f"  Original: {format_size(original_size)}")
        print(f"  Optimized (MP4): {format_size(output_size)}")
        print(f"  Saved: {format_size(original_size - output_size)} ({((original_size - output_size) / original_size * 100):.1f}%)")

        # Generate WebM if requested
        if generate_webm:
            webm_path = output_dir / f"{base_name}_optimized.webm"
            stream = ffmpeg.input(str(input_path))

            if width > 1920:
                stream = ffmpeg.filter(stream, 'scale', 1920, -2)

            stream = ffmpeg.output(
                stream,
                str(webm_path),
                vcodec='libvpx-vp9',
                crf=30,
                acodec='libopus',
                audio_bitrate='128k'
            )

            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            webm_size = webm_path.stat().st_size
            total_output_size += webm_size
            print(f"  WebM version: {format_size(webm_size)}")

        # Generate thumbnail
        thumbnail_path = output_dir / f"{base_name}_thumb.webp"
        stream = ffmpeg.input(str(input_path), ss=1)
        stream = ffmpeg.output(stream, str(thumbnail_path), vframes=1, **{'q:v': 2})
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        print(f"  Thumbnail: {thumbnail_path.name}")

        return original_size, total_output_size

    except Exception as e:
        print(f"✗ Error processing {input_path.name}: {e}")
        return 0, 0


def main():
    parser = argparse.ArgumentParser(description='Optimize images and videos for web')
    parser.add_argument('--quality', type=int, default=85, help='Image quality (1-100, default: 85)')
    parser.add_argument('--responsive', action='store_true', help='Generate responsive image sizes (disabled by default)')
    parser.add_argument('--webm', action='store_true', help='Generate WebM versions of videos')
    args = parser.parse_args()

    # Validate quality
    if not 1 <= args.quality <= 100:
        print("Error: Quality must be between 1 and 100")
        sys.exit(1)

    # Check directories
    if not INPUT_DIR.exists():
        print(f"Error: Input directory '{INPUT_DIR}' not found")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Get all files from input directory
    files = [f for f in INPUT_DIR.iterdir() if f.is_file()]

    if not files:
        print(f"⚠ No files found in '{INPUT_DIR}' directory")
        print(f"   Place your images or videos there and run again.")
        sys.exit(0)

    # Check FFmpeg for video processing
    has_ffmpeg = check_ffmpeg()
    if not has_ffmpeg:
        print("⚠ FFmpeg not available - video processing will be skipped")
        print("  Install: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
        print()

    # Process files
    print(f"\n{'='*60}")
    print(f"  MEDIA OPTIMIZATION")
    print(f"{'='*60}")
    print(f"Quality: {args.quality}")
    print(f"Responsive: {args.responsive}")
    print(f"WebM: {args.webm}")
    print(f"{'='*60}\n")

    total_original = 0
    total_optimized = 0
    processed_count = 0
    skipped_count = 0

    start_time = time.time()

    for file_path in files:
        ext = file_path.suffix.lower()

        if ext in IMAGE_FORMATS:
            orig, opt = optimize_image(
                file_path,
                OUTPUT_DIR,
                quality=args.quality,
                responsive=args.responsive
            )
            total_original += orig
            total_optimized += opt
            if orig > 0:
                processed_count += 1
            else:
                skipped_count += 1

        elif ext in VIDEO_FORMATS:
            if has_ffmpeg:
                orig, opt = optimize_video(file_path, OUTPUT_DIR, generate_webm=args.webm)
                total_original += orig
                total_optimized += opt
                if orig > 0:
                    processed_count += 1
                else:
                    skipped_count += 1
            else:
                print(f"⚠ Skipping {file_path.name} - FFmpeg not available")
                skipped_count += 1
        else:
            print(f"⚠ Skipping {file_path.name} - unsupported format")
            skipped_count += 1

    # Summary
    elapsed_time = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"Processed: {processed_count} files")
    print(f"Skipped: {skipped_count} files")
    print(f"Total original size: {format_size(total_original)}")
    print(f"Total optimized size: {format_size(total_optimized)}")
    if total_original > 0:
        print(f"Total saved: {format_size(total_original - total_optimized)} ({((total_original - total_optimized) / total_original * 100):.1f}%)")
    print(f"Time: {elapsed_time:.1f}s")
    print(f"\n✓ Optimized files saved to '{OUTPUT_DIR}/'")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
