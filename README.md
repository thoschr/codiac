<p align="center">
  <picture>
    <img alt="Codiac Logo" src=".github/logo.png" width="80%">
  </picture>
</p>
# Interview Preparation Tracker

A Python GUI application to track your progress in interview preparation, including coding problems, topics studied, and overall progress.

## Features

- Track coding problems by topic (algorithms, data structures, etc.)
- Record difficulty levels and completion status
- Time tracking for study sessions
- Progress statistics and analytics
- Modern graphical user interface
- **Multiple database support** - Switch between different databases for different projects/goals

## Quick Start

```bash
python src/interview_tracker.py
```
or
```bash
python src/launch_gui.py
```

## GUI Features

The application provides an intuitive interface with multiple tabs:

- **📊 Dashboard**: Overview of your progress with statistics and recent activity
- **📝 Problems**: Manage coding problems with filtering, adding, editing, and progress tracking
- **📚 Topics**: Organize problems by study topics (Arrays, DP, Trees, etc.)
- **⏱️ Sessions**: Log and view study sessions with time tracking
- **🔄 Rotation**: Review completed problems on a rotation schedule

### GUI Controls
- **📁 Change DB button**: Switch between different database files or create new ones
- **Right-click** on problems for quick actions (mark completed, add time, add notes)
- **Double-click** problems to view detailed information
- **Right-click** on sessions for context menu (view details, delete)
- **Delete button** in Sessions tab to remove selected sessions
- **Filters** to find problems by topic, status, or difficulty
- **Visual progress indicators** with color-coded status

### Database Management
- **Switch databases**: Use the "📁 Change DB" button to load existing databases or create new ones
- **Auto-save**: Current data is automatically saved before switching
- **Data integrity**: All data is preserved when switching between databases
- **Fallback handling**: Graceful error handling for invalid or corrupted database files

## Data Structure

- **Topics**: Categories like "Arrays", "Dynamic Programming", "System Design"
- **Problems**: Individual coding problems with difficulty and status
- **Sessions**: Study sessions with time tracking and notes
- **Progress**: Overall statistics and completion rates

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python src/interview_tracker.py`

## Data Storage

- Data is automatically saved to JSON files
- Default location: `~/.codiac/interview_progress.json` 
- Database location is configurable via the GUI
- Configuration stored in: `~/.codiac/codiac_location.json`
