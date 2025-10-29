#!/usr/bin/env python3
"""
Additional utilities and reporting features for the interview tracker.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
try:
    from .models import ProgressTracker, Status, Difficulty
except ImportError:
    from models import ProgressTracker, Status, Difficulty
from tabulate import tabulate


class ProgressAnalyzer:
    """Advanced analytics for interview preparation progress."""
    
    def __init__(self, tracker: ProgressTracker):
        self.tracker = tracker
    
    def get_weekly_progress(self, weeks: int = 4) -> Dict[str, List[int]]:
        """Get weekly completion progress for the last N weeks."""
        now = datetime.now()
        weekly_data = {'weeks': [], 'completed': [], 'attempted': []}
        
        for week in range(weeks):
            week_start = now - timedelta(weeks=week+1)
            week_end = now - timedelta(weeks=week)
            
            completed_this_week = 0
            attempted_this_week = 0
            
            for problem in self.tracker.problems.values():
                if problem.completed_at and week_start <= problem.completed_at <= week_end:
                    completed_this_week += 1
                if week_start <= problem.created_at <= week_end:
                    attempted_this_week += 1
            
            weekly_data['weeks'].append(f"Week {weeks-week}")
            weekly_data['completed'].append(completed_this_week)
            weekly_data['attempted'].append(attempted_this_week)
        
        return weekly_data
    
    def get_time_distribution(self) -> Dict[str, float]:
        """Get time spent distribution by topic."""
        topic_time = {}
        
        for problem in self.tracker.problems.values():
            topic = problem.topic
            time_minutes = problem.time_spent.total_seconds() / 60
            
            if topic not in topic_time:
                topic_time[topic] = 0
            topic_time[topic] += time_minutes
        
        return topic_time
    
    def get_difficulty_completion_rates(self) -> Dict[str, Dict[str, int]]:
        """Get completion rates by difficulty level."""
        difficulty_stats = {}
        
        for difficulty in Difficulty:
            difficulty_stats[difficulty.value] = {
                'total': 0,
                'completed': 0,
                'rate': 0.0
            }
        
        for problem in self.tracker.problems.values():
            difficulty = problem.difficulty.value
            difficulty_stats[difficulty]['total'] += 1
            
            if problem.status == Status.COMPLETED:
                difficulty_stats[difficulty]['completed'] += 1
        
        # Calculate rates
        for difficulty in difficulty_stats:
            total = difficulty_stats[difficulty]['total']
            completed = difficulty_stats[difficulty]['completed']
            if total > 0:
                difficulty_stats[difficulty]['rate'] = (completed / total) * 100
        
        return difficulty_stats
    
    def get_problem_attempts_analysis(self) -> Dict[str, int]:
        """Analyze problems by number of attempts needed."""
        attempts_distribution = {
            '1 attempt': 0,
            '2 attempts': 0,
            '3+ attempts': 0,
            'not attempted': 0
        }
        
        for problem in self.tracker.problems.values():
            if problem.attempts == 0:
                attempts_distribution['not attempted'] += 1
            elif problem.attempts == 1:
                attempts_distribution['1 attempt'] += 1
            elif problem.attempts == 2:
                attempts_distribution['2 attempts'] += 1
            else:
                attempts_distribution['3+ attempts'] += 1
        
        return attempts_distribution
    
    def get_productivity_insights(self) -> Dict[str, any]:
        """Get insights about study productivity."""
        if not self.tracker.sessions:
            return {'message': 'No study sessions recorded yet'}
        
        total_time = sum((s.duration for s in self.tracker.sessions), timedelta(0))
        avg_session_length = total_time / len(self.tracker.sessions)
        
        # Find most productive session
        most_productive = max(self.tracker.sessions, 
                            key=lambda s: len(s.problems_worked))
        
        # Calculate problems per hour
        total_problems = len([p for p in self.tracker.problems.values() 
                            if p.status == Status.COMPLETED])
        total_hours = total_time.total_seconds() / 3600
        problems_per_hour = total_problems / total_hours if total_hours > 0 else 0
        
        return {
            'total_study_time': total_time,
            'avg_session_length': avg_session_length,
            'total_sessions': len(self.tracker.sessions),
            'most_productive_session': {
                'date': most_productive.date,
                'duration': most_productive.duration,
                'problems_count': len(most_productive.problems_worked)
            },
            'problems_per_hour': problems_per_hour
        }
    
    def generate_progress_report(self) -> str:
        """Generate a comprehensive progress report."""
        report = []
        report.append("📊 COMPREHENSIVE PROGRESS REPORT")
        report.append("=" * 50)
        
        # Overall stats
        overall = self.tracker.get_overall_stats()
        report.append(f"\n📈 Overall Progress:")
        report.append(f"  Total Problems: {overall['total_problems']}")
        report.append(f"  Completed: {overall['completed_problems']} ({overall['completion_rate']:.1f}%)")
        report.append(f"  Study Time: {overall['total_study_time_hours']:.1f} hours")
        
        # Difficulty analysis
        difficulty_stats = self.get_difficulty_completion_rates()
        report.append(f"\n🎯 Completion by Difficulty:")
        for difficulty, stats in difficulty_stats.items():
            if stats['total'] > 0:
                report.append(f"  {difficulty}: {stats['completed']}/{stats['total']} ({stats['rate']:.1f}%)")
        
        # Time distribution
        time_dist = self.get_time_distribution()
        if time_dist:
            report.append(f"\n⏱️  Time Spent by Topic:")
            for topic, minutes in sorted(time_dist.items(), key=lambda x: x[1], reverse=True):
                hours = minutes / 60
                report.append(f"  {topic}: {hours:.1f} hours")
        
        # Productivity insights
        productivity = self.get_productivity_insights()
        if 'message' not in productivity:
            report.append(f"\n💪 Productivity Insights:")
            avg_minutes = productivity['avg_session_length'].total_seconds() / 60
            report.append(f"  Average session: {avg_minutes:.0f} minutes")
            report.append(f"  Problems per hour: {productivity['problems_per_hour']:.1f}")
            
            most_prod = productivity['most_productive_session']
            prod_minutes = most_prod['duration'].total_seconds() / 60
            report.append(f"  Best session: {most_prod['problems_count']} problems in {prod_minutes:.0f} minutes")
        
        return "\n".join(report)
    
    def get_recommendations(self) -> List[str]:
        """Get personalized recommendations based on progress."""
        recommendations = []
        
        overall = self.tracker.get_overall_stats()
        difficulty_stats = self.get_difficulty_completion_rates()
        
        # Study time recommendations
        if overall['total_study_time_hours'] < 10:
            recommendations.append("📚 Consider increasing your study time. Aim for at least 1-2 hours per day.")
        
        # Difficulty recommendations
        easy_rate = difficulty_stats.get('Easy', {}).get('rate', 0)
        medium_rate = difficulty_stats.get('Medium', {}).get('rate', 0)
        hard_rate = difficulty_stats.get('Hard', {}).get('rate', 0)
        
        if easy_rate < 80:
            recommendations.append("🟢 Focus on mastering Easy problems first to build confidence.")
        elif medium_rate < 60:
            recommendations.append("🟡 Good progress on Easy problems! Time to tackle more Medium problems.")
        elif hard_rate < 40:
            recommendations.append("🔴 Strong foundation! Challenge yourself with more Hard problems.")
        
        # Topic recommendations
        topic_stats = self.tracker.get_topic_stats()
        weakest_topic = min(topic_stats.items(), key=lambda x: x[1]['completion_rate']) if topic_stats else None
        
        if weakest_topic and weakest_topic[1]['completion_rate'] < 50:
            recommendations.append(f"🎯 Consider spending more time on {weakest_topic[0]} - your weakest area.")
        
        # Session recommendations
        productivity = self.get_productivity_insights()
        if 'avg_session_length' in productivity:
            avg_minutes = productivity['avg_session_length'].total_seconds() / 60
            if avg_minutes < 60:
                recommendations.append("⏰ Try longer study sessions (60-90 minutes) for deeper focus.")
            elif avg_minutes > 120:
                recommendations.append("☕ Consider shorter sessions with breaks to maintain concentration.")
        
        if not recommendations:
            recommendations.append("🎉 Great job! Keep up the consistent practice!")
        
        return recommendations