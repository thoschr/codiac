#!/bin/bash
# Setup script for Interview Tracker .desktop file

echo "🚀 Setting up Interview Tracker desktop integration..."

# Get the current directory (where the script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$SCRIPT_DIR/interview-tracker.desktop"

# Check if .desktop file exists
if [ ! -f "$DESKTOP_FILE" ]; then
    echo "❌ Error: interview-tracker.desktop file not found in $SCRIPT_DIR"
    exit 1
fi

# Create local applications directory if it doesn't exist
LOCAL_APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$LOCAL_APPS_DIR"

# Copy the .desktop file to local applications
cp "$DESKTOP_FILE" "$LOCAL_APPS_DIR/"

# Make it executable
chmod +x "$LOCAL_APPS_DIR/interview-tracker.desktop"

echo "✅ Desktop file installed to: $LOCAL_APPS_DIR/interview-tracker.desktop"

# Update desktop database (if available)
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$LOCAL_APPS_DIR"
    echo "✅ Desktop database updated"
fi

echo ""
echo "🎉 Setup complete! You can now:"
echo "   • Find 'Interview Tracker' in your applications menu"
echo "   • Search for it in your desktop environment"
echo "   • Right-click to pin it to your taskbar/dock"
echo ""
echo "📁 The application will run from: $SCRIPT_DIR"
echo "🐍 Using Python virtual environment: $SCRIPT_DIR/.venv"
echo ""
echo "Note: If you move the project folder, you'll need to run this setup again."