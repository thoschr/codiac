"""
Pytest fixtures and test utilities for Interview Tracker tests.
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from src.models import ProgressTracker, Problem, Topic, StudySession, Difficulty, Status
from src.data_manager import DataManager


@pytest.fixture
def sample_problem():
    """Create a sample problem for testing."""
    return Problem(
        title="Two Sum",
        difficulty=Difficulty.EASY,
        description="Given an array of integers, return indices of two numbers that add up to a target.",
        url="https://leetcode.com/problems/two-sum/",
        topic="Arrays"
    )


@pytest.fixture
def sample_topic():
    """Create a sample topic for testing."""
    return Topic("Arrays", "Array manipulation and algorithms")


@pytest.fixture
def sample_session():
    """Create a sample study session for testing."""
    return StudySession(
        duration_minutes=60,
        notes="Worked on array problems",
        problems_worked=["Two Sum", "Three Sum"]
    )


@pytest.fixture
def empty_tracker():
    """Create an empty progress tracker for testing."""
    return ProgressTracker()


@pytest.fixture
def populated_tracker(sample_problem, sample_topic, sample_session):
    """Create a progress tracker with sample data."""
    tracker = ProgressTracker()
    
    # Add topic
    tracker.add_topic(sample_topic)
    
    # Add problem
    tracker.add_problem(sample_problem)
    
    # Add session
    tracker.add_session(sample_session)
    
    return tracker


@pytest.fixture
def temp_data_file():
    """Create a temporary file for testing data persistence."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def data_manager(temp_data_file):
    """Create a DataManager instance with a temporary file."""
    return DataManager(temp_data_file)


class TestHelpers:
    """Helper methods for tests."""
    
    @staticmethod
    def create_test_problems(count=3):
        """Create multiple test problems."""
        problems = []
        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        
        for i in range(count):
            problem = Problem(
                title=f"Test Problem {i+1}",
                difficulty=difficulties[i % len(difficulties)],
                description=f"Description for test problem {i+1}",
                topic="Testing"
            )
            problems.append(problem)
        
        return problems
    
    @staticmethod
    def assert_problem_equals(problem1, problem2):
        """Assert that two problems are equal."""
        assert problem1.title == problem2.title
        assert problem1.difficulty == problem2.difficulty
        assert problem1.description == problem2.description
        assert problem1.url == problem2.url
        assert problem1.topic == problem2.topic
        assert problem1.status == problem2.status