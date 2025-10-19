# TV Garden Channel Extractor for Jellyfin

This tool extracts channel data from the TV Garden channel list and converts it to XMLTV format for use with Jellyfin.

## Features

- Fetches channel data from TV Garden's US channel list (1,157 channels)
- Filters channels to only include those with IPTV URLs (compatible with Jellyfin)
- Converts to standard XMLTV format
- Includes channel metadata (language, country, etc.)
- Creates detailed programme schedules for 7 days
- Generates M3U playlist for Jellyfin tuner
- Enhanced XMLTV with proper programme information

## Quick Setup

Run the automated setup:

```bash
python3 setup_jellyfin.py
```

This will:

1. Install dependencies
2. Generate all necessary files
3. Display complete Jellyfin setup instructions

## Manual Installation

1. Install Python 3.6 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Extractor

```bash
python3 channel_extractor.py
```

Generates: `tv_garden_channels.xmltv`

### Enhanced Extractor (Recommended)

```bash
python3 enhanced_extractor.py
```

Generates:

- `tv_garden_channels.m3u` - M3U playlist for Jellyfin tuner
- `tv_garden_channels_enhanced.xmltv` - Enhanced guide data with 7-day programming

## Jellyfin Setup

### Method 1: Using M3U + XMLTV (Recommended)

1. **Add M3U Tuner:**

   - Go to **Dashboard** → **Live TV** → **Tuners**
   - Click **Add** → Select **M3U Tuner**
   - Name: "TV Garden Channels"
   - M3U URL: `file:///path/to/tv_garden_channels.m3u`
   - Save

2. **Add XMLTV Guide Provider:**

   - Go to **Dashboard** → **Live TV** → **TV Guide Data Providers**
   - Click **Add** → Select **XMLTV**
   - Name: "TV Garden Guide"
   - XMLTV URL: `file:///path/to/tv_garden_channels_enhanced.xmltv`
   - Save

3. **Map Channels to Guide:**
   - Go to **Dashboard** → **Live TV** → **Mappings**
   - Map each channel to its corresponding guide data
   - Save mappings

### Method 2: Using Basic XMLTV Only

1. **Add XMLTV Guide Provider:**

   - Go to **Dashboard** → **Live TV** → **TV Guide Data Providers**
   - Click **Add** → Select **XMLTV**
   - Name: "TV Garden Basic"
   - XMLTV URL: `file:///path/to/tv_garden_channels.xmltv`
   - Save

2. **Configure Live TV:**
   - Go to **Dashboard** → **Live TV** → **Tuners**
   - Add a new tuner with the M3U playlist
   - Map the channels to the XMLTV guide data

## Generated Files

- `tv_garden_channels.m3u` - M3U playlist (1,157 channels)
- `tv_garden_channels_enhanced.xmltv` - Enhanced XMLTV with 7-day programming
- `tv_garden_channels.xmltv` - Basic XMLTV with simple programme entries
- `channel_extractor.py` - Basic extraction script
- `enhanced_extractor.py` - Enhanced extraction script with M3U generation
- `setup_jellyfin.py` - Automated setup script
- `requirements.txt` - Python dependencies

## Channel Information

The script extracts the following information for each channel:

- Channel name and number (1-1157)
- IPTV streaming URL
- Language (if specified)
- Country
- Unique channel ID
- 7-day programme schedule with morning/afternoon/evening blocks

## Programme Schedule

The enhanced XMLTV includes:

- **Morning Programming**: 6:00 AM - 12:00 PM
- **Afternoon Programming**: 12:00 PM - 6:00 PM
- **Evening Programming**: 6:00 PM - 6:00 AM (next day)
- **7 days** of programming data

## Notes

- Only channels with IPTV URLs are included (YouTube-only channels are automatically skipped)
- Some IPTV streams may be geo-blocked or require specific network access
- Channels are numbered 1-1157 for easy navigation
- The XMLTV format is compatible with Jellyfin and other media servers
- Channel data is fetched from: https://raw.githubusercontent.com/TVGarden/tv-garden-channel-list/refs/heads/main/channels/raw/countries/us.json

## Troubleshooting

- If channels don't appear in Jellyfin, check that the file paths are correct
- Ensure your Jellyfin server can access the M3U and XMLTV files
- Some streams may not work in your region due to geo-blocking
- Check Jellyfin logs for any parsing errors
- Verify that the M3U and XMLTV files are properly formatted
