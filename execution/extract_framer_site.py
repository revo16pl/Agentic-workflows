#!/usr/bin/env python3
"""
Extract Framer Site - Execution Script

Wrapper for framer-extract.mjs that handles directory setup and provides
a clean Python interface for the agent orchestration layer.

Usage:
    python execution/extract_framer_site.py --url <url> [--max-pages <number>]

Example:
    python execution/extract_framer_site.py --url https://example.framer.website --max-pages 60
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def sanitize_domain(url: str) -> str:
    """
    Convert URL to safe directory name.

    Args:
        url: Full URL to sanitize

    Returns:
        Safe directory name (e.g., "example-framer-website")
    """
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    # Remove www. prefix and replace dots/special chars with hyphens
    domain = re.sub(r'^www\.', '', domain)
    domain = re.sub(r'[^\w\-]', '-', domain)
    domain = re.sub(r'-+', '-', domain).strip('-')
    return domain.lower()


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"

    # Add https:// if no protocol specified
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "Invalid URL format - no domain found"
        return True, url
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description='Extract a Framer website (or any website) with all assets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python execution/extract_framer_site.py --url https://example.framer.website
  python execution/extract_framer_site.py --url example.framer.website --max-pages 100
        """
    )
    parser.add_argument(
        '--url',
        required=True,
        help='URL of the Framer site to extract (e.g., https://example.framer.website)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=40,
        help='Maximum number of pages to crawl (default: 40)'
    )

    args = parser.parse_args()

    # Validate URL
    is_valid, result = validate_url(args.url)
    if not is_valid:
        print(f"❌ Error: {result}", file=sys.stderr)
        sys.exit(1)

    url = result
    print(f"🔗 URL: {url}")

    # Validate max-pages
    if args.max_pages <= 0:
        print("❌ Error: --max-pages must be a positive number", file=sys.stderr)
        sys.exit(1)

    # Setup paths
    project_root = Path(__file__).parent.parent
    extracts_dir = project_root / "framer_extracts"
    domain_name = sanitize_domain(url)
    output_dir = extracts_dir / domain_name

    # Create base extracts directory
    extracts_dir.mkdir(exist_ok=True)

    # Path to Node.js extraction script
    node_script = project_root / "execution" / "framer-extract.mjs"

    if not node_script.exists():
        print(f"❌ Error: Node.js script not found at {node_script}", file=sys.stderr)
        sys.exit(1)

    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Max pages: {args.max_pages}")
    print()

    # Build command
    cmd = [
        "node",
        str(node_script),
        url,
        str(output_dir),
        "--max-pages",
        str(args.max_pages)
    ]

    try:
        print("🚀 Starting extraction...")
        print()

        # Run the Node.js script
        result = subprocess.run(
            cmd,
            cwd=project_root,
            check=True,
            text=True,
            capture_output=False  # Stream output in real-time
        )

        print()
        print("✅ Extraction completed successfully!")
        print(f"📂 Output location: {output_dir}")
        print()
        print("To view the site:")
        print(f"  open {output_dir / 'index.html'}")

        return 0

    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ Extraction failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ Error: Node.js not found. Please install Node.js first:", file=sys.stderr)
        print("  https://nodejs.org/", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print("⚠️  Extraction cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
