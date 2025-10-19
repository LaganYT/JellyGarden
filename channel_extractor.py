#!/usr/bin/env python3
"""
Channel Extractor for TV Garden to XMLTV
Converts TV Garden channel data to XMLTV format for Jellyfin
"""

import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import sys
from urllib.parse import urlparse

def fetch_channel_data(url):
    """Fetch channel data from the provided URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def create_xmltv_header():
    """Create XMLTV header with metadata"""
    root = ET.Element("tv")
    root.set("generator-info-name", "TV Garden Channel Extractor")
    root.set("generator-info-url", "https://github.com/TVGarden/tv-garden-channel-list")
    root.set("source-info-name", "TV Garden")
    root.set("source-info-url", "https://raw.githubusercontent.com/TVGarden/tv-garden-channel-list/refs/heads/main/channels/raw/countries/us.json")
    
    return root

def create_channel_element(channel_data):
    """Create a channel element for XMLTV"""
    channel = ET.Element("channel")
    channel.set("id", channel_data.get("nanoid", ""))
    
    # Display name
    display_name = ET.SubElement(channel, "display-name")
    display_name.text = channel_data.get("name", "Unknown Channel")
    
    # URL (use first IPTV URL if available, otherwise first YouTube URL)
    urls = channel_data.get("iptv_urls", []) + channel_data.get("youtube_urls", [])
    if urls:
        url_elem = ET.SubElement(channel, "url")
        url_elem.text = urls[0]
    
    # Language
    language = channel_data.get("language", "")
    if language:
        lang_elem = ET.SubElement(channel, "language")
        lang_elem.text = language
    
    # Country
    country = channel_data.get("country", "")
    if country:
        country_elem = ET.SubElement(channel, "country")
        country_elem.text = country.upper()
    
    return channel

def create_programme_element(channel_id, start_time, end_time, title="Live Stream"):
    """Create a programme element for XMLTV"""
    programme = ET.Element("programme")
    programme.set("channel", channel_id)
    programme.set("start", start_time)
    programme.set("stop", end_time)
    
    # Title
    title_elem = ET.SubElement(programme, "title")
    title_elem.text = title
    
    # Description
    desc_elem = ET.SubElement(programme, "desc")
    desc_elem.text = "Live streaming content"
    
    return programme

def convert_to_xmltv(channels_data):
    """Convert channel data to XMLTV format"""
    root = create_xmltv_header()
    
    # Get current time for programme scheduling
    now = datetime.now(timezone.utc)
    start_time = now.strftime("%Y%m%d%H%M%S %z")
    end_time = (now.replace(hour=23, minute=59, second=59)).strftime("%Y%m%d%H%M%S %z")
    
    for channel_data in channels_data:
        # Create channel element
        channel = create_channel_element(channel_data)
        root.append(channel)
        
        # Create a basic programme entry for live streaming
        programme = create_programme_element(
            channel_data.get("nanoid", ""),
            start_time,
            end_time,
            "Live Stream"
        )
        root.append(programme)
    
    return root

def save_xmltv(xmltv_root, filename="channels.xmltv"):
    """Save XMLTV data to file"""
    # Format the XML with proper indentation
    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                    indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    indent(xmltv_root)
    
    # Write to file
    tree = ET.ElementTree(xmltv_root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"XMLTV file saved as: {filename}")

def main():
    """Main function to extract channels and create XMLTV"""
    url = "https://raw.githubusercontent.com/TVGarden/tv-garden-channel-list/refs/heads/main/channels/raw/countries/us.json"
    
    print("Fetching channel data from TV Garden...")
    channels_data = fetch_channel_data(url)
    
    if not channels_data:
        print("Failed to fetch channel data")
        sys.exit(1)
    
    print(f"Found {len(channels_data)} channels")
    
    # Filter out channels without IPTV URLs and skip YouTube-only channels
    valid_channels = [ch for ch in channels_data if ch.get("iptv_urls") and not (ch.get("iptv_urls") == [] and ch.get("youtube_urls"))]
    print(f"Found {len(valid_channels)} channels with IPTV URLs (YouTube-only channels skipped)")
    
    if not valid_channels:
        print("No channels with IPTV URLs found")
        sys.exit(1)
    
    # Convert to XMLTV
    print("Converting to XMLTV format...")
    xmltv_root = convert_to_xmltv(valid_channels)
    
    # Save XMLTV file
    save_xmltv(xmltv_root, "tv_garden_channels.xmltv")
    
    print("XMLTV file created successfully!")
    print("\nTo use with Jellyfin:")
    print("1. Place the XMLTV file in your Jellyfin server's accessible location")
    print("2. In Jellyfin, go to Dashboard > Live TV > TV Guide Data Providers")
    print("3. Add a new XMLTV provider and point to your file")
    print("4. The channels should appear in your Live TV section")

if __name__ == "__main__":
    main()
