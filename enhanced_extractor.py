#!/usr/bin/env python3
"""
Enhanced Channel Extractor for TV Garden to XMLTV
Converts TV Garden channel data to XMLTV format for Jellyfin with M3U playlist generation
"""

import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import sys
from urllib.parse import urlparse
import os

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
    root.set("generator-info-name", "TV Garden Enhanced Channel Extractor")
    root.set("generator-info-url", "https://github.com/TVGarden/tv-garden-channel-list")
    root.set("source-info-name", "TV Garden")
    root.set("source-info-url", "https://raw.githubusercontent.com/TVGarden/tv-garden-channel-list/refs/heads/main/channels/raw/countries/us.json")
    
    return root

def create_channel_element(channel_data, channel_number):
    """Create a channel element for XMLTV"""
    channel = ET.Element("channel")
    channel.set("id", channel_data.get("nanoid", ""))
    
    # Display name
    display_name = ET.SubElement(channel, "display-name")
    display_name.text = channel_data.get("name", "Unknown Channel")
    
    # Channel number
    display_name_num = ET.SubElement(channel, "display-name")
    display_name_num.text = f"{channel_number}. {channel_data.get('name', 'Unknown Channel')}"
    
    # URL (use first IPTV URL if available)
    urls = channel_data.get("iptv_urls", [])
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

def create_programme_schedule(channel_id, channel_name):
    """Create a more detailed programme schedule"""
    programmes = []
    now = datetime.now(timezone.utc)
    
    # Create programmes for the next 7 days
    for day in range(7):
        current_date = now + timedelta(days=day)
        
        # Morning programme
        morning_start = current_date.replace(hour=6, minute=0, second=0)
        morning_end = current_date.replace(hour=12, minute=0, second=0)
        
        morning_prog = ET.Element("programme")
        morning_prog.set("channel", channel_id)
        morning_prog.set("start", morning_start.strftime("%Y%m%d%H%M%S %z"))
        morning_prog.set("stop", morning_end.strftime("%Y%m%d%H%M%S %z"))
        
        title = ET.SubElement(morning_prog, "title")
        title.text = f"{channel_name} - Morning Programming"
        
        desc = ET.SubElement(morning_prog, "desc")
        desc.text = "Live streaming content - Morning programming"
        
        programmes.append(morning_prog)
        
        # Afternoon programme
        afternoon_start = current_date.replace(hour=12, minute=0, second=0)
        afternoon_end = current_date.replace(hour=18, minute=0, second=0)
        
        afternoon_prog = ET.Element("programme")
        afternoon_prog.set("channel", channel_id)
        afternoon_prog.set("start", afternoon_start.strftime("%Y%m%d%H%M%S %z"))
        afternoon_prog.set("stop", afternoon_end.strftime("%Y%m%d%H%M%S %z"))
        
        title = ET.SubElement(afternoon_prog, "title")
        title.text = f"{channel_name} - Afternoon Programming"
        
        desc = ET.SubElement(afternoon_prog, "desc")
        desc.text = "Live streaming content - Afternoon programming"
        
        programmes.append(afternoon_prog)
        
        # Evening programme
        evening_start = current_date.replace(hour=18, minute=0, second=0)
        next_day = current_date + timedelta(days=1)
        evening_end = next_day.replace(hour=6, minute=0, second=0)
        
        evening_prog = ET.Element("programme")
        evening_prog.set("channel", channel_id)
        evening_prog.set("start", evening_start.strftime("%Y%m%d%H%M%S %z"))
        evening_prog.set("stop", evening_end.strftime("%Y%m%d%H%M%S %z"))
        
        title = ET.SubElement(evening_prog, "title")
        title.text = f"{channel_name} - Evening Programming"
        
        desc = ET.SubElement(evening_prog, "desc")
        desc.text = "Live streaming content - Evening programming"
        
        programmes.append(evening_prog)
    
    return programmes

def create_m3u_playlist(channels_data, filename="tv_garden_channels.m3u"):
    """Create an M3U playlist file for the channels"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        
        for i, channel_data in enumerate(channels_data, 1):
            name = channel_data.get("name", "Unknown Channel")
            urls = channel_data.get("iptv_urls", [])
            
            if urls:
                # Use the first IPTV URL
                url = urls[0]
                f.write(f"#EXTINF:-1 tvg-id=\"{channel_data.get('nanoid', '')}\" tvg-name=\"{name}\" tvg-logo=\"\" group-title=\"TV Garden\",{i}. {name}\n")
                f.write(f"{url}\n")
    
    print(f"M3U playlist saved as: {filename}")

def convert_to_xmltv(channels_data):
    """Convert channel data to XMLTV format"""
    root = create_xmltv_header()
    
    for i, channel_data in enumerate(channels_data, 1):
        # Create channel element
        channel = create_channel_element(channel_data, i)
        root.append(channel)
        
        # Create programme schedule
        programmes = create_programme_schedule(
            channel_data.get("nanoid", ""),
            channel_data.get("name", "Unknown Channel")
        )
        
        for programme in programmes:
            root.append(programme)
    
    return root

def save_xmltv(xmltv_root, filename="tv_garden_channels_enhanced.xmltv"):
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
    print(f"Enhanced XMLTV file saved as: {filename}")

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
    
    # Create M3U playlist
    print("Creating M3U playlist...")
    create_m3u_playlist(valid_channels)
    
    # Convert to XMLTV
    print("Converting to enhanced XMLTV format...")
    xmltv_root = convert_to_xmltv(valid_channels)
    
    # Save XMLTV file
    save_xmltv(xmltv_root)
    
    print("\nFiles created successfully!")
    print("1. tv_garden_channels.m3u - M3U playlist for Jellyfin tuner")
    print("2. tv_garden_channels_enhanced.xmltv - Enhanced XMLTV guide data")
    print("\nTo use with Jellyfin:")
    print("1. Add the M3U playlist as a tuner in Jellyfin")
    print("2. Add the XMLTV file as guide data provider")
    print("3. Map channels to guide data in Jellyfin settings")

if __name__ == "__main__":
    main()
