#!/usr/bin/env python3
"""
Interview Preparation Tracker - GUI Application

A graphical user interface for tracking coding interview preparation progress.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
from typing import Optional, List

try:
    # Try relative imports first (when used as a module)
    from .models import ProgressTracker, Topic, Problem, Difficulty, Status, StudySession
    from .data_manager import DataManager
except ImportError:
    # Fall back to absolute imports (when run as a script)
    from models import ProgressTracker, Topic, Problem, Difficulty, Status, StudySession
    from data_manager import DataManager


class InterviewTrackerGUI:
    """Main GUI application for the interview preparation tracker."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interview Preparation Tracker")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Data management
        self.data_manager = DataManager()
        self.tracker = self.load_or_create_tracker()
        
        # Auto-refresh timer
        self.auto_refresh_enabled = True
        self.last_data_hash = None
        
        # Configure styles
        self.setup_styles()
        
        # Create main interface
        self.create_widgets()
        
        # Load initial data
        self.refresh_all_views()
        
        # Start auto-refresh timer
        self.start_auto_refresh()
    
    def start_auto_refresh(self):
        """Start automatic refresh timer to update dashboard."""
        self.check_for_updates()
        # Schedule next check in 1 second for more responsive updates
        self.root.after(1000, self.start_auto_refresh)
    
    def check_for_updates(self):
        """Check if data has changed and refresh if needed."""
        if not self.auto_refresh_enabled:
            return
            
        try:
            # Create a simple hash of the current data
            current_hash = self.get_data_hash()
            
            if self.last_data_hash is None:
                self.last_data_hash = current_hash
                self.refresh_dashboard()  # Initial refresh
            elif current_hash != self.last_data_hash:
                # Data has changed, refresh dashboard
                self.refresh_dashboard()
                self.last_data_hash = current_hash
                # Update status to show auto-refresh worked
                current_time = datetime.now().strftime("%H:%M:%S")
                self.status_bar.config(text=f"Dashboard auto-updated at {current_time}")
        except Exception as e:
            # Show error in status bar for debugging
            self.status_bar.config(text=f"Auto-refresh error: {str(e)}")
    
    def get_data_hash(self):
        """Get a simple hash of current data for change detection."""
        # Create a more comprehensive representation of the data state
        problem_states = []
        for problem in self.tracker.problems.values():
            problem_states.append((
                problem.title,
                problem.status.value,
                problem.topic,
                int(problem.time_spent.total_seconds()),
                problem.attempts
            ))
        
        topic_states = [(name, len(topic.problems)) for name, topic in self.tracker.topics.items()]
        session_count = len(self.tracker.sessions)
        
        data_repr = (
            tuple(sorted(problem_states)),
            tuple(sorted(topic_states)),
            session_count
        )
        return hash(str(data_repr))
    
    def setup_styles(self):
        """Configure custom styles for the application."""
        style = ttk.Style()
        
        # Configure notebook style
        style.configure('TNotebook', tabposition='n')
        style.configure('TNotebook.Tab', padding=[12, 8])
        
        # Configure frame styles
        style.configure('Card.TFrame', relief='raised', borderwidth=2, padding=10)
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Warning.TLabel', foreground='orange')
        style.configure('Error.TLabel', foreground='red')
    
    def load_or_create_tracker(self) -> ProgressTracker:
        """Load existing tracker or create new one."""
        tracker = self.data_manager.load()
        if tracker is None:
            # Create with sample data if no existing data
            response = messagebox.askyesno(
                "Welcome to Interview Tracker",
                "No existing data found. Would you like to start with sample data?"
            )
            if response:
                tracker = self.data_manager.create_sample_data()
            else:
                tracker = ProgressTracker()
            # Save the new tracker data
            self.data_manager.save(tracker)
        return tracker
    
    def save_data(self):
        """Save current tracker data and trigger dashboard refresh."""
        if not self.data_manager.save(self.tracker):
            messagebox.showerror("Error", "Failed to save data!")
        else:
            # Force dashboard refresh after saving and update hash
            self.refresh_dashboard_immediate()
            # Also refresh the current tab if it's not dashboard
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if "Problems" in current_tab:
                self.refresh_problems_view()
            elif "Topics" in current_tab:
                self.refresh_topics_view()
            elif "Sessions" in current_tab:
                self.refresh_sessions_view()
    
    def create_widgets(self):
        """Create the main application widgets."""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_problems_tab()
        self.create_topics_tab()
        self.create_sessions_tab()
        self.create_rotation_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief='sunken')
        self.status_bar.pack(side='bottom', fill='x')
    
    def create_dashboard_tab(self):
        """Create the dashboard tab with overview statistics."""
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")
        
        # Main container with scrollbar
        canvas = tk.Canvas(self.dashboard_frame)
        scrollbar = ttk.Scrollbar(self.dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Interview Preparation Dashboard", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Refresh button for dashboard
        refresh_frame = ttk.Frame(scrollable_frame)
        refresh_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        refresh_btn = ttk.Button(refresh_frame, text="🔄 Refresh Dashboard", 
                               command=self.refresh_dashboard_immediate)
        refresh_btn.pack(side='right')
        
        # Auto-refresh status
        auto_refresh_label = ttk.Label(refresh_frame, text="🔄 Auto-refresh: ON", 
                                     font=('Arial', 9), foreground='green')
        auto_refresh_label.pack(side='left')
        
        # Last update time
        self.last_update_label = ttk.Label(refresh_frame, text="", 
                                         font=('Arial', 9), foreground='blue')
        self.last_update_label.pack(side='left', padx=(10, 0))
        
        # Stats cards container
        stats_container = ttk.Frame(scrollable_frame)
        stats_container.pack(fill='x', padx=20)
        
        # Overall stats card
        self.overall_stats_frame = ttk.LabelFrame(stats_container, text="Overall Progress", 
                                                 style='Card.TFrame')
        self.overall_stats_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Topics progress card
        self.topics_stats_frame = ttk.LabelFrame(stats_container, text="Progress by Topic", 
                                               style='Card.TFrame')
        self.topics_stats_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Recent activity section
        recent_frame = ttk.LabelFrame(scrollable_frame, text="Recent Activity")
        recent_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Recent sessions list
        self.recent_sessions_tree = ttk.Treeview(recent_frame, columns=('Duration', 'Problems', 'Notes'), 
                                               show='tree headings', height=6)
        self.recent_sessions_tree.heading('#0', text='Date')
        self.recent_sessions_tree.heading('Duration', text='Duration')
        self.recent_sessions_tree.heading('Problems', text='Problems Worked')
        self.recent_sessions_tree.heading('Notes', text='Notes')
        
        self.recent_sessions_tree.column('#0', width=150)
        self.recent_sessions_tree.column('Duration', width=100)
        self.recent_sessions_tree.column('Problems', width=200)
        self.recent_sessions_tree.column('Notes', width=300)
        
        self.recent_sessions_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bind double-click to view session details
        self.recent_sessions_tree.bind("<Double-1>", self.view_session_details)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_problems_tab(self):
        """Create the problems management tab."""
        self.problems_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.problems_frame, text="📝 Problems")
        
        # Top controls frame
        controls_frame = ttk.Frame(self.problems_frame)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Add problem button
        add_problem_btn = ttk.Button(controls_frame, text="➕ Add Problem", 
                                   command=self.add_problem_dialog)
        add_problem_btn.pack(side='left', padx=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame, text="🔄 Refresh", 
                               command=self.refresh_problems_view)
        refresh_btn.pack(side='left', padx=(0, 10))
        
        # Delete button
        delete_btn = ttk.Button(controls_frame, text="🗑️ Delete Selected", 
                              command=self.delete_selected_problem)
        delete_btn.pack(side='left', padx=(0, 10))
        
        # Recalculate attempts button
        recalc_btn = ttk.Button(controls_frame, text="🔢 Recalculate Attempts", 
                              command=self.recalculate_attempts)
        recalc_btn.pack(side='left', padx=(0, 10))
        
        # Recalculate time button
        recalc_time_btn = ttk.Button(controls_frame, text="⏱️ Recalculate Time", 
                                   command=self.recalculate_time_from_sessions)
        recalc_time_btn.pack(side='left', padx=(0, 10))
        
        # Filters frame
        filters_frame = ttk.LabelFrame(controls_frame, text="Filters")
        filters_frame.pack(side='right', padx=(10, 0))
        
        # Topic filter
        ttk.Label(filters_frame, text="Topic:").grid(row=0, column=0, padx=5, pady=5)
        self.topic_filter = ttk.Combobox(filters_frame, width=15)
        self.topic_filter.grid(row=0, column=1, padx=5, pady=5)
        self.topic_filter.bind('<<ComboboxSelected>>', self.filter_problems)
        
        # Status filter
        ttk.Label(filters_frame, text="Status:").grid(row=0, column=2, padx=5, pady=5)
        self.status_filter = ttk.Combobox(filters_frame, width=15)
        self.status_filter['values'] = ['All', 'Not Started', 'In Progress', 'Completed', 'Needs Review']
        self.status_filter.set('All')
        self.status_filter.grid(row=0, column=3, padx=5, pady=5)
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_problems)
        
        # Difficulty filter
        ttk.Label(filters_frame, text="Difficulty:").grid(row=1, column=0, padx=5, pady=5)
        self.difficulty_filter = ttk.Combobox(filters_frame, width=15)
        self.difficulty_filter['values'] = ['All', 'Easy', 'Medium', 'Hard']
        self.difficulty_filter.set('All')
        self.difficulty_filter.grid(row=1, column=1, padx=5, pady=5)
        self.difficulty_filter.bind('<<ComboboxSelected>>', self.filter_problems)
        
        # Clear filters button
        clear_filters_btn = ttk.Button(filters_frame, text="Clear", 
                                     command=self.clear_filters)
        clear_filters_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Problems list
        list_frame = ttk.Frame(self.problems_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Treeview for problems
        columns = ('Topic', 'Difficulty', 'Status', 'Attempts', 'Time')
        self.problems_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        # Configure headings
        self.problems_tree.heading('#0', text='Problem Title')
        self.problems_tree.heading('Topic', text='Topic')
        self.problems_tree.heading('Difficulty', text='Difficulty')
        self.problems_tree.heading('Status', text='Status')
        self.problems_tree.heading('Attempts', text='Attempts')
        self.problems_tree.heading('Time', text='Time Spent')
        
        # Configure column widths
        self.problems_tree.column('#0', width=300)
        self.problems_tree.column('Topic', width=150)
        self.problems_tree.column('Difficulty', width=100)
        self.problems_tree.column('Status', width=120)
        self.problems_tree.column('Attempts', width=80)
        self.problems_tree.column('Time', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.problems_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.problems_tree.xview)
        self.problems_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.problems_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu for problems
        self.problems_context_menu = tk.Menu(self.root, tearoff=0)
        self.problems_context_menu.add_command(label="View Details", command=self.view_problem_details)
        self.problems_context_menu.add_command(label="Edit Problem", command=self.edit_problem_dialog)
        self.problems_context_menu.add_separator()
        
        # Status change submenu
        status_submenu = tk.Menu(self.problems_context_menu, tearoff=0)
        status_submenu.add_command(label="Not Started", command=lambda: self.change_problem_status(Status.NOT_STARTED))
        status_submenu.add_command(label="In Progress", command=lambda: self.change_problem_status(Status.IN_PROGRESS))
        status_submenu.add_command(label="Completed", command=lambda: self.change_problem_status(Status.COMPLETED))
        status_submenu.add_command(label="Needs Review", command=lambda: self.change_problem_status(Status.NEEDS_REVIEW))
        self.problems_context_menu.add_cascade(label="Change Status", menu=status_submenu)
        
        self.problems_context_menu.add_separator()
        self.problems_context_menu.add_command(label="Add Time", command=self.add_time_dialog)
        self.problems_context_menu.add_command(label="Add Note", command=self.add_note_dialog)
        self.problems_context_menu.add_separator()
        self.problems_context_menu.add_command(label="Delete Problem", command=self.delete_selected_problem)
        
        self.problems_tree.bind("<Button-3>", self.show_problems_context_menu)
        self.problems_tree.bind("<Double-1>", self.view_problem_details)
    
    def create_topics_tab(self):
        """Create the topics management tab."""
        self.topics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.topics_frame, text="📚 Topics")
        
        # Top controls
        controls_frame = ttk.Frame(self.topics_frame)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        add_topic_btn = ttk.Button(controls_frame, text="➕ Add Topic", 
                                 command=self.add_topic_dialog)
        add_topic_btn.pack(side='left', padx=(0, 10))
        
        refresh_topics_btn = ttk.Button(controls_frame, text="🔄 Refresh", 
                                      command=self.refresh_topics_view)
        refresh_topics_btn.pack(side='left')
        
        # Topics list
        list_frame = ttk.Frame(self.topics_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        columns = ('Description', 'Problems', 'Completed', 'Progress')
        self.topics_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        self.topics_tree.heading('#0', text='Topic Name')
        self.topics_tree.heading('Description', text='Description')
        self.topics_tree.heading('Problems', text='Total Problems')
        self.topics_tree.heading('Completed', text='Completed')
        self.topics_tree.heading('Progress', text='Progress %')
        
        self.topics_tree.column('#0', width=200)
        self.topics_tree.column('Description', width=300)
        self.topics_tree.column('Problems', width=120)
        self.topics_tree.column('Completed', width=120)
        self.topics_tree.column('Progress', width=120)
        
        # Scrollbars for topics
        topics_v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.topics_tree.yview)
        topics_h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.topics_tree.xview)
        self.topics_tree.configure(yscrollcommand=topics_v_scrollbar.set, xscrollcommand=topics_h_scrollbar.set)
        
        self.topics_tree.grid(row=0, column=0, sticky='nsew')
        topics_v_scrollbar.grid(row=0, column=1, sticky='ns')
        topics_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
    
    def create_sessions_tab(self):
        """Create the study sessions tab."""
        self.sessions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sessions_frame, text="⏱️ Sessions")
        
        # Top controls
        controls_frame = ttk.Frame(self.sessions_frame)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        add_session_btn = ttk.Button(controls_frame, text="➕ Add Session", 
                                   command=self.add_session_dialog)
        add_session_btn.pack(side='left', padx=(0, 10))
        
        refresh_sessions_btn = ttk.Button(controls_frame, text="🔄 Refresh", 
                                        command=self.refresh_sessions_view)
        refresh_sessions_btn.pack(side='left', padx=(0, 10))
        
        delete_session_btn = ttk.Button(controls_frame, text="🗑️ Delete Selected", 
                                      command=self.delete_selected_session)
        delete_session_btn.pack(side='left')
        
        # Sessions list
        list_frame = ttk.Frame(self.sessions_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        columns = ('Duration', 'Problems', 'Notes')
        self.sessions_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        self.sessions_tree.heading('#0', text='Date & Time')
        self.sessions_tree.heading('Duration', text='Duration')
        self.sessions_tree.heading('Problems', text='Problems Worked')
        self.sessions_tree.heading('Notes', text='Session Notes')
        
        self.sessions_tree.column('#0', width=180)
        self.sessions_tree.column('Duration', width=100)
        self.sessions_tree.column('Problems', width=250)
        self.sessions_tree.column('Notes', width=350)
        
        # Scrollbars for sessions
        sessions_v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.sessions_tree.yview)
        sessions_h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.sessions_tree.xview)
        self.sessions_tree.configure(yscrollcommand=sessions_v_scrollbar.set, xscrollcommand=sessions_h_scrollbar.set)
        
        self.sessions_tree.grid(row=0, column=0, sticky='nsew')
        sessions_v_scrollbar.grid(row=0, column=1, sticky='ns')
        sessions_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu for sessions
        self.sessions_context_menu = tk.Menu(self.root, tearoff=0)
        self.sessions_context_menu.add_command(label="View Details", command=self.view_session_details)
        self.sessions_context_menu.add_separator()
        self.sessions_context_menu.add_command(label="Delete Session", command=self.delete_selected_session)
        
        self.sessions_tree.bind("<Button-3>", self.show_sessions_context_menu)
        self.sessions_tree.bind("<Double-1>", self.view_session_details)
    
    def create_rotation_tab(self):
        """Create the problem rotation tab for reviewing completed problems."""
        self.rotation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rotation_frame, text="🔄 Rotation")
        
        # Main container with padding
        main_container = ttk.Frame(self.rotation_frame)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title and stats section
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="Problem Rotation Review", font=('Arial', 16, 'bold'))
        title_label.pack(anchor='w')
        
        self.rotation_stats_label = ttk.Label(title_frame, text="", font=('Arial', 10))
        self.rotation_stats_label.pack(anchor='w', pady=(5, 0))
        
        # Control buttons
        controls_frame = ttk.Frame(main_container)
        controls_frame.pack(fill='x', pady=(0, 20))
        
        self.next_problem_btn = ttk.Button(controls_frame, text="🎲 Get Next Problem", 
                                         command=self.get_next_rotation_problem)
        self.next_problem_btn.pack(side='left', padx=(0, 10))
        
        self.mark_rotation_done_btn = ttk.Button(controls_frame, text="✅ Mark as Done", 
                                               command=self.mark_rotation_completed,
                                               state='disabled')
        self.mark_rotation_done_btn.pack(side='left')
        
        # Problem display area
        self.rotation_problem_frame = ttk.LabelFrame(main_container, text="Current Problem", padding="15")
        self.rotation_problem_frame.pack(fill='both', expand=True)
        
        # Initially show "no problem selected" message
        self.rotation_content_frame = ttk.Frame(self.rotation_problem_frame)
        self.rotation_content_frame.pack(fill='both', expand=True)
        
        self.no_problem_label = ttk.Label(self.rotation_content_frame, 
                                        text="Click 'Get Next Problem' to start reviewing completed problems.",
                                        font=('Arial', 12),
                                        foreground='gray')
        self.no_problem_label.pack(expand=True)
        
        # Current rotation problem
        self.current_rotation_problem: Optional[Problem] = None

    def refresh_all_views(self):
        """Refresh all tabs with current data."""
        self.refresh_dashboard()
        self.refresh_problems_view()
        self.refresh_topics_view()
        self.refresh_sessions_view()
        self.refresh_rotation_view()
        self.update_filters()
    
    def refresh_dashboard_immediate(self):
        """Immediately refresh dashboard and update data hash."""
        self.refresh_dashboard()
        self.last_data_hash = self.get_data_hash()
    
    def on_tab_changed(self, event):
        """Handle tab change events to refresh current tab."""
        selected_tab = event.widget.tab('current')['text']
        
        # Refresh the appropriate view based on selected tab
        if "Dashboard" in selected_tab:
            self.refresh_dashboard()
        elif "Problems" in selected_tab:
            self.refresh_problems_view()
            self.update_filters()
        elif "Topics" in selected_tab:
            self.refresh_topics_view()
        elif "Sessions" in selected_tab:
            self.refresh_sessions_view()
        elif "Rotation" in selected_tab:
            self.refresh_rotation_view()
    
    def update_filters(self):
        """Update filter dropdown values."""
        # Update topic filter
        topics = ['All'] + list(self.tracker.topics.keys())
        self.topic_filter['values'] = topics
        if not self.topic_filter.get() or self.topic_filter.get() not in topics:
            self.topic_filter.set('All')
    
    def refresh_dashboard(self):
        """Refresh the dashboard statistics."""
        # Ensure topic-problem connections are correct
        self.tracker.rebuild_topic_connections()
        
        # Update last refresh time
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        if hasattr(self, 'last_update_label'):
            self.last_update_label.config(text=f"Updated: {current_time}")
        
        # Clear existing widgets
        for widget in self.overall_stats_frame.winfo_children():
            widget.destroy()
        for widget in self.topics_stats_frame.winfo_children():
            widget.destroy()
        
        # Overall statistics
        overall_stats = self.tracker.get_overall_stats()
        
        ttk.Label(self.overall_stats_frame, text=f"Total Problems: {overall_stats['total_problems']}", 
                 font=('Arial', 12)).pack(anchor='w', pady=2)
        ttk.Label(self.overall_stats_frame, text=f"Completed: {overall_stats['completed_problems']}", 
                 font=('Arial', 12)).pack(anchor='w', pady=2)
        ttk.Label(self.overall_stats_frame, text=f"Progress: {overall_stats['completion_rate']:.1f}%", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=2)
        ttk.Label(self.overall_stats_frame, text=f"Study Time: {overall_stats['total_study_time_hours']:.1f} hours", 
                 font=('Arial', 12)).pack(anchor='w', pady=2)
        ttk.Label(self.overall_stats_frame, text=f"Sessions: {overall_stats['total_sessions']}", 
                 font=('Arial', 12)).pack(anchor='w', pady=2)
        
        # Progress bar
        progress_frame = ttk.Frame(self.overall_stats_frame)
        progress_frame.pack(fill='x', pady=10)
        
        progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        progress_bar['value'] = overall_stats['completion_rate']
        progress_bar.pack()
        
        # Topics statistics
        topic_stats = self.tracker.get_topic_stats()
        
        if topic_stats:
            # Debug info
            ttk.Label(self.topics_stats_frame, text="Topic Progress (Live):", 
                     font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
            
            # Debug: show total problems in tracker vs topics
            total_problems_in_tracker = len(self.tracker.problems)
            total_problems_in_topics = sum(len(topic.problems) for topic in self.tracker.topics.values())
            
            ttk.Label(self.topics_stats_frame, 
                     text=f"Debug: {total_problems_in_tracker} total problems, {total_problems_in_topics} in topics", 
                     font=('Arial', 8), foreground='gray').pack(anchor='w', pady=(0, 5))
            
            for i, (topic, stats) in enumerate(topic_stats.items()):
                topic_frame = ttk.Frame(self.topics_stats_frame)
                topic_frame.pack(fill='x', pady=2)
                
                # Show more detailed info for debugging
                completed = stats['completed_problems']
                total = stats['total_problems']
                rate = stats['completion_rate']
                
                ttk.Label(topic_frame, text=f"{topic}:", font=('Arial', 10, 'bold')).pack(side='left')
                ttk.Label(topic_frame, text=f"{completed}/{total} ({rate:.1f}%)", 
                         font=('Arial', 10)).pack(side='right')
        else:
            ttk.Label(self.topics_stats_frame, text="No topics yet").pack()
        
        # Refresh recent sessions
        self.recent_sessions_tree.delete(*self.recent_sessions_tree.get_children())
        
        recent_sessions = sorted(self.tracker.sessions, key=lambda s: s.date, reverse=True)[:5]
        for i, session in enumerate(recent_sessions):
            duration = f"{int(session.duration.total_seconds() / 60)}m"
            problems = ", ".join(session.problems_worked[:2]) + ("..." if len(session.problems_worked) > 2 else "")
            notes = session.notes[:50] + "..." if len(session.notes) > 50 else session.notes
            
            self.recent_sessions_tree.insert('', 'end', 
                                           text=session.date.strftime('%Y-%m-%d %H:%M'),
                                           values=(duration, problems, notes),
                                           tags=(str(i),))  # Store session index
    
    def refresh_problems_view(self):
        """Refresh the problems list."""
        # Clear existing items
        self.problems_tree.delete(*self.problems_tree.get_children())
        
        # Get filtered problems
        problems = self.get_filtered_problems()
        
        for problem in problems:
            time_spent = f"{int(problem.time_spent.total_seconds() / 60)}m"
            
            # Add color coding based on status
            tags = []
            if problem.status == Status.COMPLETED:
                tags.append('completed')
            elif problem.status == Status.IN_PROGRESS:
                tags.append('in_progress')
            elif problem.status == Status.NEEDS_REVIEW:
                tags.append('review')
            
            self.problems_tree.insert('', 'end', 
                                    text=problem.title,
                                    values=(problem.topic, problem.difficulty.value, 
                                           problem.status.value, problem.attempts, time_spent),
                                    tags=tags)
        
        # Configure tags for color coding
        self.problems_tree.tag_configure('completed', background='#d4edda')
        self.problems_tree.tag_configure('in_progress', background='#fff3cd')
        self.problems_tree.tag_configure('review', background='#f8d7da')
    
    def get_filtered_problems(self) -> List[Problem]:
        """Get problems filtered by current filter settings."""
        problems = list(self.tracker.problems.values())
        
        # Filter by topic
        topic_filter = self.topic_filter.get()
        if topic_filter and topic_filter != 'All':
            problems = [p for p in problems if p.topic == topic_filter]
        
        # Filter by status
        status_filter = self.status_filter.get()
        if status_filter and status_filter != 'All':
            status_map = {
                'Not Started': Status.NOT_STARTED,
                'In Progress': Status.IN_PROGRESS,
                'Completed': Status.COMPLETED,
                'Needs Review': Status.NEEDS_REVIEW
            }
            if status_filter in status_map:
                problems = [p for p in problems if p.status == status_map[status_filter]]
        
        # Filter by difficulty
        difficulty_filter = self.difficulty_filter.get()
        if difficulty_filter and difficulty_filter != 'All':
            difficulty_map = {
                'Easy': Difficulty.EASY,
                'Medium': Difficulty.MEDIUM,
                'Hard': Difficulty.HARD
            }
            if difficulty_filter in difficulty_map:
                problems = [p for p in problems if p.difficulty == difficulty_map[difficulty_filter]]
        
        return problems
    
    def filter_problems(self, event=None):
        """Apply filters to problems list."""
        self.refresh_problems_view()
    
    def clear_filters(self):
        """Clear all filters."""
        self.topic_filter.set('All')
        self.status_filter.set('All')
        self.difficulty_filter.set('All')
        self.refresh_problems_view()
    
    def refresh_topics_view(self):
        """Refresh the topics list."""
        self.topics_tree.delete(*self.topics_tree.get_children())
        
        for topic in self.tracker.topics.values():
            completion_rate = topic.get_completion_rate()
            completed_count = sum(1 for p in topic.problems if p.status == Status.COMPLETED)
            
            self.topics_tree.insert('', 'end',
                                  text=topic.name,
                                  values=(topic.description, len(topic.problems), 
                                         completed_count, f"{completion_rate:.1f}%"))
    
    def refresh_sessions_view(self):
        """Refresh the sessions list."""
        self.sessions_tree.delete(*self.sessions_tree.get_children())
        
        sessions = sorted(self.tracker.sessions, key=lambda s: s.date, reverse=True)
        for i, session in enumerate(sessions):
            duration = f"{int(session.duration.total_seconds() / 60)}m"
            problems = ", ".join(session.problems_worked) if session.problems_worked else "None"
            
            # Store session index as a tag for deletion
            self.sessions_tree.insert('', 'end',
                                    text=session.date.strftime('%Y-%m-%d %H:%M'),
                                    values=(duration, problems, session.notes),
                                    tags=(str(i),))  # Store session index
    
    def show_sessions_context_menu(self, event):
        """Show context menu for sessions."""
        item = self.sessions_tree.identify_row(event.y)
        if item:
            self.sessions_tree.selection_set(item)
            self.sessions_context_menu.post(event.x_root, event.y_root)
    
    def view_session_details(self, event=None):
        """Show detailed view of selected session."""
        selection = self.sessions_tree.selection()
        if not selection:
            return
        
        item = self.sessions_tree.item(selection[0])
        session_tags = item['tags']
        
        if session_tags:
            try:
                session_index = int(session_tags[0])
                sessions = sorted(self.tracker.sessions, key=lambda s: s.date, reverse=True)
                if 0 <= session_index < len(sessions):
                    session = sessions[session_index]
                    SessionDetailsDialog(self.root, session)
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Could not find session details.")
    
    def delete_selected_session(self):
        """Delete the selected session."""
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session to delete.")
            return
        
        item = self.sessions_tree.item(selection[0])
        session_date = item['text']
        session_tags = item['tags']
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete the study session from {session_date}?\n\nThis action cannot be undone."
        )
        
        if result:
            try:
                if session_tags:
                    session_index = int(session_tags[0])
                    sessions = sorted(self.tracker.sessions, key=lambda s: s.date, reverse=True)
                    if 0 <= session_index < len(sessions):
                        session_to_delete = sessions[session_index]
                        self.tracker.remove_session(session_to_delete)
                        self.save_data()
                        self.refresh_all_views()
                        self.status_bar.config(text=f"Deleted session from {session_date} - Time and attempts updated")
                    else:
                        messagebox.showerror("Error", "Session not found.")
                else:
                    messagebox.showerror("Error", "Could not identify session to delete.")
            except (ValueError, IndexError) as e:
                messagebox.showerror("Error", f"Error deleting session: {e}")
    
    # Rotation methods
    def refresh_rotation_view(self):
        """Refresh the rotation tab display."""
        stats = self.tracker.get_rotation_stats()
        stats_text = f"Completed Problems: {stats['total_completed']} | Reviewed: {stats['total_reviewed']} | Pending: {stats['pending_review']}"
        self.rotation_stats_label.config(text=stats_text)
        
        # Enable/disable buttons based on available problems
        has_completed = stats['total_completed'] > 0
        self.next_problem_btn.config(state='normal' if has_completed else 'disabled')
        
        if not has_completed:
            self.show_no_problems_message()
    
    def get_next_rotation_problem(self):
        """Get and display the next problem for rotation review."""
        problem = self.tracker.get_next_rotation_problem()
        
        if problem:
            self.current_rotation_problem = problem
            self.display_rotation_problem(problem)
            self.mark_rotation_done_btn.config(state='normal')
        else:
            self.show_no_problems_message()
            self.mark_rotation_done_btn.config(state='disabled')
    
    def mark_rotation_completed(self):
        """Mark the current rotation problem as completed."""
        if not self.current_rotation_problem:
            return
        
        self.current_rotation_problem.mark_rotation_completed()
        self.save_data()
        
        # Clear current problem and update display
        self.current_rotation_problem = None
        self.mark_rotation_done_btn.config(state='disabled')
        self.show_completion_message()
        
        # Refresh stats
        self.refresh_rotation_view()
        self.status_bar.config(text="Problem marked as reviewed in rotation")
    
    def display_rotation_problem(self, problem: Problem):
        """Display the rotation problem details."""
        # Clear existing content
        for widget in self.rotation_content_frame.winfo_children():
            widget.destroy()
        
        # Create scrollable frame for problem content
        canvas = tk.Canvas(self.rotation_content_frame)
        scrollbar = ttk.Scrollbar(self.rotation_content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Problem details
        title_label = ttk.Label(scrollable_frame, text=problem.title, font=('Arial', 18, 'bold'))
        title_label.pack(anchor='w', pady=(0, 15))
        
        # Info grid
        info_frame = ttk.Frame(scrollable_frame)
        info_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(info_frame, text="Topic:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Label(info_frame, text=problem.topic, font=('Arial', 11)).grid(row=0, column=1, sticky='w')
        
        ttk.Label(info_frame, text="Difficulty:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky='w', padx=(0, 10))
        ttk.Label(info_frame, text=problem.difficulty.value, font=('Arial', 11)).grid(row=1, column=1, sticky='w')
        
        ttk.Label(info_frame, text="Attempts:", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky='w', padx=(0, 10))
        ttk.Label(info_frame, text=str(problem.attempts), font=('Arial', 11)).grid(row=2, column=1, sticky='w')
        
        time_spent = int(problem.time_spent.total_seconds() / 60)
        ttk.Label(info_frame, text="Time Spent:", font=('Arial', 11, 'bold')).grid(row=3, column=0, sticky='w', padx=(0, 10))
        ttk.Label(info_frame, text=f"{time_spent} minutes", font=('Arial', 11)).grid(row=3, column=1, sticky='w')
        
        if problem.completed_at:
            completed_date = problem.completed_at.strftime('%Y-%m-%d')
            ttk.Label(info_frame, text="Completed:", font=('Arial', 11, 'bold')).grid(row=4, column=0, sticky='w', padx=(0, 10))
            ttk.Label(info_frame, text=completed_date, font=('Arial', 11)).grid(row=4, column=1, sticky='w')
        
        # From/URL
        if problem.url:
            ttk.Label(scrollable_frame, text="From:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            url_label = ttk.Label(scrollable_frame, text=problem.url, foreground='blue', cursor='hand2')
            url_label.pack(anchor='w')
        
        # Description
        if problem.description:
            ttk.Label(scrollable_frame, text="Description:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(15, 5))
            desc_text = tk.Text(scrollable_frame, height=8, wrap='word', state='disabled', font=('Arial', 10))
            desc_text.config(state='normal')
            desc_text.insert('1.0', problem.description)
            desc_text.config(state='disabled')
            desc_text.pack(fill='x', pady=(0, 10))
        
        # Notes
        if problem.notes:
            ttk.Label(scrollable_frame, text="Notes:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            notes_text = tk.Text(scrollable_frame, height=6, wrap='word', state='disabled', font=('Arial', 10))
            notes_text.config(state='normal')
            for note in problem.notes:
                notes_text.insert('end', f"• {note}\n")
            notes_text.config(state='disabled')
            notes_text.pack(fill='x')
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def show_no_problems_message(self):
        """Show message when no problems are available for rotation."""
        # Clear existing content
        for widget in self.rotation_content_frame.winfo_children():
            widget.destroy()
        
        message = "No completed problems available for rotation review.\nComplete some problems first!"
        label = ttk.Label(self.rotation_content_frame, 
                         text=message,
                         font=('Arial', 12),
                         foreground='gray',
                         justify='center')
        label.pack(expand=True)
    
    def show_completion_message(self):
        """Show completion message after marking a problem as done."""
        # Clear existing content
        for widget in self.rotation_content_frame.winfo_children():
            widget.destroy()
        
        message = "✅ Problem marked as reviewed!\n\nClick 'Get Next Problem' to continue rotation review."
        label = ttk.Label(self.rotation_content_frame, 
                         text=message,
                         font=('Arial', 12),
                         foreground='green',
                         justify='center')
        label.pack(expand=True)

    # Dialog functions
    def add_problem_dialog(self):
        """Show dialog to add a new problem."""
        dialog = ProblemDialog(self.root, self.tracker.topics.keys())
        if dialog.result:
            # Handle both old and new formats
            if len(dialog.result) == 6:
                title, difficulty, topic, description, url, status = dialog.result
            else:
                title, difficulty, topic, description, url = dialog.result
                status = None
            
            if title in self.tracker.problems:
                messagebox.showerror("Error", f"Problem '{title}' already exists!")
                return
            
            if topic not in self.tracker.topics:
                messagebox.showerror("Error", f"Topic '{topic}' doesn't exist!")
                return
            
            difficulty_enum = {
                'Easy': Difficulty.EASY,
                'Medium': Difficulty.MEDIUM,
                'Hard': Difficulty.HARD
            }[difficulty]
            
            problem = Problem(title, difficulty_enum, description, url, topic)
            
            # Apply status if provided from dialog
            if status:
                status_enum = {
                    'Not Started': Status.NOT_STARTED,
                    'In Progress': Status.IN_PROGRESS,
                    'Completed': Status.COMPLETED,
                    'Needs Review': Status.NEEDS_REVIEW
                }.get(status, Status.NOT_STARTED)
                problem.status = status_enum
                if status_enum == Status.COMPLETED:
                    problem.completed_at = datetime.now()
            
            self.tracker.add_problem(problem)
            self.save_data()
            self.refresh_all_views()
            self.status_bar.config(text=f"Added problem: {title} - Dashboard updated automatically")
    
    def edit_problem_dialog(self):
        """Show dialog to edit selected problem."""
        selection = self.problems_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a problem to edit.")
            return
        
        item = self.problems_tree.item(selection[0])
        problem_title = item['text']
        problem = self.tracker.problems.get(problem_title)
        
        if not problem:
            messagebox.showerror("Error", "Problem not found!")
            return
        
        dialog = ProblemDialog(self.root, self.tracker.topics.keys(), problem)
        if dialog.result:
            title, difficulty, topic, description, url, status = dialog.result
            
            # Update problem properties
            if title != problem.title:
                # Handle title change
                del self.tracker.problems[problem.title]
                problem.title = title
                self.tracker.problems[title] = problem
            
            problem.difficulty = {
                'Easy': Difficulty.EASY,
                'Medium': Difficulty.MEDIUM,
                'Hard': Difficulty.HARD
            }[difficulty]
            problem.topic = topic
            problem.description = description
            problem.url = url
            
            # Handle status change if provided
            if status:
                old_status = problem.status.value
                new_status = {
                    'Not Started': Status.NOT_STARTED,
                    'In Progress': Status.IN_PROGRESS,
                    'Completed': Status.COMPLETED,
                    'Needs Review': Status.NEEDS_REVIEW
                }[status]
                
                problem.status = new_status
                
                # Handle completion date
                if new_status == Status.COMPLETED and old_status != 'Completed':
                    problem.mark_completed()
                elif new_status != Status.COMPLETED and old_status == 'Completed':
                    problem.completed_at = None
            
            self.save_data()
            self.refresh_all_views()
            # Force update of data hash
            self.last_data_hash = self.get_data_hash()
            self.status_bar.config(text=f"Updated problem: {title} - Dashboard refreshed")
    
    def add_topic_dialog(self):
        """Show dialog to add a new topic."""
        dialog = TopicDialog(self.root)
        if dialog.result:
            name, description = dialog.result
            
            if name in self.tracker.topics:
                messagebox.showerror("Error", f"Topic '{name}' already exists!")
                return
            
            topic = Topic(name, description)
            self.tracker.add_topic(topic)
            self.save_data()
            self.refresh_all_views()
            self.status_bar.config(text=f"Added topic: {name} - Dashboard updated")
    
    def add_session_dialog(self):
        """Show dialog to add a study session."""
        dialog = SessionDialog(self.root, self.tracker.problems.keys())
        if dialog.result:
            duration, notes, problems_worked = dialog.result
            
            session = StudySession(duration, notes, problems_worked)
            self.tracker.add_session(session)
            self.save_data()
            self.refresh_all_views()
            self.status_bar.config(text=f"Added {duration}-minute study session - Dashboard updated")
    
    def show_problems_context_menu(self, event):
        """Show context menu for problems."""
        item = self.problems_tree.identify_row(event.y)
        if item:
            self.problems_tree.selection_set(item)
            self.problems_context_menu.post(event.x_root, event.y_root)
    
    def view_problem_details(self, event=None):
        """Show detailed view of selected problem."""
        selection = self.problems_tree.selection()
        if not selection:
            return
        
        item = self.problems_tree.item(selection[0])
        problem_title = item['text']
        problem = self.tracker.problems.get(problem_title)
        
        if problem:
            ProblemDetailsDialog(self.root, problem)
    
    def change_problem_status(self, new_status: Status):
        """Change the status of selected problem."""
        selection = self.problems_tree.selection()
        if not selection:
            return
        
        item = self.problems_tree.item(selection[0])
        problem_title = item['text']
        problem = self.tracker.problems.get(problem_title)
        
        if problem:
            old_status = problem.status.value
            problem.status = new_status
            
            # If marking as completed, set completion date
            if new_status == Status.COMPLETED:
                problem.mark_completed()
            else:
                # If changing from completed to something else, clear completion date
                if problem.completed_at and new_status != Status.COMPLETED:
                    problem.completed_at = None
            
            self.save_data()
            # Force immediate refresh of all views
            self.refresh_all_views()
            # Also force dashboard refresh with updated hash
            self.last_data_hash = self.get_data_hash()
            self.status_bar.config(text=f"Changed '{problem_title}' from {old_status} to {new_status.value}")
    
    def mark_problem_completed(self):
        """Mark selected problem as completed (legacy method for compatibility)."""
        self.change_problem_status(Status.COMPLETED)
    
    def add_time_dialog(self):
        """Show dialog to add time to selected problem."""
        selection = self.problems_tree.selection()
        if not selection:
            return
        
        item = self.problems_tree.item(selection[0])
        problem_title = item['text']
        problem = self.tracker.problems.get(problem_title)
        
        if problem:
            time_str = simpledialog.askstring("Add Time", "Enter time spent (in minutes):")
            if time_str:
                try:
                    minutes = int(time_str)
                    problem.add_time(minutes)
                    self.save_data()
                    self.refresh_all_views()
                    self.status_bar.config(text=f"Added {minutes} minutes to '{problem_title}' - Time tracking updated")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number of minutes.")
    
    def add_note_dialog(self):
        """Show dialog to add note to selected problem."""
        selection = self.problems_tree.selection()
        if not selection:
            return
        
        item = self.problems_tree.item(selection[0])
        problem_title = item['text']
        problem = self.tracker.problems.get(problem_title)
        
        if problem:
            note = simpledialog.askstring("Add Note", "Enter your note:")
            if note:
                problem.add_note(note)
                self.save_data()
                self.refresh_all_views()
                self.status_bar.config(text=f"Added note to '{problem_title}' - Data updated")

    def delete_selected_problem(self):
        """Delete the selected problem with confirmation."""
        selection = self.problems_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a problem to delete.")
            return
        
        item = self.problems_tree.item(selection[0])
        problem_title = item['text']
        problem = self.tracker.problems.get(problem_title)
        
        if not problem:
            messagebox.showerror("Error", "Problem not found.")
            return
        
        # Confirmation dialog
        result = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete the problem '{problem_title}'?\n\n"
            f"Topic: {problem.topic}\n"
            f"Difficulty: {problem.difficulty.value}\n"
            f"Status: {problem.status.value}\n\n"
            f"This action cannot be undone."
        )
        
        if result:
            try:
                # Use the centralized delete method from ProgressTracker
                deleted = self.tracker.delete_problem(problem_title)
                
                if deleted:
                    # Save data and refresh views
                    self.save_data()
                    self.refresh_all_views()
                    self.status_bar.config(text=f"Deleted problem '{problem_title}' - Data updated")
                else:
                    messagebox.showerror("Error", "Problem not found in tracker.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting problem: {str(e)}")

    def recalculate_attempts(self):
        """Recalculate attempt counters based on existing sessions."""
        result = messagebox.askyesno(
            "Recalculate Attempts", 
            "This will recalculate all attempt counters based on existing study sessions.\n\n"
            "All current attempt counts will be reset and recalculated from session data.\n\n"
            "Do you want to continue?"
        )
        
        if result:
            try:
                updated_counts = self.tracker.recalculate_attempt_counters()
                
                if updated_counts:
                    # Save the updated data
                    self.save_data()
                    self.refresh_all_views()
                    
                    # Show summary of updates
                    summary_lines = []
                    for problem_title, count in updated_counts.items():
                        summary_lines.append(f"• {problem_title}: {count} attempts")
                    
                    summary = "\n".join(summary_lines[:10])  # Show max 10 problems
                    if len(updated_counts) > 10:
                        summary += f"\n... and {len(updated_counts) - 10} more"
                    
                    messagebox.showinfo(
                        "Recalculation Complete", 
                        f"Successfully recalculated attempt counters for {len(updated_counts)} problems:\n\n{summary}"
                    )
                    
                    self.status_bar.config(text=f"Recalculated attempt counters for {len(updated_counts)} problems")
                else:
                    messagebox.showinfo("Recalculation Complete", "No problems found with session data to update.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error recalculating attempts: {str(e)}")

    def recalculate_time_from_sessions(self):
        """Recalculate problem time spent based on existing sessions."""
        result = messagebox.askyesno(
            "Recalculate Time from Sessions", 
            "This will recalculate all problem time tracking based on existing study sessions.\n\n"
            "All current time spent values will be reset and recalculated by distributing session durations among the problems worked on.\n\n"
            "Do you want to continue?"
        )
        
        if result:
            try:
                updated_times = self.tracker.recalculate_time_from_sessions()
                
                if updated_times:
                    # Save the updated data
                    self.save_data()
                    self.refresh_all_views()
                    
                    # Show summary of updates
                    summary_lines = []
                    for problem_title, time_minutes in updated_times.items():
                        summary_lines.append(f"• {problem_title}: {time_minutes} minutes")
                    
                    summary = "\n".join(summary_lines[:10])  # Show max 10 problems
                    if len(updated_times) > 10:
                        summary += f"\n... and {len(updated_times) - 10} more"
                    
                    messagebox.showinfo(
                        "Time Recalculation Complete", 
                        f"Successfully recalculated time spent for {len(updated_times)} problems:\n\n{summary}"
                    )
                    
                    self.status_bar.config(text=f"Recalculated time tracking for {len(updated_times)} problems")
                else:
                    messagebox.showinfo("Time Recalculation Complete", "No problems found with session data to update.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error recalculating time: {str(e)}")


class ProblemDialog:
    """Dialog for adding/editing problems."""
    
    def __init__(self, parent, topics, problem=None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Problem" if problem is None else "Edit Problem")
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Variables
        self.title_var = tk.StringVar(value=problem.title if problem else "")
        self.difficulty_var = tk.StringVar(value=problem.difficulty.value if problem else "Easy")
        self.topic_var = tk.StringVar(value=problem.topic if problem else "")
        self.description_var = tk.StringVar(value=problem.description if problem else "")
        self.url_var = tk.StringVar(value=problem.url if problem else "")
        self.status_var = tk.StringVar(value=problem.status.value if problem else "Not Started")
        
        self.create_widgets(topics)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self, topics):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Problem Title:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        title_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=(0, 10))
        title_entry.focus()
        
        # Difficulty
        ttk.Label(main_frame, text="Difficulty:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        difficulty_combo = ttk.Combobox(main_frame, textvariable=self.difficulty_var, 
                                       values=['Easy', 'Medium', 'Hard'], state='readonly')
        difficulty_combo.grid(row=1, column=1, sticky='w', pady=(0, 10))
        
        # Topic
        ttk.Label(main_frame, text="Topic:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        topic_combo = ttk.Combobox(main_frame, textvariable=self.topic_var, 
                                  values=list(topics), state='readonly')
        topic_combo.grid(row=2, column=1, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Status
        ttk.Label(main_frame, text="Status:").grid(row=3, column=0, sticky='w', pady=(0, 5))
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var,
                                   values=['Not Started', 'In Progress', 'Completed', 'Needs Review'],
                                   state='readonly')
        status_combo.grid(row=3, column=1, sticky='w', pady=(0, 10))
        status_row = 4
        
        # URL
        ttk.Label(main_frame, text="From (optional):").grid(row=status_row, column=0, sticky='w', pady=(0, 5))
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=status_row, column=1, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=status_row+1, column=0, sticky='nw', pady=(0, 5))
        desc_frame = ttk.Frame(main_frame)
        desc_frame.grid(row=status_row+1, column=1, columnspan=2, sticky='ew', pady=(0, 20))
        
        self.description_text = tk.Text(desc_frame, height=6, width=50, wrap='word')
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient='vertical', command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
        
        self.description_text.pack(side='left', fill='both', expand=True)
        desc_scrollbar.pack(side='right', fill='y')
        
        if self.description_var.get():
            self.description_text.insert('1.0', self.description_var.get())
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=status_row+2, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left')
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
    
    def save(self):
        """Save the problem data."""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a problem title.")
            return
        
        topic = self.topic_var.get()
        if not topic:
            messagebox.showerror("Error", "Please select a topic.")
            return
        
        description = self.description_text.get('1.0', 'end-1c').strip()
        
        # Always include status
        status = self.status_var.get()
        
        self.result = (title, self.difficulty_var.get(), topic, description, self.url_var.get().strip(), status)
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()


class TopicDialog:
    """Dialog for adding topics."""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Topic")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Name
        ttk.Label(main_frame, text="Topic Name:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=(0, 10))
        self.name_entry.focus()
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        self.description_entry = ttk.Entry(main_frame, width=40)
        self.description_entry.grid(row=1, column=1, sticky='ew', pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", command=self.save).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left')
        
        main_frame.columnconfigure(1, weight=1)
    
    def save(self):
        """Save the topic data."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a topic name.")
            return
        
        description = self.description_entry.get().strip()
        self.result = (name, description)
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()


class SessionDialog:
    """Dialog for adding study sessions."""
    
    def __init__(self, parent, problems):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Study Session")
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.problems = problems
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Duration
        ttk.Label(main_frame, text="Duration (minutes):").grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.duration_entry = ttk.Entry(main_frame, width=20)
        self.duration_entry.grid(row=0, column=1, sticky='w', pady=(0, 10))
        self.duration_entry.focus()
        
        # Notes
        ttk.Label(main_frame, text="Session Notes:").grid(row=1, column=0, sticky='nw', pady=(0, 5))
        notes_frame = ttk.Frame(main_frame)
        notes_frame.grid(row=1, column=1, columnspan=2, sticky='ew', pady=(0, 10))
        
        self.notes_text = tk.Text(notes_frame, height=4, width=40, wrap='word')
        notes_scrollbar = ttk.Scrollbar(notes_frame, orient='vertical', command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)
        
        self.notes_text.pack(side='left', fill='both', expand=True)
        notes_scrollbar.pack(side='right', fill='y')
        
        # Problems worked on
        ttk.Label(main_frame, text="Problems Worked On:").grid(row=2, column=0, sticky='nw', pady=(0, 5))
        problems_frame = ttk.Frame(main_frame)
        problems_frame.grid(row=2, column=1, columnspan=2, sticky='ew', pady=(0, 20))
        
        # Listbox for problems selection
        self.problems_listbox = tk.Listbox(problems_frame, height=6, selectmode='multiple')
        problems_scrollbar = ttk.Scrollbar(problems_frame, orient='vertical', command=self.problems_listbox.yview)
        self.problems_listbox.configure(yscrollcommand=problems_scrollbar.set)
        
        for problem in self.problems:
            self.problems_listbox.insert('end', problem)
        
        self.problems_listbox.pack(side='left', fill='both', expand=True)
        problems_scrollbar.pack(side='right', fill='y')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Add", command=self.save).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left')
        
        main_frame.columnconfigure(1, weight=1)
    
    def save(self):
        """Save the session data."""
        try:
            duration = int(self.duration_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid duration in minutes.")
            return
        
        notes = self.notes_text.get('1.0', 'end-1c').strip()
        
        # Get selected problems
        selected_indices = self.problems_listbox.curselection()
        problems_worked = [self.problems_listbox.get(i) for i in selected_indices]
        
        self.result = (duration, notes, problems_worked)
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.dialog.destroy()


class ProblemDetailsDialog:
    """Dialog showing detailed problem information."""
    
    def __init__(self, parent, problem):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Problem Details - {problem.title}")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets(problem)
        
        # Set grab after the window is configured and widgets are created
        self.dialog.update_idletasks()
        self.dialog.grab_set()
        self.dialog.wait_window()
    
    def create_widgets(self, problem):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=problem.title, font=('Arial', 16, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Details frame
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill='x', pady=(0, 10))
        
        # Left column
        left_frame = ttk.Frame(details_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        ttk.Label(left_frame, text=f"Topic: {problem.topic}", font=('Arial', 11)).pack(anchor='w', pady=2)
        ttk.Label(left_frame, text=f"Difficulty: {problem.difficulty.value}", font=('Arial', 11)).pack(anchor='w', pady=2)
        ttk.Label(left_frame, text=f"Status: {problem.status.value}", font=('Arial', 11)).pack(anchor='w', pady=2)
        
        # Right column
        right_frame = ttk.Frame(details_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        time_spent = int(problem.time_spent.total_seconds() / 60)
        ttk.Label(right_frame, text=f"Attempts: {problem.attempts}", font=('Arial', 11)).pack(anchor='w', pady=2)
        ttk.Label(right_frame, text=f"Time Spent: {time_spent} minutes", font=('Arial', 11)).pack(anchor='w', pady=2)
        
        if problem.completed_at:
            completed_date = problem.completed_at.strftime('%Y-%m-%d %H:%M')
            ttk.Label(right_frame, text=f"Completed: {completed_date}", font=('Arial', 11)).pack(anchor='w', pady=2)
        
        # URL
        if problem.url:
            ttk.Label(main_frame, text="From:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            url_label = ttk.Label(main_frame, text=problem.url, foreground='blue', cursor='hand2')
            url_label.pack(anchor='w')
        
        # Description
        if problem.description:
            ttk.Label(main_frame, text="Description:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            
            desc_frame = ttk.Frame(main_frame)
            desc_frame.pack(fill='both', expand=True, pady=(0, 10))
            
            desc_text = tk.Text(desc_frame, height=6, wrap='word', state='disabled')
            desc_scrollbar = ttk.Scrollbar(desc_frame, orient='vertical', command=desc_text.yview)
            desc_text.configure(yscrollcommand=desc_scrollbar.set)
            
            desc_text.config(state='normal')
            desc_text.insert('1.0', problem.description)
            desc_text.config(state='disabled')
            
            desc_text.pack(side='left', fill='both', expand=True)
            desc_scrollbar.pack(side='right', fill='y')
        
        # Notes
        if problem.notes:
            ttk.Label(main_frame, text="Notes:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            
            notes_frame = ttk.Frame(main_frame)
            notes_frame.pack(fill='both', expand=True, pady=(0, 10))
            
            notes_text = tk.Text(notes_frame, height=6, wrap='word', state='disabled')
            notes_scrollbar = ttk.Scrollbar(notes_frame, orient='vertical', command=notes_text.yview)
            notes_text.configure(yscrollcommand=notes_scrollbar.set)
            
            notes_text.config(state='normal')
            for note in problem.notes:
                notes_text.insert('end', f"• {note}\n")
            notes_text.config(state='disabled')
            
            notes_text.pack(side='left', fill='both', expand=True)
            notes_scrollbar.pack(side='right', fill='y')
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=self.dialog.destroy)
        close_btn.pack(pady=20)


class SessionDetailsDialog:
    """Dialog showing detailed session information."""
    
    def __init__(self, parent, session):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Session Details - {session.date.strftime('%Y-%m-%d %H:%M')}")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets(session)
        
        # Make sure the dialog is visible before grabbing focus
        self.dialog.update_idletasks()
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.grab_set()
        
        self.dialog.wait_window()
    
    def create_widgets(self, session):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Study Session", font=('Arial', 16, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Session info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Date: {session.date.strftime('%Y-%m-%d %H:%M')}", 
                 font=('Arial', 11)).pack(anchor='w', pady=2)
        
        duration_minutes = int(session.duration.total_seconds() / 60)
        ttk.Label(info_frame, text=f"Duration: {duration_minutes} minutes", 
                 font=('Arial', 11)).pack(anchor='w', pady=2)
        
        # Problems worked on
        if session.problems_worked:
            ttk.Label(main_frame, text="Problems Worked On:", 
                     font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            
            problems_frame = ttk.Frame(main_frame)
            problems_frame.pack(fill='both', expand=True, pady=(0, 10))
            
            problems_listbox = tk.Listbox(problems_frame, height=6)
            problems_scrollbar = ttk.Scrollbar(problems_frame, orient='vertical', 
                                             command=problems_listbox.yview)
            problems_listbox.configure(yscrollcommand=problems_scrollbar.set)
            
            for problem in session.problems_worked:
                problems_listbox.insert('end', f"• {problem}")
            
            problems_listbox.pack(side='left', fill='both', expand=True)
            problems_scrollbar.pack(side='right', fill='y')
        
        # Session notes
        if session.notes:
            ttk.Label(main_frame, text="Session Notes:", 
                     font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
            
            notes_frame = ttk.Frame(main_frame)
            notes_frame.pack(fill='both', expand=True, pady=(0, 10))
            
            notes_text = tk.Text(notes_frame, height=6, wrap='word', state='disabled')
            notes_scrollbar = ttk.Scrollbar(notes_frame, orient='vertical', 
                                          command=notes_text.yview)
            notes_text.configure(yscrollcommand=notes_scrollbar.set)
            
            notes_text.config(state='normal')
            notes_text.insert('1.0', session.notes)
            notes_text.config(state='disabled')
            
            notes_text.pack(side='left', fill='both', expand=True)
            notes_scrollbar.pack(side='right', fill='y')
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=self.dialog.destroy)
        close_btn.pack(pady=20)


def main():
    """Main function to run the GUI application."""
    app = InterviewTrackerGUI()
    app.root.mainloop()


if __name__ == '__main__':
    main()