"""
Integration tests for the Interview Tracker application.
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta

from src.models import ProgressTracker, Problem, Topic, StudySession, Difficulty, Status
from src.data_manager import DataManager
from src.analytics import ProgressAnalyzer


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
    
    def test_analytics_integration(self):
        """Test analytics integration with real data."""
        # Create tracker with comprehensive data
        tracker = ProgressTracker()
        
        # Add topics
        topics = [
            Topic("Arrays", "Array problems"),
            Topic("Strings", "String problems"),
            Topic("Trees", "Tree problems")
        ]
        for topic in topics:
            tracker.add_topic(topic)
        
        # Add problems with various statuses and difficulties
        problems_data = [
            ("Two Sum", "Arrays", Difficulty.EASY, Status.COMPLETED),
            ("Three Sum", "Arrays", Difficulty.MEDIUM, Status.IN_PROGRESS),
            ("Valid Palindrome", "Strings", Difficulty.EASY, Status.COMPLETED),
            ("Binary Tree Inorder", "Trees", Difficulty.MEDIUM, Status.NOT_STARTED),
            ("Serialize Tree", "Trees", Difficulty.HARD, Status.NEEDS_REVIEW),
        ]
        
        for title, topic_name, difficulty, status in problems_data:
            problem = Problem(title, difficulty, f"Description for {title}", topic=topic_name)
            problem.status = status
            if status == Status.COMPLETED:
                problem.mark_completed()
            tracker.add_problem(problem)
        
        # Add study sessions
        sessions = [
            StudySession(60, "Arrays practice", ["Two Sum", "Three Sum"]),
            StudySession(45, "String problems", ["Valid Palindrome"]),
            StudySession(90, "Tree traversal", ["Binary Tree Inorder"]),
        ]
        
        for session in sessions:
            tracker.add_session(session)
        
        # Create analyzer
        analyzer = ProgressAnalyzer(tracker)
        
        # Test various analytics functions
        time_dist = analyzer.get_time_distribution()
        assert isinstance(time_dist, dict)
        
        difficulty_rates = analyzer.get_difficulty_completion_rates()
        assert isinstance(difficulty_rates, dict)
        
        insights = analyzer.get_productivity_insights()
        assert isinstance(insights, dict)
        assert len(insights) > 0
        
        recommendations = analyzer.get_recommendations()
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        weekly_progress = analyzer.get_weekly_progress()
        assert isinstance(weekly_progress, dict)
        assert "weeks" in weekly_progress
    
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
        
        # Test that analytics still work efficiently
        analyzer = ProgressAnalyzer(tracker)
        
        # These should complete quickly even with large dataset
        stats = tracker.get_overall_stats()
        assert stats['total_problems'] == 100
        
        insights = analyzer.get_productivity_insights()
        assert len(insights) > 0
        
        # Test recalculation with large dataset
        updated_counts = tracker.recalculate_attempt_counters()
        assert len(updated_counts) > 0