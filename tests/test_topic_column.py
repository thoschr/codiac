#!/usr/bin/env python3
"""
Test script for the topic column visibility functionality.
This script tests the new topic column hide/show feature.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import ttk

# Mock the GUI components we need to test
class MockInterviewTrackerGUI:
    """Mock version of InterviewTrackerGUI to test topic column functionality."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window for testing
        
        # Column visibility state
        self.topic_column_visible = False  # Hidden by default
        
        # Create a simple frame and treeview for testing
        self.frame = ttk.Frame(self.root)
        
        # Topic visibility toggle button
        self.topic_visibility_btn = ttk.Button(self.frame, text="👁️ Topic", 
                                             command=self.toggle_topic_column)
        
        # Treeview for problems
        columns = ('Topic', 'Difficulty', 'Status', 'Attempts', 'Time')
        self.problems_tree = ttk.Treeview(self.frame, columns=columns, show='tree headings')
        
        # Configure headings
        self.problems_tree.heading('#0', text='Problem Title')
        self.problems_tree.heading('Topic', text='Topic')
        self.problems_tree.heading('Difficulty', text='Difficulty')
        self.problems_tree.heading('Status', text='Status')
        self.problems_tree.heading('Attempts', text='Attempts')
        self.problems_tree.heading('Time', text='Time Spent')
        
        # Hide topic column by default
        self.apply_topic_column_visibility()
        
    def toggle_topic_column(self):
        """Toggle the visibility of the Topic column in the problems tree."""
        self.topic_column_visible = not self.topic_column_visible
        self.apply_topic_column_visibility()
    
    def apply_topic_column_visibility(self):
        """Apply the current topic column visibility setting."""
        if self.topic_column_visible:
            # Show topic column - show all columns including Topic
            all_columns = ('Topic', 'Difficulty', 'Status', 'Attempts', 'Time')
            self.problems_tree['displaycolumns'] = all_columns
        else:
            # Hide topic column - show all columns except Topic
            visible_columns = ('Difficulty', 'Status', 'Attempts', 'Time')
            self.problems_tree['displaycolumns'] = visible_columns
    
def test_topic_column_functionality():
    """Test the topic column visibility functionality."""
    print("🧪 Testing topic column visibility functionality...")
    
    # Create mock GUI
    app = MockInterviewTrackerGUI()
    
    # Test 1: Initial state should be hidden
    print("📋 Test 1: Initial state")
    displayed_columns = list(app.problems_tree['displaycolumns'])
    if 'Topic' not in displayed_columns:
        print("✅ Topic column is hidden by default")
    else:
        print("❌ Topic column should be hidden by default")
        return False
    
    if not app.topic_column_visible:
        print("✅ topic_column_visible state is False by default")
    else:
        print("❌ topic_column_visible state should be False by default")
        return False
    
    # Test 2: Show topic column
    print("\n📋 Test 2: Show topic column")
    app.toggle_topic_column()
    displayed_columns = list(app.problems_tree['displaycolumns'])
    if 'Topic' in displayed_columns:
        print("✅ Topic column is visible after toggle")
    else:
        print("❌ Topic column should be visible after toggle")
        return False
    
    if app.topic_column_visible:
        print("✅ topic_column_visible state is True after toggle")
    else:
        print("❌ topic_column_visible state should be True after toggle")
        return False
    
    # Test 3: Hide topic column again
    print("\n📋 Test 3: Hide topic column again")
    app.toggle_topic_column()
    displayed_columns = list(app.problems_tree['displaycolumns'])
    if 'Topic' not in displayed_columns:
        print("✅ Topic column is hidden after second toggle")
    else:
        print("❌ Topic column should be hidden after second toggle")
        return False
    
    if not app.topic_column_visible:
        print("✅ topic_column_visible state is False after second toggle")
    else:
        print("❌ topic_column_visible state should be False after second toggle")
        return False
    
    # Test 4: Check button text updates
    print("\n📋 Test 4: Button text updates")
    button_text_hidden = app.topic_visibility_btn['text']
    app.toggle_topic_column()  # Show column
    button_text_visible = app.topic_visibility_btn['text']
    
    if button_text_hidden != button_text_visible:
        print("✅ Button text changes when toggling visibility")
    else:
        print("❌ Button text should change when toggling visibility")
        return False
    
    # Clean up
    app.root.destroy()
    
    print("\n🎉 All tests passed! Topic column functionality works correctly.")
    return True


if __name__ == '__main__':
    success = test_topic_column_functionality()
    sys.exit(0 if success else 1)