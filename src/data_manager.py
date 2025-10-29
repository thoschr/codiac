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
    
    def __init__(self, data_file: str = "interview_progress.json"):
        self.data_file = Path(data_file)
        self.backup_file = Path(f"{data_file}.backup")
    
    def save(self, tracker: ProgressTracker) -> bool:
        """Save progress tracker to file."""
        try:
            # Create backup of existing file
            if self.data_file.exists():
                self.data_file.replace(self.backup_file)
            
            # Save new data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(tracker.to_dict(), f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            # Restore backup if save failed
            if self.backup_file.exists():
                self.backup_file.replace(self.data_file)
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
            
            # Try to load from backup
            if self.backup_file.exists():
                try:
                    with open(self.backup_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print("Loaded from backup file.")
                    return ProgressTracker.from_dict(data)
                except Exception as backup_e:
                    print(f"Error loading backup: {backup_e}")
            
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
    
    def create_sample_data(self) -> ProgressTracker:
        """Create sample data for demonstration."""
        try:
            from .models import Topic, Problem, Difficulty, Status, StudySession
        except ImportError:
            from models import Topic, Problem, Difficulty, Status, StudySession
        
        tracker = ProgressTracker()
        
        # Create topics
        arrays_topic = Topic("Arrays", "Array manipulation and algorithms")
        strings_topic = Topic("Strings", "String processing and algorithms")
        dp_topic = Topic("Dynamic Programming", "Dynamic programming problems")
        trees_topic = Topic("Trees", "Tree data structures and algorithms")
        graphs_topic = Topic("Graphs", "Graph algorithms and traversal")
        
        tracker.add_topic(arrays_topic)
        tracker.add_topic(strings_topic)
        tracker.add_topic(dp_topic)
        tracker.add_topic(trees_topic)
        tracker.add_topic(graphs_topic)
        
        # Create sample problems
        problems = [
            # Arrays
            Problem("Two Sum", Difficulty.EASY, 
                   "Find two numbers that add up to target", 
                   "https://leetcode.com/problems/two-sum/", "Arrays"),
            Problem("Best Time to Buy and Sell Stock", Difficulty.EASY,
                   "Find max profit from stock prices",
                   "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/", "Arrays"),
            Problem("3Sum", Difficulty.MEDIUM,
                   "Find all unique triplets that sum to zero",
                   "https://leetcode.com/problems/3sum/", "Arrays"),
            Problem("Product of Array Except Self", Difficulty.MEDIUM,
                   "Return array where each element is product of all others",
                   "https://leetcode.com/problems/product-of-array-except-self/", "Arrays"),
            
            # Strings
            Problem("Valid Anagram", Difficulty.EASY,
                   "Check if two strings are anagrams",
                   "https://leetcode.com/problems/valid-anagram/", "Strings"),
            Problem("Longest Palindromic Substring", Difficulty.MEDIUM,
                   "Find the longest palindromic substring",
                   "https://leetcode.com/problems/longest-palindromic-substring/", "Strings"),
            Problem("Group Anagrams", Difficulty.MEDIUM,
                   "Group strings that are anagrams of each other",
                   "https://leetcode.com/problems/group-anagrams/", "Strings"),
            
            # Dynamic Programming
            Problem("Climbing Stairs", Difficulty.EASY,
                   "Count ways to climb n stairs",
                   "https://leetcode.com/problems/climbing-stairs/", "Dynamic Programming"),
            Problem("House Robber", Difficulty.MEDIUM,
                   "Rob houses without alerting police",
                   "https://leetcode.com/problems/house-robber/", "Dynamic Programming"),
            Problem("Coin Change", Difficulty.MEDIUM,
                   "Find minimum coins to make amount",
                   "https://leetcode.com/problems/coin-change/", "Dynamic Programming"),
            Problem("Longest Increasing Subsequence", Difficulty.MEDIUM,
                   "Find length of longest increasing subsequence",
                   "https://leetcode.com/problems/longest-increasing-subsequence/", "Dynamic Programming"),
            
            # Trees
            Problem("Maximum Depth of Binary Tree", Difficulty.EASY,
                   "Find maximum depth of binary tree",
                   "https://leetcode.com/problems/maximum-depth-of-binary-tree/", "Trees"),
            Problem("Invert Binary Tree", Difficulty.EASY,
                   "Invert a binary tree",
                   "https://leetcode.com/problems/invert-binary-tree/", "Trees"),
            Problem("Binary Tree Level Order Traversal", Difficulty.MEDIUM,
                   "Return level order traversal of tree",
                   "https://leetcode.com/problems/binary-tree-level-order-traversal/", "Trees"),
            Problem("Validate Binary Search Tree", Difficulty.MEDIUM,
                   "Check if tree is valid BST",
                   "https://leetcode.com/problems/validate-binary-search-tree/", "Trees"),
            
            # Graphs
            Problem("Number of Islands", Difficulty.MEDIUM,
                   "Count number of islands in 2D grid",
                   "https://leetcode.com/problems/number-of-islands/", "Graphs"),
            Problem("Course Schedule", Difficulty.MEDIUM,
                   "Check if all courses can be taken",
                   "https://leetcode.com/problems/course-schedule/", "Graphs"),
            Problem("Clone Graph", Difficulty.MEDIUM,
                   "Clone an undirected graph",
                   "https://leetcode.com/problems/clone-graph/", "Graphs")
        ]
        
        # Add problems and simulate some progress
        for i, problem in enumerate(problems):
            tracker.add_problem(problem)
            
            # Simulate some completed problems
            if i < 5:
                problem.mark_completed()
                problem.add_time(30 + i * 10)
                problem.increment_attempts()
                problem.add_note("Solved on first try!")
            elif i < 8:
                problem.status = Status.IN_PROGRESS
                problem.add_time(45)
                problem.increment_attempts()
                problem.add_note("Need to review the approach")
            elif i < 10:
                problem.status = Status.NEEDS_REVIEW
                problem.add_time(60)
                problem.attempts = 2
                problem.add_note("Solved but need to optimize")
        
        # Add some study sessions
        sessions = [
            StudySession(120, "Focused on array problems", ["Two Sum", "3Sum"]),
            StudySession(90, "String algorithms practice", ["Valid Anagram", "Group Anagrams"]),
            StudySession(150, "Dynamic programming deep dive", ["Climbing Stairs", "House Robber"]),
            StudySession(60, "Quick tree problems review", ["Maximum Depth of Binary Tree"]),
            StudySession(180, "Graph algorithms study session", ["Number of Islands", "Course Schedule"])
        ]
        
        for session in sessions:
            tracker.add_session(session)
        
        return tracker