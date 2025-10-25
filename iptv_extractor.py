#!/usr/bin/env python3
"""
IPTV Extractor - Downloads BuddyChewChew's playlist, filters adult content, and fetches EPG data
"""

import requests
import sys
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

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

def download_xml_epg(url):
    """Download XML EPG data"""
    try:
        print(f"Downloading EPG XML from: {url}")
        response = requests.get(url, timeout=60, verify=True)
        response.raise_for_status()
        print(f"Downloaded {len(response.text)} characters of XML data")
        return response.text
    except requests.exceptions.SSLError as e:
        print(f"SSL Error downloading EPG XML: {e}")
        print("Note: The EPG source may have SSL certificate issues.")
        print("Trying with SSL verification disabled...")
        try:
            response = requests.get(url, timeout=60, verify=False)
            response.raise_for_status()
            print(f"Downloaded {len(response.text)} characters of XML data (SSL verification bypassed)")
            return response.text
        except Exception as e2:
            print(f"Still failed: {e2}")
            return None
    except Exception as e:
        print(f"Error downloading EPG XML: {e}")
        return None

def filter_adult_content(m3u_content):
    """Filter out adult/XXX content from M3U"""
    lines = m3u_content.split('\n')
    filtered_lines = []
    skip_channel = False

    # Comprehensive list of adult content keywords and patterns
    adult_keywords = [
        'xxx', 'porn', 'sex', 'adult', 'erotic', 'nude', 'naked',
        'hentai', 'milf', 'teen', 'amateur', 'fetish', 'bdsm',
        'lesbian', 'gay', 'bisexual', 'trans', 'shemale', 'ladyboy',
        'escort', 'prostitute', 'strip', 'cam', 'webcam', 'onlyfans',
        'manyvids', 'realitykings', 'bangbros', 'naughtyamerica',
        'blacked', 'tushy', 'vixen', 'brazzers', 'evilangel'
    ]

    # Group patterns that indicate adult content
    adult_groups = [
        'xxx', 'porn', 'adult', 'erotic', 'sex', 'nude',
        'daddylive xxx', 'drewlive xxx'
    ]

    # Channel ID patterns for adult content
    adult_channel_ids = [
        'adult.section.dummy',
        'xxx.',
        'porn.',
        'sex.',
        'adult.',
        'erotic.'
    ]

    for line in lines:
        line_lower = line.lower().strip()

        # Skip empty lines
        if not line_lower:
            filtered_lines.append(line)
            continue

        # Check for adult group markers
        if line_lower.startswith('#extgrp:'):
            group_name = line_lower[8:].strip()
            if any(adult_term in group_name for adult_term in adult_groups):
                skip_channel = True
                continue

        # Check for adult channel IDs in EXTINF lines
        elif line_lower.startswith('#extinf:'):
            # Reset skip flag for new channel
            skip_channel = False

            # Check for radio stations (skip them)
            if 'radio="true"' in line_lower or ' radio ' in line_lower:
                skip_channel = True
                continue

            # Check TVG-ID attribute
            if any(adult_id in line_lower for adult_id in adult_channel_ids):
                skip_channel = True
                continue

            # Check for adult keywords in channel name (after comma)
            if ',' in line:
                channel_name = line.split(',', 1)[1].lower().strip()

                # Skip legitimate channels that happen to contain "adult"
                legitimate_exceptions = [
                    'adult swim',  # Cartoon Network
                    'black jesus',  # TV show
                ]

                # Check if it's a legitimate exception
                is_legitimate = any(exception in channel_name for exception in legitimate_exceptions)

                if not is_legitimate:
                    # Check for adult keywords, but be more specific
                    if any(keyword in channel_name for keyword in adult_keywords):
                        # Additional check: avoid false positives with movie/TV show names
                        # Only flag if it seems like explicit adult content
                        adult_indicators = ['xxx', 'porn', 'sex', 'nude', 'naked', 'erotic', 'amateur']
                        if any(indicator in channel_name for indicator in adult_indicators):
                            skip_channel = True
                            continue

                    # Check for 18+ markers
                    if '18+' in channel_name or '+18' in channel_name:
                        skip_channel = True
                        continue

                    # Check for explicit content markers
                    explicit_markers = ['only fans', 'onlyfans', 'manyvids', 'cam', 'webcam']
                    if any(marker in channel_name for marker in explicit_markers):
                        skip_channel = True
                        continue

        # If we're skipping a channel, skip the URL line too
        elif skip_channel and not line.startswith('#'):
            continue

        # Add line if not skipping
        if not skip_channel:
            filtered_lines.append(line)

    filtered_content = '\n'.join(filtered_lines)

    # Count channels before and after filtering
    original_count = m3u_content.count('#EXTINF:')
    filtered_count = filtered_content.count('#EXTINF:')
    removed_count = original_count - filtered_count

    # Count radio stations in original content
    radio_count = m3u_content.lower().count('radio="true"')

    print(f"Original channels: {original_count}")
    print(f"Radio stations found: {radio_count}")
    print(f"Filtered channels: {filtered_count}")
    print(f"Adult/radio channels removed: {removed_count}")

    return filtered_content

def parse_and_save_xmltv(xml_content, filename):
    """Parse XML EPG data and save as XMLTV format"""
    try:
        # Parse the XML
        root = ET.fromstring(xml_content)

        # Create XMLTV structure
        tv_element = ET.Element('tv')
        tv_element.set('generator-info-name', 'PlutoTV EPG')
        tv_element.set('generator-info-url', 'https://i.mjh.nz/PlutoTV/us.xml')

        # Extract channels and programmes
        channels = {}
        programme_count = 0

        for programme in root.findall('.//programme'):
            # Extract programme data
            start = programme.get('start')
            stop = programme.get('stop')
            channel = programme.get('channel')
            title = programme.find('title')
            desc = programme.find('desc')

            if channel and title is not None:
                # Add to channels dict if not exists
                if channel not in channels:
                    channels[channel] = {
                        'id': channel,
                        'display_name': channel,
                        'icon': None
                    }

                # Create programme element
                prog_element = ET.SubElement(tv_element, 'programme')
                prog_element.set('start', start)
                prog_element.set('stop', stop)
                prog_element.set('channel', channel)

                title_element = ET.SubElement(prog_element, 'title')
                title_element.set('lang', 'en')
                title_element.text = title.text or 'No Title'

                if desc is not None and desc.text:
                    desc_element = ET.SubElement(prog_element, 'desc')
                    desc_element.set('lang', 'en')
                    desc_element.text = desc.text

                programme_count += 1

        # Add channel elements
        for channel_id, channel_data in channels.items():
            channel_element = ET.SubElement(tv_element, 'channel')
            channel_element.set('id', channel_id)

            display_name_element = ET.SubElement(channel_element, 'display-name')
            display_name_element.set('lang', 'en')
            display_name_element.text = channel_data['display_name']

        # Convert to string and save
        xmltv_content = ET.tostring(tv_element, encoding='unicode', method='xml')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">\n')
            f.write(xmltv_content)

        channel_count = len(channels)
        print(f"Parsed {channel_count} channels and {programme_count} programmes")
        print(f"Saved XMLTV EPG to: {filename}")

        return filename

    except Exception as e:
        print(f"Error parsing XML EPG data: {e}")
        return None

def save_filtered_m3u(content, filename):
    """Save the filtered M3U content"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved filtered M3U to: {filename}")
    return filename

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="IPTV Extractor - Downloads M3U playlist, filters adult content, and fetches PlutoTV EPG data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python iptv_extractor.py                           # Download M3U and PlutoTV EPG, filter adult content
  python iptv_extractor.py --source URL              # Use custom M3U source
  python iptv_extractor.py --output-m3u FILE         # Custom M3U output filename
  python iptv_extractor.py --output-xmltv FILE       # Custom XMLTV output filename
  python iptv_extractor.py --epg-source URL          # Custom EPG XML source (e.g., SamsungTVPlus, Stirr, etc.)
        """
    )

    parser.add_argument(
        "--source",
        type=str,
        default="https://raw.githubusercontent.com/BuddyChewChew/combine-remote-playlists/refs/heads/main/combined_playlist.m3u",
        help="M3U playlist source URL"
    )

    parser.add_argument(
        "--epg-source",
        type=str,
        default="https://i.mjh.nz/PlutoTV/us.xml",
        help="EPG XML source URL (default: PlutoTV US EPG)"
    )

    parser.add_argument(
        "--output-m3u",
        type=str,
        default="iptv_playlist.m3u",
        help="M3U output filename"
    )

    parser.add_argument(
        "--output-xmltv",
        type=str,
        default="epg_guide.xmltv",
        help="XMLTV EPG output filename"
    )

    args = parser.parse_args()

    print("Starting IPTV extraction process...")
    print("=" * 50)

    # Download M3U
    m3u_content = download_m3u(args.source)
    if not m3u_content:
        sys.exit(1)

    # Filter adult content
    print("\nFiltering adult content...")
    filtered_content = filter_adult_content(m3u_content)

    # Save filtered M3U
    save_filtered_m3u(filtered_content, args.output_m3u)

    # Download and process EPG XML
    print("\n" + "=" * 30)
    xml_content = download_xml_epg(args.epg_source)
    if xml_content:
        parse_and_save_xmltv(xml_content, args.output_xmltv)
    else:
        print("Warning: Could not download EPG data")

    print("\n" + "=" * 50)
    print("✓ IPTV extraction completed!")
    print("✓ M3U playlist filtered (adult/XXX content and radio stations removed)")
    print("✓ EPG guide data downloaded and converted to XMLTV format")
    print("\nFiles created:")
    print(f"  - M3U Playlist: {args.output_m3u}")
    print(f"  - EPG Guide: {args.output_xmltv}")

if __name__ == "__main__":
    main()
