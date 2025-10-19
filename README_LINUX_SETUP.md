# TV Garden Linux Daily Service

This setup provides a complete Linux service that runs the TV Garden channel extractor daily and hosts the results via HTTP.

## Features

- **Daily Automation**: Runs the enhanced extractor every day automatically
- **Web Hosting**: Serves the generated files via HTTP on port 3126
- **Systemd Integration**: Full systemd service with timer for daily execution
- **Logging**: Comprehensive logging with rotation
- **Error Handling**: Automatic retry on failures
- **Easy Management**: Simple commands to start, stop, and monitor

## Files Generated

- `tv_garden_channels_enhanced.xmltv` - Enhanced XMLTV guide data
- `tv_garden_channels.m3u` - M3U playlist for IPTV players

## Quick Installation

1. **Make the installation script executable:**

   ```bash
   chmod +x install_tv_garden.sh
   ```

2. **Run the installation (requires sudo):**

   ```bash
   sudo ./install_tv_garden.sh
   ```

3. **Check the status:**
   ```bash
   sudo ./install_tv_garden.sh status
   ```

## Manual Installation

If you prefer to install manually:

1. **Copy files to system directory:**

   ```bash
   sudo mkdir -p /opt/tv-garden
   sudo cp enhanced_extractor.py /opt/tv-garden/
   sudo cp requirements.txt /opt/tv-garden/
   sudo cp daily_tv_garden.sh /opt/tv-garden/
   sudo chmod +x /opt/tv-garden/daily_tv_garden.sh
   ```

2. **Install Python dependencies:**

   ```bash
   sudo pip3 install -r requirements.txt
   ```

3. **Create directories:**

   ```bash
   sudo mkdir -p /var/log/tv-garden /var/www/tv-garden
   ```

4. **Install systemd service:**

   ```bash
   sudo cp tv-garden.service /etc/systemd/system/
   sudo cp tv-garden-daily.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable tv-garden.service
   sudo systemctl enable tv-garden-daily.timer
   ```

5. **Start the service:**
   ```bash
   sudo systemctl start tv-garden.service
   sudo systemctl start tv-garden-daily.timer
   ```

## Usage

### Service Management

```bash
# Start the service
sudo systemctl start tv-garden.service

# Stop the service
sudo systemctl stop tv-garden.service

# Restart the service
sudo systemctl restart tv-garden.service

# Check status
sudo systemctl status tv-garden.service

# View logs
sudo journalctl -u tv-garden.service -f
```

### Manual Operations

```bash
# Run extraction only
/opt/tv-garden/daily_tv_garden.sh extract

# Start web server only
/opt/tv-garden/daily_tv_garden.sh web

# Show status
/opt/tv-garden/daily_tv_garden.sh status

# Restart everything
/opt/tv-garden/daily_tv_garden.sh restart
```

### Accessing Files

Once running, the files are available at:

- **XMLTV Guide Data**: `http://localhost:3126/tv_garden_channels_enhanced.xmltv`
- **M3U Playlist**: `http://localhost:3126/tv_garden_channels.m3u`

## Configuration

### Web Port

To change the web port, edit `/opt/tv-garden/daily_tv_garden.sh` and modify the `WEB_PORT` variable:

```bash
WEB_PORT=3126  # Change to your preferred port
```

### Timer Schedule

The service runs daily by default. To modify the schedule, edit the timer:

```bash
sudo systemctl edit tv-garden-daily.timer
```

Add your custom schedule:

```ini
[Timer]
OnCalendar=*-*-* 06:00:00  # Run at 6 AM daily
```

## Jellyfin Integration

### Adding as Tuner

1. In Jellyfin, go to **Dashboard** → **Live TV** → **Tuners**
2. Click **Add Tuner** → **M3U Tuner**
3. Enter the M3U URL: `http://your-server:3126/tv_garden_channels.m3u`
4. Save the tuner

### Adding Guide Data

1. In Jellyfin, go to **Dashboard** → **Live TV** → **Guide Data Providers**
2. Click **Add Guide Data Provider** → **XMLTV**
3. Enter the XMLTV URL: `http://your-server:3126/tv_garden_channels_enhanced.xmltv`
4. Save the provider

### Mapping Channels

1. Go to **Live TV** → **Channels**
2. Map each channel to its corresponding guide data
3. The channels should now show program information

## Monitoring

### Log Files

- **Service Logs**: `/var/log/tv-garden/daily_extraction.log`
- **Web Server Logs**: `/var/log/tv-garden/web_server.log`
- **System Logs**: `sudo journalctl -u tv-garden.service`

### Health Checks

```bash
# Check if web server is responding
curl -I http://localhost:3126/tv_garden_channels.m3u

# Check file sizes
ls -lh /var/www/tv-garden/

# Check service status
/opt/tv-garden/daily_tv_garden.sh status
```

## Troubleshooting

### Service Won't Start

1. Check logs: `sudo journalctl -u tv-garden.service -f`
2. Verify Python dependencies: `python3 -c "import requests"`
3. Check file permissions: `ls -la /opt/tv-garden/`

### Files Not Updating

1. Check if extraction is running: `sudo systemctl status tv-garden-daily.timer`
2. Run manual extraction: `/opt/tv-garden/daily_tv_garden.sh extract`
3. Check network connectivity: `curl -I https://raw.githubusercontent.com/TVGarden/tv-garden-channel-list/refs/heads/main/channels/raw/countries/us.json`

### Web Server Issues

1. Check if port is in use: `sudo netstat -tlnp | grep :3126`
2. Restart web server: `/opt/tv-garden/daily_tv_garden.sh restart`
3. Check web server logs: `tail -f /var/log/tv-garden/web_server.log`

## Uninstallation

To remove the service completely:

```bash
sudo ./install_tv_garden.sh uninstall
```

Or manually:

```bash
sudo systemctl stop tv-garden-daily.timer
sudo systemctl stop tv-garden.service
sudo systemctl disable tv-garden-daily.timer
sudo systemctl disable tv-garden.service
sudo rm -f /etc/systemd/system/tv-garden.service
sudo rm -f /etc/systemd/system/tv-garden-daily.timer
sudo rm -rf /opt/tv-garden
sudo systemctl daemon-reload
```

## Security Notes

- The service runs as root for system integration
- Web server is bound to localhost by default
- Files are served with appropriate permissions
- Consider firewall rules for external access

## Customization

### Adding Custom Channels

Edit `/opt/tv-garden/enhanced_extractor.py` to modify the source URL or add filtering logic.

### Changing Output Format

Modify the XMLTV generation functions in `enhanced_extractor.py` to customize the output format.

### Adding Authentication

For external access, consider adding nginx with authentication in front of the Python HTTP server.

## Support

For issues or questions:

1. Check the logs first: `sudo journalctl -u tv-garden.service -f`
2. Verify the manual extraction works: `/opt/tv-garden/daily_tv_garden.sh extract`
3. Check network connectivity to the TV Garden API
4. Ensure all dependencies are installed: `pip3 install -r requirements.txt`
