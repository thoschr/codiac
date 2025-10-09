# Interview Preparation Tracker

A Python GUI application to track your progress in interview preparation, including coding problems, topics studied, and overall progress.

## Features

- Track coding problems by topic (algorithms, data structures, etc.)
- Record difficulty levels and completion status
- Time tracking for study sessions
- Progress statistics and analytics
- Modern graphical user interface
- Data persistence with automatic backups

## Quick Start

```bash
python interview_tracker.py
```
or
```bash
python launch_gui.py
```

## GUI Features

The application provides an intuitive interface with multiple tabs:

- **📊 Dashboard**: Overview of your progress with statistics and recent activity
- **📝 Problems**: Manage coding problems with filtering, adding, editing, and progress tracking
- **📚 Topics**: Organize problems by study topics (Arrays, DP, Trees, etc.)
- **⏱️ Sessions**: Log and view study sessions with time tracking

### GUI Controls
- **Right-click** on problems for quick actions (mark completed, add time, add notes)
- **Double-click** problems to view detailed information
- **Right-click** on sessions for context menu (view details, delete)
- **Delete button** in Sessions tab to remove selected sessions
- **Filters** to find problems by topic, status, or difficulty
- **Visual progress indicators** with color-coded status

## Data Structure

- **Topics**: Categories like "Arrays", "Dynamic Programming", "System Design"
- **Problems**: Individual coding problems with difficulty and status
- **Sessions**: Study sessions with time tracking and notes
- **Progress**: Overall statistics and completion rates

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python interview_tracker.py`

## Data Storage

All data is automatically saved to `interview_progress.json` with backup files created for safety.