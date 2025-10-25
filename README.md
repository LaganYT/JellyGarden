# IPTV Extractor for Jellyfin

A comprehensive IPTV solution that downloads M3U playlists, filters adult content, fetches EPG data, and provides automated daily updates for Jellyfin.

## Features

- **M3U Playlist Processing**: Downloads from BuddyChewChew's combined playlist (11,000+ channels)
- **Adult Content Filtering**: Automatically removes XXX/porn/adult channels and radio stations
- **EPG Data Integration**: Fetches program schedules from PlutoTV and converts to XMLTV format
- **Daily Automation**: Systemd service for automatic daily updates
- **Jellyfin Integration**: Ready-to-use configuration for Jellyfin Live TV

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run extraction**:
   ```bash
   python iptv_extractor.py
   ```

3. **Install daily service**:
   ```bash
   sudo python setup_jellyfin.py --install-service
   ```

4. **Configure Jellyfin**:
   - Add M3U Tuner: `file:///var/lib/tv-garden/iptv_playlist.m3u`
   - Add XMLTV Guide: `file:///var/lib/tv-garden/epg_guide.xmltv`

## Usage

```bash
# Basic usage (downloads M3U and EPG)
python iptv_extractor.py

# Custom sources
python iptv_extractor.py --source "https://your-m3u-url" --epg-source "https://i.mjh.nz/SamsungTVPlus/us.xml"

# Custom output files
python iptv_extractor.py --output-m3u my_playlist.m3u --output-xmltv my_guide.xmltv

# Setup automation
python setup_jellyfin.py --install-service
python setup_jellyfin.py --extract
```

## Files Created

- `iptv_playlist.m3u` - Filtered M3U playlist with adult content removed
- `epg_guide.xmltv` - XMLTV formatted EPG data for program schedules

## Notes

- Adult content and radio stations are automatically filtered
- EPG data provides program titles, descriptions, and scheduling
- SSL certificate issues with EPG source are handled gracefully
- Daily updates run automatically when service is installed
- Logs available at `/var/log/tv-garden/daily_extraction.log`
