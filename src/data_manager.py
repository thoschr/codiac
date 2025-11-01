"""
Data persistence layer for the interview preparation tracker.
"""
import json
import os
from pathlib import Path
from typing import Optional

try:
    from .models import ProgressTracker
except ImportError:
    from models import ProgressTracker


class DataManager:
    """Handles saving and loading of progress data."""
    
    def __init__(self, data_file: str = "interview_progress.json", loc_file: str = "codiac_location.json"):
        loc_path = Path.home() / ".codiac"
        self.data_location = loc_path / loc_file
        
        if not self.data_location.exists():
            # Create default data file location
            self.data_file = loc_path / data_file
            loc = {
                "data_location": str(self.data_file)
            }
            try:
                os.makedirs(os.path.dirname(self.data_location), exist_ok=True)
                # Save new data location file
                with open(self.data_location, 'w', encoding='utf-8') as f:
                    json.dump(loc, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error creating data location file: {e}")
                # Fallback to current directory if home directory fails
                self.data_file = Path(data_file)
        else:
            # Read existing data location from json
            try:
                with open(self.data_location, 'r', encoding='utf-8') as f:
                    location_data = json.load(f)
                    self.data_file = Path(location_data["data_location"])
                    print(f"Data file: {self.data_file}")
            except Exception as e:
                print(f"Error reading data location: {e}")
                # Fallback to default location
                self.data_file = loc_path / data_file
    
    def save(self, tracker: ProgressTracker) -> bool:
        """Save progress tracker to file."""
        try:
            # Save new data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(tracker.to_dict(), f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load(self) -> Optional[ProgressTracker]:
        """Load progress tracker from file."""
        if not self.data_file.exists():
            return None
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProgressTracker.from_dict(data)
        except Exception as e:
            print(f"Error loading data: {e}")
            
            return None
    
    def export_to_json(self, tracker: ProgressTracker, filename: str) -> bool:
        """Export data to a custom JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tracker.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def import_from_json(self, filename: str) -> Optional[ProgressTracker]:
        """Import data from a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProgressTracker.from_dict(data)
        except Exception as e:
            print(f"Error importing data: {e}")
            return None