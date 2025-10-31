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