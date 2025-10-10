"""
Data models for the interview preparation tracker.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import json


class Difficulty(Enum):
    """Difficulty levels for problems."""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Status(Enum):
    """Status of problem completion."""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    NEEDS_REVIEW = "Needs Review"


class Topic:
    """Represents an interview preparation topic."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.problems: List[Problem] = []
        self.created_at = datetime.now()
    
    def add_problem(self, problem: 'Problem'):
        """Add a problem to this topic."""
        problem.topic = self.name
        self.problems.append(problem)
    
    def get_completion_rate(self) -> float:
        """Calculate completion rate for this topic."""
        if not self.problems:
            return 0.0
        completed = sum(1 for p in self.problems if p.status == Status.COMPLETED)
        return completed / len(self.problems) * 100
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'problems': [p.to_dict() for p in self.problems],
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Topic':
        """Create Topic from dictionary."""
        topic = cls(data['name'], data['description'])
        topic.created_at = datetime.fromisoformat(data['created_at'])
        topic.problems = [Problem.from_dict(p) for p in data['problems']]
        return topic


class Problem:
    """Represents a coding problem."""
    
    def __init__(self, title: str, difficulty: Difficulty, description: str = "", 
                 url: str = "", topic: str = ""):
        self.title = title
        self.difficulty = difficulty
        self.description = description
        self.url = url
        self.topic = topic
        self.status = Status.NOT_STARTED
        self.notes: List[str] = []
        self.attempts = 0
        self.time_spent = timedelta(0)
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.rotation_completed_at: Optional[datetime] = None
    
    def mark_completed(self):
        """Mark problem as completed."""
        self.status = Status.COMPLETED
        self.completed_at = datetime.now()
    
    def mark_rotation_completed(self):
        """Mark problem as completed in rotation review."""
        self.rotation_completed_at = datetime.now()
    
    def add_note(self, note: str):
        """Add a note to this problem."""
        self.notes.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - {note}")
    
    def add_time(self, minutes: int):
        """Add time spent on this problem."""
        self.time_spent += timedelta(minutes=minutes)
    
    def increment_attempts(self):
        """Increment the number of attempts."""
        self.attempts += 1
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'title': self.title,
            'difficulty': self.difficulty.value,
            'description': self.description,
            'url': self.url,
            'topic': self.topic,
            'status': self.status.value,
            'notes': self.notes,
            'attempts': self.attempts,
            'time_spent_minutes': int(self.time_spent.total_seconds() / 60),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'rotation_completed_at': self.rotation_completed_at.isoformat() if self.rotation_completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Problem':
        """Create Problem from dictionary."""
        problem = cls(
            data['title'], 
            Difficulty(data['difficulty']), 
            data['description'],
            data['url'],
            data['topic']
        )
        problem.status = Status(data['status'])
        problem.notes = data['notes']
        problem.attempts = data['attempts']
        problem.time_spent = timedelta(minutes=data['time_spent_minutes'])
        problem.created_at = datetime.fromisoformat(data['created_at'])
        if data['completed_at']:
            problem.completed_at = datetime.fromisoformat(data['completed_at'])
        if data.get('rotation_completed_at'):
            problem.rotation_completed_at = datetime.fromisoformat(data['rotation_completed_at'])
        return problem


class StudySession:
    """Represents a study session."""
    
    def __init__(self, duration_minutes: int, notes: str = "", problems_worked: List[str] = None):
        self.duration = timedelta(minutes=duration_minutes)
        self.notes = notes
        self.problems_worked = problems_worked or []
        self.date = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'duration_minutes': int(self.duration.total_seconds() / 60),
            'notes': self.notes,
            'problems_worked': self.problems_worked,
            'date': self.date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StudySession':
        """Create StudySession from dictionary."""
        session = cls(data['duration_minutes'], data['notes'], data['problems_worked'])
        session.date = datetime.fromisoformat(data['date'])
        return session


class ProgressTracker:
    """Main class to track interview preparation progress."""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.problems: Dict[str, Problem] = {}
        self.sessions: List[StudySession] = []
    
    def add_topic(self, topic: Topic):
        """Add a topic to the tracker."""
        self.topics[topic.name] = topic
    
    def add_problem(self, problem: Problem):
        """Add a problem to the tracker."""
        self.problems[problem.title] = problem
        
        # Add to topic if it exists
        if problem.topic in self.topics:
            self.topics[problem.topic].add_problem(problem)
    
    def add_session(self, session: StudySession):
        """Add a study session."""
        self.sessions.append(session)
    
    def get_overall_stats(self) -> dict:
        """Get overall progress statistics."""
        total_problems = len(self.problems)
        completed_problems = sum(1 for p in self.problems.values() if p.status == Status.COMPLETED)
        total_time = sum((s.duration for s in self.sessions), timedelta(0))
        
        return {
            'total_problems': total_problems,
            'completed_problems': completed_problems,
            'completion_rate': (completed_problems / total_problems * 100) if total_problems > 0 else 0,
            'total_study_time_hours': total_time.total_seconds() / 3600,
            'total_sessions': len(self.sessions),
            'topics_count': len(self.topics)
        }
    
    def get_topic_stats(self) -> Dict[str, dict]:
        """Get statistics by topic."""
        stats = {}
        for topic_name, topic in self.topics.items():
            total = len(topic.problems)
            completed = sum(1 for p in topic.problems if p.status == Status.COMPLETED)
            stats[topic_name] = {
                'total_problems': total,
                'completed_problems': completed,
                'completion_rate': (completed / total * 100) if total > 0 else 0
            }
        return stats
    
    def get_problems_by_difficulty(self) -> Dict[str, int]:
        """Get problem count by difficulty."""
        difficulty_count = {d.value: 0 for d in Difficulty}
        for problem in self.problems.values():
            difficulty_count[problem.difficulty.value] += 1
        return difficulty_count
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'topics': {name: topic.to_dict() for name, topic in self.topics.items()},
            'problems': {title: problem.to_dict() for title, problem in self.problems.items()},
            'sessions': [session.to_dict() for session in self.sessions]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProgressTracker':
        """Create ProgressTracker from dictionary."""
        tracker = cls()
        
        # Load topics first
        for name, topic_data in data.get('topics', {}).items():
            tracker.topics[name] = Topic.from_dict(topic_data)
        
        # Load problems and ensure they're properly linked to topics
        for title, problem_data in data.get('problems', {}).items():
            problem = Problem.from_dict(problem_data)
            tracker.problems[title] = problem
            
            # Ensure problem is added to the correct topic
            if problem.topic in tracker.topics:
                # Check if problem is already in topic's problems list
                if problem not in tracker.topics[problem.topic].problems:
                    tracker.topics[problem.topic].add_problem(problem)
        
        # Load sessions
        for session_data in data.get('sessions', []):
            tracker.sessions.append(StudySession.from_dict(session_data))
        
        return tracker
    
    def rebuild_topic_connections(self):
        """Rebuild connections between topics and problems to ensure data consistency."""
        # Clear all problems from topics
        for topic in self.topics.values():
            topic.problems.clear()
        
        # Re-add all problems to their respective topics
        for problem in self.problems.values():
            if problem.topic in self.topics:
                self.topics[problem.topic].add_problem(problem)
    
    def get_next_rotation_problem(self) -> Optional[Problem]:
        """Get the next problem for rotation review."""
        import random
        
        # Get all completed problems
        completed_problems = [p for p in self.problems.values() if p.status == Status.COMPLETED]
        
        if not completed_problems:
            return None
        
        # Separate problems into two groups:
        # 1. Problems that haven't been reviewed in rotation yet
        # 2. Problems that have been reviewed but all others have been reviewed too
        
        # Find the latest rotation completion time among all problems
        latest_rotation_times = [p.rotation_completed_at for p in completed_problems if p.rotation_completed_at]
        
        if not latest_rotation_times:
            # No problems have been reviewed yet, pick any completed problem
            return random.choice(completed_problems)
        
        # Get the latest rotation completion time
        latest_rotation_time = max(latest_rotation_times)
        
        # Find problems that haven't been reviewed since the latest "round" started
        unreviewed_in_current_round = [
            p for p in completed_problems 
            if not p.rotation_completed_at or p.rotation_completed_at < latest_rotation_time
        ]
        
        if unreviewed_in_current_round:
            # Still have problems to review in current round
            return random.choice(unreviewed_in_current_round)
        else:
            # All problems have been reviewed in current round, start new round
            # Pick any completed problem (start fresh round)
            return random.choice(completed_problems)
    
    def get_rotation_stats(self) -> dict:
        """Get rotation statistics."""
        completed_problems = [p for p in self.problems.values() if p.status == Status.COMPLETED]
        reviewed_problems = [p for p in completed_problems if p.rotation_completed_at]
        
        return {
            'total_completed': len(completed_problems),
            'total_reviewed': len(reviewed_problems),
            'pending_review': len(completed_problems) - len(reviewed_problems)
        }
    
    def delete_problem(self, problem_title: str) -> bool:
        """Delete a problem and clean up all references to it.
        
        Returns True if the problem was found and deleted, False otherwise.
        """
        if problem_title not in self.problems:
            return False
        
        problem = self.problems[problem_title]
        
        # Remove from problems dictionary
        del self.problems[problem_title]
        
        # Remove from topic's problems list if the topic exists
        if problem.topic in self.topics:
            topic = self.topics[problem.topic]
            if problem in topic.problems:
                topic.problems.remove(problem)
        
        # Remove from study sessions' problems_worked lists
        for session in self.sessions:
            if problem_title in session.problems_worked:
                session.problems_worked.remove(problem_title)
        
        return True