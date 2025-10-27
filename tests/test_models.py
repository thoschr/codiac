"""
Tests for the models module.
"""
import pytest
from datetime import datetime, timedelta

from models import Problem, Topic, StudySession, ProgressTracker, Difficulty, Status


class TestProblem:
    """Tests for the Problem class."""
    
    def test_problem_creation(self, sample_problem):
        """Test creating a new problem."""
        assert sample_problem.title == "Two Sum"
        assert sample_problem.difficulty == Difficulty.EASY
        assert sample_problem.status == Status.NOT_STARTED
        assert sample_problem.attempts == 0
        assert sample_problem.time_spent == timedelta(0)
        assert sample_problem.completed_at is None
        assert sample_problem.rotation_completed_at is None
    
    def test_mark_completed(self, sample_problem):
        """Test marking a problem as completed."""
        before_time = datetime.now()
        sample_problem.mark_completed()
        after_time = datetime.now()
        
        assert sample_problem.status == Status.COMPLETED
        assert sample_problem.completed_at is not None
        assert before_time <= sample_problem.completed_at <= after_time
    
    def test_mark_rotation_completed(self, sample_problem):
        """Test marking a problem as completed in rotation."""
        before_time = datetime.now()
        sample_problem.mark_rotation_completed()
        after_time = datetime.now()
        
        assert sample_problem.rotation_completed_at is not None
        assert before_time <= sample_problem.rotation_completed_at <= after_time
    
    def test_add_note(self, sample_problem):
        """Test adding a note to a problem."""
        initial_count = len(sample_problem.notes)
        test_note = "This is a test note"
        
        sample_problem.add_note(test_note)
        
        assert len(sample_problem.notes) == initial_count + 1
        assert test_note in sample_problem.notes[-1]
    
    def test_add_time(self, sample_problem):
        """Test adding time to a problem."""
        initial_time = sample_problem.time_spent
        additional_minutes = 30
        
        sample_problem.add_time(additional_minutes)
        
        expected_time = initial_time + timedelta(minutes=additional_minutes)
        assert sample_problem.time_spent == expected_time
    
    def test_increment_attempts(self, sample_problem):
        """Test incrementing attempts counter."""
        initial_attempts = sample_problem.attempts
        
        sample_problem.increment_attempts()
        
        assert sample_problem.attempts == initial_attempts + 1
    
    def test_problem_serialization(self, sample_problem):
        """Test problem to_dict and from_dict methods."""
        # Modify problem to have some data
        sample_problem.add_note("Test note")
        sample_problem.add_time(45)
        sample_problem.increment_attempts()
        sample_problem.mark_completed()
        
        # Serialize to dict
        problem_dict = sample_problem.to_dict()
        
        # Verify dict structure
        assert problem_dict['title'] == sample_problem.title
        assert problem_dict['difficulty'] == sample_problem.difficulty.value
        assert problem_dict['status'] == sample_problem.status.value
        assert problem_dict['attempts'] == sample_problem.attempts
        
        # Deserialize from dict
        restored_problem = Problem.from_dict(problem_dict)
        
        # Verify restored problem
        assert restored_problem.title == sample_problem.title
        assert restored_problem.difficulty == sample_problem.difficulty
        assert restored_problem.status == sample_problem.status
        assert restored_problem.attempts == sample_problem.attempts


class TestTopic:
    """Tests for the Topic class."""
    
    def test_topic_creation(self, sample_topic):
        """Test creating a new topic."""
        assert sample_topic.name == "Arrays"
        assert sample_topic.description == "Array manipulation and algorithms"
        assert len(sample_topic.problems) == 0
    
    def test_add_problem(self, sample_topic, sample_problem):
        """Test adding a problem to a topic."""
        initial_count = len(sample_topic.problems)
        
        sample_topic.add_problem(sample_problem)
        
        assert len(sample_topic.problems) == initial_count + 1
        assert sample_problem in sample_topic.problems
        assert sample_problem.topic == sample_topic.name
    
    def test_completion_rate_empty(self, sample_topic):
        """Test completion rate calculation with no problems."""
        assert sample_topic.get_completion_rate() == 0.0
    
    def test_completion_rate_with_problems(self, sample_topic):
        """Test completion rate calculation with problems."""
        from tests.conftest import TestHelpers
        
        problems = TestHelpers.create_test_problems(3)
        for problem in problems:
            sample_topic.add_problem(problem)
        
        # No completed problems
        assert sample_topic.get_completion_rate() == 0.0
        
        # Mark one as completed
        problems[0].mark_completed()
        assert sample_topic.get_completion_rate() == pytest.approx(33.33, rel=1e-2)
        
        # Mark all as completed
        for problem in problems[1:]:
            problem.mark_completed()
        assert sample_topic.get_completion_rate() == 100.0
    
    def test_topic_serialization(self, sample_topic, sample_problem):
        """Test topic serialization and deserialization."""
        sample_topic.add_problem(sample_problem)
        
        # Serialize
        topic_dict = sample_topic.to_dict()
        
        # Verify dict structure
        assert topic_dict['name'] == sample_topic.name
        assert topic_dict['description'] == sample_topic.description
        assert len(topic_dict['problems']) == 1
        
        # Deserialize
        restored_topic = Topic.from_dict(topic_dict)
        
        # Verify restored topic
        assert restored_topic.name == sample_topic.name
        assert restored_topic.description == sample_topic.description
        assert len(restored_topic.problems) == len(sample_topic.problems)


class TestStudySession:
    """Tests for the StudySession class."""
    
    def test_session_creation(self, sample_session):
        """Test creating a study session."""
        assert sample_session.duration == timedelta(minutes=60)
        assert sample_session.notes == "Worked on array problems"
        assert "Two Sum" in sample_session.problems_worked
        assert "Three Sum" in sample_session.problems_worked
    
    def test_session_serialization(self, sample_session):
        """Test session serialization and deserialization."""
        # Serialize
        session_dict = sample_session.to_dict()
        
        # Verify dict structure
        assert session_dict['duration_minutes'] == 60
        assert session_dict['notes'] == sample_session.notes
        assert session_dict['problems_worked'] == sample_session.problems_worked
        
        # Deserialize
        restored_session = StudySession.from_dict(session_dict)
        
        # Verify restored session
        assert restored_session.duration == sample_session.duration
        assert restored_session.notes == sample_session.notes
        assert restored_session.problems_worked == sample_session.problems_worked


class TestProgressTracker:
    """Tests for the ProgressTracker class."""
    
    def test_tracker_creation(self, empty_tracker):
        """Test creating an empty progress tracker."""
        assert len(empty_tracker.problems) == 0
        assert len(empty_tracker.topics) == 0
        assert len(empty_tracker.sessions) == 0
    
    def test_add_topic(self, empty_tracker, sample_topic):
        """Test adding a topic to the tracker."""
        empty_tracker.add_topic(sample_topic)
        
        assert sample_topic.name in empty_tracker.topics
        assert empty_tracker.topics[sample_topic.name] == sample_topic
    
    def test_add_problem(self, empty_tracker, sample_problem, sample_topic):
        """Test adding a problem to the tracker."""
        # Add topic first
        empty_tracker.add_topic(sample_topic)
        
        # Add problem
        empty_tracker.add_problem(sample_problem)
        
        assert sample_problem.title in empty_tracker.problems
        assert empty_tracker.problems[sample_problem.title] == sample_problem
        assert sample_problem in sample_topic.problems
    
    def test_add_session_increments_attempts(self, empty_tracker, sample_problem, sample_session):
        """Test that adding a session increments problem attempts."""
        # Add problem to tracker
        empty_tracker.add_problem(sample_problem)
        
        # Initial attempts should be 0
        assert sample_problem.attempts == 0
        
        # Add session that references this problem
        session = StudySession(30, "Test session", [sample_problem.title])
        empty_tracker.add_session(session)
        
        # Attempts should be incremented
        assert sample_problem.attempts == 1
    
    def test_delete_problem(self, populated_tracker, sample_problem):
        """Test deleting a problem from the tracker."""
        problem_title = sample_problem.title
        
        # Verify problem exists
        assert problem_title in populated_tracker.problems
        
        # Delete problem
        result = populated_tracker.delete_problem(problem_title)
        
        # Verify deletion
        assert result is True
        assert problem_title not in populated_tracker.problems
    
    def test_delete_nonexistent_problem(self, empty_tracker):
        """Test deleting a problem that doesn't exist."""
        result = empty_tracker.delete_problem("Nonexistent Problem")
        assert result is False
    
    def test_recalculate_attempt_counters(self, empty_tracker):
        """Test recalculating attempt counters from sessions."""
        from tests.conftest import TestHelpers
        
        # Create test problems
        problems = TestHelpers.create_test_problems(2)
        for problem in problems:
            empty_tracker.add_problem(problem)
        
        # Create sessions referencing problems multiple times
        sessions = [
            StudySession(30, "Session 1", [problems[0].title]),
            StudySession(45, "Session 2", [problems[0].title, problems[1].title]),
            StudySession(60, "Session 3", [problems[1].title])
        ]
        
        # Set manual attempts (to be overridden)
        problems[0].attempts = 99
        problems[1].attempts = 88
        
        # Add sessions manually without triggering auto-increment
        for session in sessions:
            empty_tracker.sessions.append(session)
        
        # Recalculate
        updated_counts = empty_tracker.recalculate_attempt_counters()
        
        # Verify results
        assert updated_counts[problems[0].title] == 2  # Referenced in 2 sessions
        assert updated_counts[problems[1].title] == 2  # Referenced in 2 sessions
        assert problems[0].attempts == 2
        assert problems[1].attempts == 2
    
    def test_get_overall_stats(self, populated_tracker):
        """Test getting overall statistics."""
        stats = populated_tracker.get_overall_stats()
        
        assert 'total_problems' in stats
        assert 'completed_problems' in stats
        assert 'completion_rate' in stats
        assert 'total_study_time_hours' in stats
        assert 'total_sessions' in stats
        assert 'topics_count' in stats
        
        assert stats['total_problems'] >= 1
        assert stats['total_sessions'] >= 1
        assert stats['topics_count'] >= 1
    
    def test_get_rotation_stats(self, empty_tracker):
        """Test getting rotation statistics."""
        from tests.conftest import TestHelpers
        
        # Create and add completed problems
        problems = TestHelpers.create_test_problems(3)
        for problem in problems:
            problem.mark_completed()
            empty_tracker.add_problem(problem)
        
        # Mark one as reviewed in rotation
        problems[0].mark_rotation_completed()
        
        stats = empty_tracker.get_rotation_stats()
        
        assert stats['total_completed'] == 3
        assert stats['total_reviewed'] == 1
        assert stats['pending_review'] == 2
    
    def test_get_next_rotation_problem(self, empty_tracker):
        """Test getting next rotation problem."""
        from tests.conftest import TestHelpers
        
        # No completed problems
        assert empty_tracker.get_next_rotation_problem() is None
        
        # Add completed problems
        problems = TestHelpers.create_test_problems(2)
        for problem in problems:
            problem.mark_completed()
            empty_tracker.add_problem(problem)
        
        # Should return a problem
        next_problem = empty_tracker.get_next_rotation_problem()
        assert next_problem is not None
        assert next_problem.status == Status.COMPLETED