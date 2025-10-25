#!/usr/bin/env python3
"""
Simple M3U Cleaner - Downloads BuddyChewChew's playlist and removes adult content
"""

import requests
import sys
import argparse

def download_m3u(url):
    """Download the M3U playlist"""
    try:
        print(f"Downloading M3U from: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        print(f"Downloaded {len(response.text)} characters")
        return response.text
    except Exception as e:
        print(f"Error downloading M3U: {e}")
        return None

def filter_adult_content(m3u_content):
    """Filter out adult/XXX content from M3U"""
    lines = m3u_content.split('\n')
    filtered_lines = []
    skip_channel = False

    for line in lines:
        line_lower = line.lower()

        # Check for adult content markers
        if ('#extgrp:daddylive xxx' in line_lower or
            'tvg-id="adult.section.dummy.us"' in line_lower or
            ('18+' in line and '#extinf:' in line_lower) or
            ('porn' in line and '#extinf:' in line_lower) or
            ('sex' in line and '#extinf:' in line_lower)):
            # Skip this channel (next 2 lines: EXTINF and URL)
            skip_channel = True
            continue

        # If we're skipping a channel, skip the URL line too
        if skip_channel and not line.startswith('#'):
            skip_channel = False
            continue

        # Reset skip flag for next channel
        if line.startswith('#extinf:'):
            skip_channel = False

        filtered_lines.append(line)

    filtered_content = '\n'.join(filtered_lines)

    # Count channels
    channel_count = filtered_content.count('#EXTINF:')
    print(f"Filtered to {channel_count} clean channels")

    return filtered_content

def save_filtered_m3u(content, filename):
    """Save the filtered M3U content"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved filtered M3U to: {filename}")
    return filename

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Simple M3U Adult Content Filter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python iptv_extractor.py                    # Download and filter default M3U
  python iptv_extractor.py --source URL       # Use custom M3U source
  python iptv_extractor.py --output FILE      # Custom output filename
        """
    )

    parser.add_argument(
        "--source",
        type=str,
        default="https://raw.githubusercontent.com/BuddyChewChew/combine-remote-playlists/refs/heads/main/combined_playlist.m3u",
        help="M3U playlist source URL"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="filtered_playlist.m3u",
        help="Output filename (default: filtered_playlist.m3u)"
    )

    args = parser.parse_args()

    # Download M3U
    m3u_content = download_m3u(args.source)
    if not m3u_content:
        sys.exit(1)

    # Filter adult content
    print("Filtering adult content...")
    filtered_content = filter_adult_content(m3u_content)

    # Save filtered M3U
    save_filtered_m3u(filtered_content, args.output)

    print("\n✓ M3U playlist successfully filtered!")
    print("Adult/XXX content has been removed.")

if __name__ == "__main__":
    main()
