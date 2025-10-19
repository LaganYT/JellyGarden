#!/bin/bash

# Daily TV Garden Channel Extractor and Web Server
# This script runs the enhanced extractor and hosts the results via HTTP

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="/var/log/tv-garden"
WEB_DIR="/var/www/tv-garden"
PYTHON_SCRIPT="$SCRIPT_DIR/enhanced_extractor.py"
LOG_FILE="$LOG_DIR/daily_extraction.log"
PID_FILE="/run/tv-garden-web.pid"
WEB_PORT=3126

# Create directories if they don't exist
sudo mkdir -p "$LOG_DIR" "$WEB_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if web server is running
is_web_server_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start web server
start_web_server() {
    if is_web_server_running; then
        log_message "Web server is already running on port $WEB_PORT"
        return 0
    fi
    
    log_message "Starting web server on port $WEB_PORT"
    
    # Start Python HTTP server in background
    cd "$WEB_DIR"
    nohup python3 -m http.server "$WEB_PORT" > "$LOG_DIR/web_server.log" 2>&1 &
    echo $! > "$PID_FILE"
    
    # Wait a moment for server to start
    sleep 2
    
    if is_web_server_running; then
        log_message "Web server started successfully on http://localhost:$WEB_PORT"
        log_message "Files available at:"
        log_message "  - http://localhost:$WEB_PORT/tv_garden_channels_enhanced.xmltv"
        log_message "  - http://localhost:$WEB_PORT/tv_garden_channels.m3u"
    else
        log_message "ERROR: Failed to start web server"
        return 1
    fi
}

# Function to stop web server
stop_web_server() {
    if is_web_server_running; then
        local pid=$(cat "$PID_FILE")
        log_message "Stopping web server (PID: $pid)"
        kill "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
        log_message "Web server stopped"
    else
        log_message "Web server is not running"
    fi
}

# Function to run the extraction
run_extraction() {
    log_message "Starting TV Garden channel extraction..."
    
    # Create a temporary writable directory
    TEMP_DIR="/tmp/tv-garden-$$"
    mkdir -p "$TEMP_DIR"
    
    # Change to temporary directory
    cd "$TEMP_DIR"
    
    # Check if Python script exists
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        log_message "ERROR: Python script not found at $PYTHON_SCRIPT"
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    # Check if requirements are installed
    if ! python3 -c "import requests" 2>/dev/null; then
        log_message "Installing Python requirements..."
        pip3 install -r "$SCRIPT_DIR/requirements.txt" || {
            log_message "ERROR: Failed to install requirements"
            rm -rf "$TEMP_DIR"
            return 1
        }
    fi
    
    # Copy the Python script to temp directory
    cp "$PYTHON_SCRIPT" "$TEMP_DIR/"
    cp "$SCRIPT_DIR/requirements.txt" "$TEMP_DIR/" 2>/dev/null || true
    
    # Run the extraction in temp directory
    if python3 "$TEMP_DIR/enhanced_extractor.py"; then
        log_message "Extraction completed successfully"
        
        # Copy files to web directory
        cp -f "$TEMP_DIR/tv_garden_channels_enhanced.xmltv" "$WEB_DIR/"
        cp -f "$TEMP_DIR/tv_garden_channels.m3u" "$WEB_DIR/"
        
        # Set proper permissions
        chmod 644 "$WEB_DIR/tv_garden_channels_enhanced.xmltv"
        chmod 644 "$WEB_DIR/tv_garden_channels.m3u"
        
        log_message "Files copied to web directory: $WEB_DIR"
        
        # Clean up temp directory
        rm -rf "$TEMP_DIR"
        return 0
    else
        log_message "ERROR: Extraction failed"
        rm -rf "$TEMP_DIR"
        return 1
    fi
}

# Function to show status
show_status() {
    echo "TV Garden Daily Service Status"
    echo "=============================="
    echo "Script Directory: $SCRIPT_DIR"
    echo "Web Directory: $WEB_DIR"
    echo "Log Directory: $LOG_DIR"
    echo "Web Port: $WEB_PORT"
    echo ""
    
    if is_web_server_running; then
        echo "Web Server: RUNNING (PID: $(cat "$PID_FILE"))"
        echo "URL: http://localhost:$WEB_PORT"
    else
        echo "Web Server: NOT RUNNING"
    fi
    
    echo ""
    echo "Available Files:"
    if [ -f "$WEB_DIR/tv_garden_channels_enhanced.xmltv" ]; then
        echo "  ✓ tv_garden_channels_enhanced.xmltv ($(stat -f%z "$WEB_DIR/tv_garden_channels_enhanced.xmltv" 2>/dev/null || stat -c%s "$WEB_DIR/tv_garden_channels_enhanced.xmltv" 2>/dev/null || echo "unknown") bytes)"
    else
        echo "  ✗ tv_garden_channels_enhanced.xmltv (not found)"
    fi
    
    if [ -f "$WEB_DIR/tv_garden_channels.m3u" ]; then
        echo "  ✓ tv_garden_channels.m3u ($(stat -f%z "$WEB_DIR/tv_garden_channels.m3u" 2>/dev/null || stat -c%s "$WEB_DIR/tv_garden_channels.m3u" 2>/dev/null || echo "unknown") bytes)"
    else
        echo "  ✗ tv_garden_channels.m3u (not found)"
    fi
    
    echo ""
    echo "Recent Log Entries:"
    if [ -f "$LOG_FILE" ]; then
        tail -5 "$LOG_FILE"
    else
        echo "No log file found"
    fi
}

# Main script logic
case "${1:-run}" in
    "run")
        log_message "=== Starting daily TV Garden extraction ==="
        run_extraction
        start_web_server
        log_message "=== Daily extraction completed ==="
        ;;
    "start")
        log_message "Starting TV Garden service..."
        run_extraction
        start_web_server
        ;;
    "stop")
        log_message "Stopping TV Garden service..."
        stop_web_server
        ;;
    "restart")
        log_message "Restarting TV Garden service..."
        stop_web_server
        sleep 2
        run_extraction
        start_web_server
        ;;
    "status")
        show_status
        ;;
    "extract")
        log_message "Running extraction only..."
        run_extraction
        ;;
    "web")
        log_message "Starting web server only..."
        start_web_server
        ;;
    *)
        echo "Usage: $0 {run|start|stop|restart|status|extract|web}"
        echo ""
        echo "Commands:"
        echo "  run     - Run extraction and start web server (default)"
        echo "  start   - Run extraction and start web server"
        echo "  stop    - Stop web server"
        echo "  restart - Stop, then run extraction and start web server"
        echo "  status  - Show current status"
        echo "  extract - Run extraction only"
        echo "  web     - Start web server only"
        exit 1
        ;;
esac
