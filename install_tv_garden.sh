#!/bin/bash

# TV Garden Installation Script
# This script installs and configures the TV Garden daily extraction service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/tv-garden"
SERVICE_USER="tv-garden"
WEB_PORT=3126

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if pip3 is installed
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check if systemd is available
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd is required but not available"
        exit 1
    fi
    
    print_success "System requirements met"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install requests if not already installed
    if ! python3 -c "import requests" 2>/dev/null; then
        pip3 install requests
    fi
    
    print_success "Python dependencies installed"
}

# Function to create directories
create_directories() {
    print_status "Creating directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "/var/log/tv-garden"
    mkdir -p "/var/www/tv-garden"
    
    print_success "Directories created"
}

# Function to copy files
copy_files() {
    print_status "Copying files to installation directory..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Copy Python scripts
    cp "$SCRIPT_DIR/enhanced_extractor.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/daily_tv_garden.sh" "$INSTALL_DIR/"
    
    # Make scripts executable
    chmod +x "$INSTALL_DIR/daily_tv_garden.sh"
    chmod +x "$INSTALL_DIR/enhanced_extractor.py"
    
    print_success "Files copied to $INSTALL_DIR"
}

# Function to install systemd service
install_service() {
    print_status "Installing systemd service..."
    
    # Copy service files
    cp "$SCRIPT_DIR/tv-garden.service" "/etc/systemd/system/"
    cp "$SCRIPT_DIR/tv-garden-daily.service" "/etc/systemd/system/"
    cp "$SCRIPT_DIR/tv-garden-daily.timer" "/etc/systemd/system/"
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable and start the service
    systemctl enable tv-garden.service
    systemctl enable tv-garden-daily.service
    systemctl enable tv-garden-daily.timer
    
    print_success "Systemd service installed and enabled"
}

# Function to run initial extraction
run_initial_extraction() {
    print_status "Running initial extraction..."
    
    cd "$INSTALL_DIR"
    ./daily_tv_garden.sh extract
    
    if [ $? -eq 0 ]; then
        print_success "Initial extraction completed"
    else
        print_warning "Initial extraction failed, but service will retry"
    fi
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start the main service
    systemctl start tv-garden.service
    
    # Start the timer
    systemctl start tv-garden-daily.timer
    
    print_success "Services started"
}

# Function to show status
show_status() {
    echo ""
    echo "=========================================="
    echo "TV Garden Service Installation Complete"
    echo "=========================================="
    echo ""
    echo "Installation Directory: $INSTALL_DIR"
    echo "Web Directory: /var/www/tv-garden"
    echo "Log Directory: /var/log/tv-garden"
    echo "Web Port: $WEB_PORT"
    echo ""
    echo "Service Status:"
    systemctl status tv-garden.service --no-pager -l
    echo ""
    echo "Timer Status:"
    systemctl status tv-garden-daily.timer --no-pager -l
    echo ""
    echo "Files Available:"
    if [ -f "/var/www/tv-garden/tv_garden_channels_enhanced.xmltv" ]; then
        echo "  ✓ tv_garden_channels_enhanced.xmltv"
        echo "    URL: http://localhost:$WEB_PORT/tv_garden_channels_enhanced.xmltv"
    else
        echo "  ✗ tv_garden_channels_enhanced.xmltv (not found)"
    fi
    
    if [ -f "/var/www/tv-garden/tv_garden_channels.m3u" ]; then
        echo "  ✓ tv_garden_channels.m3u"
        echo "    URL: http://localhost:$WEB_PORT/tv_garden_channels.m3u"
    else
        echo "  ✗ tv_garden_channels.m3u (not found)"
    fi
    echo ""
    echo "Management Commands:"
    echo "  sudo systemctl start tv-garden.service    # Start service"
    echo "  sudo systemctl stop tv-garden.service     # Stop service"
    echo "  sudo systemctl restart tv-garden.service   # Restart service"
    echo "  sudo systemctl status tv-garden.service   # Check status"
    echo "  sudo journalctl -u tv-garden.service -f    # View logs"
    echo ""
    echo "Manual Commands:"
    echo "  $INSTALL_DIR/daily_tv_garden.sh status    # Show status"
    echo "  $INSTALL_DIR/daily_tv_garden.sh extract   # Run extraction"
    echo "  $INSTALL_DIR/daily_tv_garden.sh restart   # Restart web server"
    echo ""
}

# Function to uninstall
uninstall() {
    print_status "Uninstalling TV Garden service..."
    
    # Stop and disable services
    systemctl stop tv-garden-daily.timer 2>/dev/null || true
    systemctl stop tv-garden.service 2>/dev/null || true
    systemctl disable tv-garden-daily.timer 2>/dev/null || true
    systemctl disable tv-garden.service 2>/dev/null || true
    
    # Remove service files
    rm -f "/etc/systemd/system/tv-garden.service"
    rm -f "/etc/systemd/system/tv-garden-daily.timer"
    
    # Remove installation directory
    rm -rf "$INSTALL_DIR"
    
    # Remove web directory (ask first)
    if [ -d "/var/www/tv-garden" ]; then
        read -p "Remove web directory /var/www/tv-garden? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "/var/www/tv-garden"
        fi
    fi
    
    # Remove log directory (ask first)
    if [ -d "/var/log/tv-garden" ]; then
        read -p "Remove log directory /var/log/tv-garden? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "/var/log/tv-garden"
        fi
    fi
    
    # Reload systemd
    systemctl daemon-reload
    
    print_success "TV Garden service uninstalled"
}

# Main installation logic
main() {
    case "${1:-install}" in
        "install")
            print_status "Installing TV Garden service..."
            check_root
            check_requirements
            install_dependencies
            create_directories
            copy_files
            install_service
            run_initial_extraction
            start_services
            show_status
            ;;
        "uninstall")
            check_root
            uninstall
            ;;
        "status")
            if [ -f "$INSTALL_DIR/daily_tv_garden.sh" ]; then
                "$INSTALL_DIR/daily_tv_garden.sh" status
            else
                print_error "TV Garden service not installed"
                exit 1
            fi
            ;;
        *)
            echo "Usage: $0 {install|uninstall|status}"
            echo ""
            echo "Commands:"
            echo "  install   - Install TV Garden service (default)"
            echo "  uninstall - Remove TV Garden service"
            echo "  status    - Show service status"
            exit 1
            ;;
    esac
}

main "$@"
