"""
Tests for the data_manager module.
"""
import pytest
import json
import os
from pathlib import Path

from src.data_manager import DataManager
from src.models import ProgressTracker, Topic


class TestDataManager:
    """Tests for the DataManager class."""
    
    def test_data_manager_creation(self, temp_data_file):
        """Test creating a DataManager instance."""
        manager = DataManager(temp_data_file)
        
        assert manager.data_file == Path(temp_data_file)
    
    def test_save_empty_tracker(self, data_manager, empty_tracker):
        """Test saving an empty tracker."""
        result = data_manager.save(empty_tracker)
        
        assert result is True
        assert data_manager.data_file.exists()
    
    def test_save_populated_tracker(self, data_manager, populated_tracker):
        """Test saving a populated tracker."""
        result = data_manager.save(populated_tracker)
        
        assert result is True
        assert data_manager.data_file.exists()
        
        # Verify file content
        with open(data_manager.data_file, 'r') as f:
            data = json.load(f)
        
        assert 'problems' in data
        assert 'topics' in data
        assert 'sessions' in data
    
    def test_load_nonexistent_file(self, data_manager):
        """Test loading from a non-existent file."""
        result = data_manager.load()
        assert result is None
    
    def test_save_and_load_cycle(self, data_manager, populated_tracker):
        """Test complete save and load cycle."""
        # Save tracker
        save_result = data_manager.save(populated_tracker)
        assert save_result is True
        
        # Load tracker
        loaded_tracker = data_manager.load()
        assert loaded_tracker is not None
        
        # Verify data integrity
        assert len(loaded_tracker.problems) == len(populated_tracker.problems)
        assert len(loaded_tracker.topics) == len(populated_tracker.topics)
        assert len(loaded_tracker.sessions) == len(populated_tracker.sessions)
        
        # Check specific problem
        original_problems = list(populated_tracker.problems.keys())
        if original_problems:
            problem_title = original_problems[0]
            original_problem = populated_tracker.problems[problem_title]
            loaded_problem = loaded_tracker.problems[problem_title]
            
            assert loaded_problem.title == original_problem.title
            assert loaded_problem.difficulty == original_problem.difficulty
            assert loaded_problem.status == original_problem.status
    
    def test_invalid_json_handling(self, data_manager, temp_data_file):
        """Test handling of invalid JSON files."""
        # Write invalid JSON to file
        with open(temp_data_file, 'w') as f:
            f.write("invalid json content {")
        
        # Try to load
        result = data_manager.load()
        
        # Should return None due to invalid JSON
        assert result is None
    
    def test_custom_file_path_creation(self):
        """Test creating DataManager with custom file path."""
        import tempfile
        
        # Create temporary file path
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        custom_path = temp_file.name
        temp_file.close()
        
        try:
            # Create DataManager with custom path
            manager = DataManager(custom_path)
            
            # Should use the custom path directly
            assert str(manager.data_file) == custom_path
            
            # Test saving and loading with custom path
            from src.models import ProgressTracker, Topic
            tracker = ProgressTracker()
            topic = Topic("Test Topic", "Test description")
            tracker.add_topic(topic)
            
            # Save and verify
            assert manager.save(tracker) is True
            assert os.path.exists(custom_path)
            
            # Load and verify
            loaded_tracker = manager.load()
            assert loaded_tracker is not None
            assert "Test Topic" in loaded_tracker.topics
            
        finally:
            # Cleanup
            try:
                os.unlink(custom_path)
            except FileNotFoundError:
                pass
    
    def test_export_import_functionality(self, data_manager, populated_tracker):
        """Test export and import functionality."""
        import tempfile
        
        # Create temporary export file
        temp_export = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        export_path = temp_export.name
        temp_export.close()
        
        try:
            # Export data
            export_result = data_manager.export_to_json(populated_tracker, export_path)
            assert export_result is True
            assert os.path.exists(export_path)
            
            # Import data
            imported_tracker = data_manager.import_from_json(export_path)
            assert imported_tracker is not None
            
            # Verify data integrity
            assert len(imported_tracker.problems) == len(populated_tracker.problems)
            assert len(imported_tracker.topics) == len(populated_tracker.topics)
            assert len(imported_tracker.sessions) == len(populated_tracker.sessions)
            
        finally:
            # Cleanup
            try:
                os.unlink(export_path)
            except FileNotFoundError:
                pass
    
    def test_export_import_error_handling(self, data_manager, populated_tracker):
        """Test error handling in export/import operations."""
        # Test export to invalid path
        export_result = data_manager.export_to_json(populated_tracker, "/invalid/path/file.json")
        assert export_result is False
        
        # Test import from non-existent file
        imported_tracker = data_manager.import_from_json("/non/existent/file.json")
        assert imported_tracker is None