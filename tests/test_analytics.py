"""
Tests for the analytics module.
"""
import pytest
from datetime import datetime, timedelta

from src.analytics import ProgressAnalyzer
from src.models import ProgressTracker, Problem, StudySession, Difficulty, Status


class TestProgressAnalyzer:
    """Tests for the ProgressAnalyzer class."""
    
    @pytest.fixture
    def analyzer_with_data(self):
        """Create an analyzer with sample data."""
        tracker = ProgressTracker()
        
        # Create problems with different statuses and difficulties
        problems_data = [
            ("Easy Problem 1", Difficulty.EASY, Status.COMPLETED),
            ("Easy Problem 2", Difficulty.EASY, Status.IN_PROGRESS),
            ("Medium Problem 1", Difficulty.MEDIUM, Status.COMPLETED),
            ("Medium Problem 2", Difficulty.MEDIUM, Status.NOT_STARTED),
            ("Hard Problem 1", Difficulty.HARD, Status.NEEDS_REVIEW),
        ]
        
        for title, difficulty, status in problems_data:
            problem = Problem(title, difficulty, f"Description for {title}")
            problem.status = status
            if status == Status.COMPLETED:
                problem.mark_completed()
            tracker.add_problem(problem)
        
        # Create some sessions
        sessions = [
            StudySession(60, "Session 1", ["Easy Problem 1"]),
            StudySession(90, "Session 2", ["Medium Problem 1", "Easy Problem 2"]),
            StudySession(45, "Session 3", ["Hard Problem 1"]),
        ]
        
        for session in sessions:
            # Manually add to avoid auto-increment of attempts (for controlled testing)
            tracker.sessions.append(session)
        
        return ProgressAnalyzer(tracker)
    
    def test_analyzer_creation(self, empty_tracker):
        """Test creating a ProgressAnalyzer."""
        analyzer = ProgressAnalyzer(empty_tracker)
        assert analyzer.tracker == empty_tracker
    
    def test_get_time_distribution(self, analyzer_with_data):
        """Test getting time distribution by topic."""
        distribution = analyzer_with_data.get_time_distribution()
        
        assert isinstance(distribution, dict)
        # Should have topic names as keys and time values
        for topic, time_spent in distribution.items():
            assert isinstance(topic, str)
            assert isinstance(time_spent, (int, float))
    
    def test_get_difficulty_completion_rates(self, analyzer_with_data):
        """Test getting difficulty completion rates."""
        rates = analyzer_with_data.get_difficulty_completion_rates()
        
        assert isinstance(rates, dict)
        # Should have difficulty levels
        for difficulty, stats in rates.items():
            assert difficulty in [d.value for d in Difficulty]
            assert isinstance(stats, dict)
    
    def test_get_productivity_insights_empty(self, empty_tracker):
        """Test productivity insights with empty tracker."""
        analyzer = ProgressAnalyzer(empty_tracker)
        insights = analyzer.get_productivity_insights()
        
        assert isinstance(insights, dict)
        # With no sessions, should return a message
        assert "message" in insights
        assert insights["message"] == "No study sessions recorded yet"
    
    def test_get_productivity_insights_with_data(self, analyzer_with_data):
        """Test productivity insights with data."""
        insights = analyzer_with_data.get_productivity_insights()
        
        assert isinstance(insights, dict)
        assert len(insights) > 0
        # Should contain various productivity metrics
        assert "total_study_time" in insights
        assert "total_sessions" in insights
    
    def test_get_recommendations_empty(self, empty_tracker):
        """Test recommendations with empty tracker."""
        analyzer = ProgressAnalyzer(empty_tracker)
        recommendations = analyzer.get_recommendations()
        
        assert len(recommendations) > 0
        assert isinstance(recommendations, list)
        # Should still provide recommendations even with no data
        assert all(isinstance(rec, str) for rec in recommendations)
    
    def test_get_recommendations_with_data(self, analyzer_with_data):
        """Test recommendations with data."""
        recommendations = analyzer_with_data.get_recommendations()
        
        assert len(recommendations) > 0
        assert isinstance(recommendations, list)
        # Should provide meaningful recommendations
        recommendations_text = " ".join(recommendations)
        assert any(word in recommendations_text.lower() for word in 
                  ["practice", "review", "focus", "work", "try", "consider"])
    
    def test_get_weekly_progress_empty(self, empty_tracker):
        """Test weekly progress with no data."""
        analyzer = ProgressAnalyzer(empty_tracker)
        progress = analyzer.get_weekly_progress()
        
        assert isinstance(progress, dict)
        assert "weeks" in progress
        assert "completed" in progress
        assert "attempted" in progress
    
    def test_get_problem_attempts_analysis(self, analyzer_with_data):
        """Test problem attempts analysis."""
        analysis = analyzer_with_data.get_problem_attempts_analysis()
        
        assert isinstance(analysis, dict)
        # Should contain attempt statistics
        for stat_name, value in analysis.items():
            assert isinstance(stat_name, str)
            assert isinstance(value, (int, float))
    
    def test_get_weekly_progress_with_data(self, analyzer_with_data):
        """Test weekly progress with data."""
        progress = analyzer_with_data.get_weekly_progress(weeks=2)
        
        assert isinstance(progress, dict)
        assert len(progress["weeks"]) == 2
        assert len(progress["completed"]) == 2
        assert len(progress["attempted"]) == 2