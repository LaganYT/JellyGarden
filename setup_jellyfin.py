#!/usr/bin/env python3
"""
Jellyfin Setup Helper for TV Garden Channels
Checks dependencies and provides setup instructions
"""

import os
import subprocess
import sys
import argparse

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []

    try:
        import requests
        print("✓ requests library found")
    except ImportError:
        missing_deps.append("requests")

    try:
        import tmdbsimple
        print("✓ tmdbsimple library found (TMDB integration available)")
    except ImportError:
        print("⚠ tmdbsimple library not found (TMDB integration disabled)")

    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv library found")
    except ImportError:
        print("⚠ python-dotenv library not found (environment variables only)")

    return len(missing_deps) == 0, missing_deps

def install_dependencies(missing_deps):
    """Install missing required dependencies"""
    print("Installing missing dependencies...")
    deps_to_install = missing_deps + ["tmdbsimple", "python-dotenv"]  # Install optional deps too

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + deps_to_install)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def run_extractor(tmdb_enabled=False, api_key=None):
    """Run the enhanced channel extractor"""
    print("\n" + "="*50)
    print("Running TV Garden channel extractor...")
    print("="*50)

    cmd = [sys.executable, "enhanced_extractor.py"]
    if tmdb_enabled:
        cmd.append("--tmdb")
        if api_key:
            cmd.extend(["--api-key", api_key])

    try:
        subprocess.check_call(cmd)
        print("✓ Extractor completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Extractor failed with exit code {e.returncode}")
        return False

def show_setup_instructions():
    """Display Jellyfin setup instructions"""
    print("\n" + "="*60)
    print("JELLYFIN SETUP INSTRUCTIONS")
    print("="*60)
    print("""
1. BASIC USAGE (with M3U):
   python enhanced_extractor.py

2. XMLTV ONLY:
   python enhanced_extractor.py --no-m3u

3. DAILY AUTOMATION (Recommended):
   python setup_jellyfin.py --install-service

4. JELLYFIN CONFIGURATION:

   A. Add M3U Tuner:
      - Go to Dashboard → Live TV → Tuners
      - Click "Add" → Select "M3U Tuner"
      - Name: "TV Garden Channels"
      - M3U URL: file:///var/lib/tv-garden/tv_garden_channels.m3u
      - Save

   B. Add XMLTV Guide Provider:
      - Go to Dashboard → Live TV → Guide Data Providers
      - Click "Add" → Select "XMLTV"
      - Name: "TV Garden Guide"
      - XMLTV URL: file:///var/lib/tv-garden/tv_garden_channels.xmltv
      - Save

   C. Map Channels to Guide:
      - Go to Dashboard → Live TV → Channels
      - Map each channel to its corresponding guide data
      - Save mappings

5. FEATURES:
   - 1,000+ US channels from EPGShare01
   - Real programme schedules with detailed metadata
   - M3U playlist templates for easy stream URL addition
   - Automatic channel numbering
   - Daily automated updates via systemd
   - Channel icons and rich programme information

6. NOTES:
   - EPGShare01 provides programme data only (no stream URLs)
   - Add your own IPTV stream URLs to the generated M3U file
   - Daily service logs to /var/log/tv-garden/daily_extraction.log
   - Files stored in /var/lib/tv-garden/
""")

def install_service():
    """Install systemd service for daily EPGShare01 extraction"""
    print("Installing systemd service for daily EPGShare01 extraction...")

    try:
        import subprocess
        import os
        import shutil

        # Check if running as root
        if os.geteuid() != 0:
            print("ERROR: Service installation requires root privileges")
            print("Run with: sudo python setup_jellyfin.py --install-service")
            return False

        # Check if systemd is available
        if not shutil.which("systemctl"):
            print("ERROR: systemd is not available on this system")
            return False

        script_dir = os.path.dirname(os.path.abspath(__file__))
        service_file = os.path.join(script_dir, "tv-garden-daily.service")
        timer_file = os.path.join(script_dir, "tv-garden-daily.timer")

        # Check if service files exist
        if not os.path.exists(service_file):
            print(f"ERROR: Service file not found: {service_file}")
            return False
        if not os.path.exists(timer_file):
            print(f"ERROR: Timer file not found: {timer_file}")
            return False

        # Copy service files to systemd directory
        systemd_dir = "/etc/systemd/system"
        shutil.copy2(service_file, systemd_dir)
        shutil.copy2(timer_file, systemd_dir)

        # Reload systemd
        subprocess.check_call(["systemctl", "daemon-reload"])

        # Enable and start the timer
        subprocess.check_call(["systemctl", "enable", "tv-garden-daily.timer"])
        subprocess.check_call(["systemctl", "start", "tv-garden-daily.timer"])

        print("✓ Systemd service installed and started")
        print("  Service: tv-garden-daily.service")
        print("  Timer: tv-garden-daily.timer")
        print("  Logs: /var/log/tv-garden/daily_extraction.log")
        print("  Files: /var/lib/tv-garden/")

        return True

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install service: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Service installation failed: {e}")
        return False

def uninstall_service():
    """Remove systemd service"""
    print("Uninstalling systemd service...")

    try:
        import subprocess
        import os

        # Check if running as root
        if os.geteuid() != 0:
            print("ERROR: Service uninstallation requires root privileges")
            print("Run with: sudo python setup_jellyfin.py --uninstall-service")
            return False

        # Stop and disable services
        subprocess.call(["systemctl", "stop", "tv-garden-daily.timer"], stderr=subprocess.DEVNULL)
        subprocess.call(["systemctl", "stop", "tv-garden-daily.service"], stderr=subprocess.DEVNULL)
        subprocess.call(["systemctl", "disable", "tv-garden-daily.timer"], stderr=subprocess.DEVNULL)
        subprocess.call(["systemctl", "disable", "tv-garden-daily.service"], stderr=subprocess.DEVNULL)

        # Remove service files
        service_files = [
            "/etc/systemd/system/tv-garden-daily.service",
            "/etc/systemd/system/tv-garden-daily.timer"
        ]

        for service_file in service_files:
            if os.path.exists(service_file):
                os.remove(service_file)

        # Reload systemd
        subprocess.check_call(["systemctl", "daemon-reload"])

        print("✓ Systemd service uninstalled")

        return True

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to uninstall service: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Service uninstallation failed: {e}")
        return False

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="TV Garden Channel Setup Helper")
    parser.add_argument("--install-deps", action="store_true", help="Install missing dependencies")
    parser.add_argument("--extract", action="store_true", help="Run channel extraction")
    parser.add_argument("--tmdb", action="store_true", help="Enable TMDB integration")
    parser.add_argument("--api-key", type=str, help="TMDB API key")
    parser.add_argument("--install-service", action="store_true", help="Install systemd service for daily execution")
    parser.add_argument("--uninstall-service", action="store_true", help="Remove systemd service")

    args = parser.parse_args()

    print("TV Garden Channel Extractor Setup for Jellyfin")
    print("=" * 50)

    # Check dependencies
    deps_ok, missing_deps = check_dependencies()

    if not deps_ok and not args.install_deps:
        print(f"\nMissing required dependencies: {', '.join(missing_deps)}")
        print("Run with --install-deps to install them automatically")
        print("Or install manually: pip install -r requirements.txt")
        sys.exit(1)

    if not deps_ok and args.install_deps:
        if not install_dependencies(missing_deps):
            print("Failed to install dependencies. Please install manually:")
            print("pip install -r requirements.txt")
            sys.exit(1)
        # Recheck after installation
        deps_ok, _ = check_dependencies()

    # Handle service installation/uninstallation
    if args.install_service:
        if not install_service():
            print("Failed to install service")
            sys.exit(1)
        return  # Exit after service installation

    if args.uninstall_service:
        if not uninstall_service():
            print("Failed to uninstall service")
            sys.exit(1)
        return  # Exit after service uninstallation

    # Run extraction if requested
    if args.extract:
        if not run_extractor(args.tmdb, args.api_key):
            print("Failed to generate channel files")
            sys.exit(1)

    # Show setup instructions
    show_setup_instructions()

    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("Run 'python enhanced_extractor.py' to generate channel files.")
    print("Follow the instructions above to configure Jellyfin.")

if __name__ == "__main__":
    main()
