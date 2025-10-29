#!/usr/bin/env python3
"""
Launcher script for the Interview Preparation Tracker GUI
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os

def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        import tkinter as tk
        from tkinter import ttk
        import datetime
        import json
        import tabulate
        return True
    except ImportError as e:
        messagebox.showerror("Missing Dependencies", 
                           f"Required module not found: {e}\n\n"
                           "Please install the required dependencies with:\n"
                           "pip install -r requirements.txt")
        return False

def main():
    """Main launcher function."""
    if not check_dependencies():
        return
    
    try:
        # Import and run the GUI application
        try:
            from .interview_tracker import main as run_gui
        except ImportError:
            from interview_tracker import main as run_gui
        run_gui()
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Import Error", 
                           f"Could not import GUI application: {e}\n\n"
                           "Please ensure all files are in the same directory.")
    except Exception as e:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Application Error", 
                           f"An error occurred while starting the application:\n\n{e}")

if __name__ == '__main__':
    main()