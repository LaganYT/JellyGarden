#!/usr/bin/env python3
"""
Jellyfin Setup Helper for TV Garden Channels
Creates all necessary files and provides setup instructions
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import requests
        print("✓ requests library found")
        return True
    except ImportError:
        print("✗ requests library not found")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def run_extractors():
    """Run both channel extractors"""
    print("\n" + "="*50)
    print("Running basic channel extractor...")
    print("="*50)
    try:
        subprocess.check_call([sys.executable, "channel_extractor.py"])
        print("✓ Basic extractor completed")
    except subprocess.CalledProcessError:
        print("✗ Basic extractor failed")
        return False
    
    print("\n" + "="*50)
    print("Running enhanced channel extractor...")
    print("="*50)
    try:
        subprocess.check_call([sys.executable, "enhanced_extractor.py"])
        print("✓ Enhanced extractor completed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Enhanced extractor failed")
        return False

def show_setup_instructions():
    """Display Jellyfin setup instructions"""
    print("\n" + "="*60)
    print("JELLYFIN SETUP INSTRUCTIONS")
    print("="*60)
    print("""
1. BASIC SETUP (Recommended):
   - Use: tv_garden_channels.m3u (M3U playlist)
   - Use: tv_garden_channels_enhanced.xmltv (Enhanced guide data)
   
2. JELLYFIN CONFIGURATION:
   
   A. Add M3U Tuner:
      - Go to Dashboard → Live TV → Tuners
      - Click "Add" → Select "M3U Tuner"
      - Name: "TV Garden Channels"
      - M3U URL: file:///path/to/tv_garden_channels.m3u
      - Save
   
   B. Add XMLTV Guide Provider:
      - Go to Dashboard → Live TV → TV Guide Data Providers
      - Click "Add" → Select "XMLTV"
      - Name: "TV Garden Guide"
      - XMLTV URL: file:///path/to/tv_garden_channels_enhanced.xmltv
      - Save
   
   C. Map Channels to Guide:
      - Go to Dashboard → Live TV → Mappings
      - Map each channel to its corresponding guide data
      - Save mappings
   
3. FILES GENERATED:
   - tv_garden_channels.m3u (1,157 channels)
   - tv_garden_channels_enhanced.xmltv (Enhanced guide data)
   - tv_garden_channels.xmltv (Basic guide data)
   
4. NOTES:
   - YouTube-only channels are automatically skipped
   - Some streams may be geo-blocked
   - Not all channels may work in your region
   - Guide data includes 7 days of programming
   - Channels are numbered 1-1157 for easy navigation
""")

def main():
    """Main setup function"""
    print("TV Garden Channel Extractor Setup for Jellyfin")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\nInstalling missing dependencies...")
        if not install_dependencies():
            print("Failed to install dependencies. Please install manually:")
            print("pip install -r requirements.txt")
            sys.exit(1)
    
    # Run extractors
    if not run_extractors():
        print("Failed to generate channel files")
        sys.exit(1)
    
    # Show setup instructions
    show_setup_instructions()
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("All files have been generated successfully.")
    print("Follow the instructions above to configure Jellyfin.")

if __name__ == "__main__":
    main()
