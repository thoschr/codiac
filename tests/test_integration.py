"""
Integration tests for the Interview Tracker application.
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta

from src.models import ProgressTracker, Problem, Topic, StudySession, Difficulty, Status
from src.data_manager import DataManager


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete workflows."""
    
    def test_complete_problem_management_workflow(self):
        """Test complete problem management workflow."""
        # Create tracker
        tracker = ProgressTracker()
        
        # Add topic
        topic = Topic("Arrays", "Array manipulation problems")
        tracker.add_topic(topic)
        
        # Add problem
        problem = Problem(
            "Two Sum",
            Difficulty.EASY,
            "Find two numbers that add up to target",
            "https://leetcode.com/problems/two-sum/",
            "Arrays"
        )
        tracker.add_problem(problem)
        
        # Verify problem is linked to topic
        assert problem.title in tracker.problems
        assert problem in topic.problems
        assert problem.topic == topic.name
        
        # Work on problem (simulate study session)
        session = StudySession(60, "Worked on Two Sum problem", ["Two Sum"])
        tracker.add_session(session)
        
        # Verify attempt counter was incremented
        assert problem.attempts == 1
        
        # Mark problem as completed
        problem.mark_completed()
        
        # Verify completion
        assert problem.status == Status.COMPLETED
        assert problem.completed_at is not None
        
        # Get overall stats
        stats = tracker.get_overall_stats()
        assert stats['total_problems'] == 1
        assert stats['completed_problems'] == 1
        assert stats['completion_rate'] == 100.0
    
    def test_data_persistence_workflow(self):
        """Test complete data persistence workflow."""
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()
        
        try:
            # Create data manager
            data_manager = DataManager(temp_file.name)
            
            # Create and populate tracker
            original_tracker = ProgressTracker()
            
            # Add some data
            topic = Topic("Testing", "Test topic")
            original_tracker.add_topic(topic)
            
            problem = Problem("Test Problem", Difficulty.MEDIUM, "Test description")
            problem.add_note("Test note")
            problem.add_time(30)
            original_tracker.add_problem(problem)
            
            session = StudySession(45, "Test session", ["Test Problem"])
            original_tracker.add_session(session)
            
            # Save data
            save_result = data_manager.save(original_tracker)
            assert save_result is True
            
            # Load data
            loaded_tracker = data_manager.load()
            assert loaded_tracker is not None
            
            # Verify data integrity
            assert len(loaded_tracker.problems) == len(original_tracker.problems)
            assert len(loaded_tracker.topics) == len(original_tracker.topics)
            assert len(loaded_tracker.sessions) == len(original_tracker.sessions)
            
            # Verify specific data
            loaded_problem = loaded_tracker.problems["Test Problem"]
            assert loaded_problem.title == problem.title
            assert loaded_problem.difficulty == problem.difficulty
            assert loaded_problem.attempts == 1  # Should be incremented by session
            
        finally:
            # Clean up
            try:
                os.unlink(temp_file.name)
            except FileNotFoundError:
                pass
    
    def test_rotation_workflow(self):
        """Test problem rotation workflow."""
        tracker = ProgressTracker()
        
        # Add completed problems
        completed_problems = []
        for i in range(3):
            problem = Problem(f"Problem {i+1}", Difficulty.EASY, f"Description {i+1}")
            problem.mark_completed()
            tracker.add_problem(problem)
            completed_problems.append(problem)
        
        # Test rotation selection
        selected_problem = tracker.get_next_rotation_problem()
        assert selected_problem is not None
        assert selected_problem.status == Status.COMPLETED
        
        # Mark as rotation completed
        selected_problem.mark_rotation_completed()
        
        # Verify rotation stats
        stats = tracker.get_rotation_stats()
        assert stats['total_completed'] == 3
        assert stats['total_reviewed'] == 1
        assert stats['pending_review'] == 2
        
        # Get next problem (should be different or follow rotation logic)
        next_problem = tracker.get_next_rotation_problem()
        assert next_problem is not None
    
    def test_problem_deletion_workflow(self):
        """Test problem deletion workflow."""
        tracker = ProgressTracker()
        
        # Add topic and problem
        topic = Topic("Testing", "Test topic")
        tracker.add_topic(topic)
        
        problem = Problem("Test Problem", Difficulty.EASY, "Test", topic="Testing")
        tracker.add_problem(problem)
        
        # Add session referencing the problem
        session = StudySession(30, "Test session", ["Test Problem"])
        tracker.add_session(session)
        
        # Verify initial state
        assert "Test Problem" in tracker.problems
        assert problem in topic.problems
        assert "Test Problem" in session.problems_worked
        
        # Delete problem
        result = tracker.delete_problem("Test Problem")
        assert result is True
        
        # Verify deletion cleanup
        assert "Test Problem" not in tracker.problems
        assert problem not in topic.problems
        assert "Test Problem" not in session.problems_worked
    
    @pytest.mark.slow
    def test_large_dataset_performance(self):
        """Test performance with larger dataset."""
        tracker = ProgressTracker()
        
        # Add many topics
        for i in range(10):
            topic = Topic(f"Topic {i}", f"Description for topic {i}")
            tracker.add_topic(topic)
        
        # Add many problems
        topics = list(tracker.topics.keys())
        for i in range(100):
            topic_name = topics[i % len(topics)]
            difficulty = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD][i % 3]
            problem = Problem(f"Problem {i}", difficulty, f"Description {i}", topic=topic_name)
            
            # Randomly set some as completed
            if i % 3 == 0:
                problem.mark_completed()
            
            tracker.add_problem(problem)
        
        # Add many sessions
        problem_titles = list(tracker.problems.keys())
        for i in range(50):
            # Select random problems for each session
            session_problems = problem_titles[i:i+3] if i+3 <= len(problem_titles) else problem_titles[i:]
            session = StudySession(60, f"Session {i}", session_problems)
            tracker.add_session(session)
        
        # These should complete quickly even with large dataset
        stats = tracker.get_overall_stats()
        assert stats['total_problems'] == 100
        
    def test_database_switching_workflow(self):
        """Test switching between different database files."""
        import tempfile
        
        # Create two temporary database files
        db1_file = tempfile.NamedTemporaryFile(mode='w', suffix='_db1.json', delete=False)
        db2_file = tempfile.NamedTemporaryFile(mode='w', suffix='_db2.json', delete=False)
        db1_file.close()
        db2_file.close()
        
        try:
            # Create first database with some data
            dm1 = DataManager(db1_file.name)
            tracker1 = ProgressTracker()
            
            topic1 = Topic("Database 1 Topic", "First database topic")
            tracker1.add_topic(topic1)
            
            problem1 = Problem("DB1 Problem", Difficulty.EASY, "Problem in first DB", topic="Database 1 Topic")
            tracker1.add_problem(problem1)
            
            # Save first database
            assert dm1.save(tracker1) is True
            
            # Create second database with different data
            dm2 = DataManager(db2_file.name)
            tracker2 = ProgressTracker()
            
            topic2 = Topic("Database 2 Topic", "Second database topic")
            tracker2.add_topic(topic2)
            
            problem2 = Problem("DB2 Problem", Difficulty.HARD, "Problem in second DB", topic="Database 2 Topic")
            tracker2.add_problem(problem2)
            
            # Save second database
            assert dm2.save(tracker2) is True
            
            # Verify data separation
            loaded_tracker1 = dm1.load()
            loaded_tracker2 = dm2.load()
            
            assert len(loaded_tracker1.problems) == 1
            assert len(loaded_tracker2.problems) == 1
            assert "DB1 Problem" in loaded_tracker1.problems
            assert "DB2 Problem" in loaded_tracker2.problems
            assert "DB1 Problem" not in loaded_tracker2.problems
            assert "DB2 Problem" not in loaded_tracker1.problems
            
            # Test switching between databases
            dm_switch = DataManager(db1_file.name)
            loaded_from_switch = dm_switch.load()
            assert "DB1 Problem" in loaded_from_switch.problems
            
            # Switch to second database
            dm_switch = DataManager(db2_file.name)
            loaded_from_switch = dm_switch.load()
            assert "DB2 Problem" in loaded_from_switch.problems
            
        finally:
            # Cleanup
            for file_path in [db1_file.name, db2_file.name]:
                try:
                    os.unlink(file_path)
                except FileNotFoundError:
                    pass