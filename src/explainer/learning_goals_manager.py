"""
Learning Goals Manager for the explAIner system.
Handles loading, tracking, and visualization of student learning goals.
"""

import streamlit as st
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class LearningGoalsManager:
    """Manages learning goals tracking and progress for students."""
    
    def __init__(self, goals_file_path: str = None):
        """Initialize the learning goals manager."""
        if goals_file_path is None:
            # Default path to learning goals file in data/information/
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.goals_file_path = os.path.join(project_root, "data", "information", "learning_goals.md")
        else:
            self.goals_file_path = goals_file_path
            
        self.learning_goals = self._load_learning_goals()
    
    def _load_learning_goals(self) -> List[Dict[str, str]]:
        """Load learning goals from the markdown file."""
        goals = []
        
        try:
            if os.path.exists(self.goals_file_path):
                with open(self.goals_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse markdown content - new simple bullet list format
                lines = content.strip().split('\n')
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line.startswith('- '):
                        # Extract bullet point content
                        description = line[2:].strip()  # Remove '- '
                        goal = {
                            'id': f'goal_{i + 1}',
                            'number': str(i + 1),
                            'title': f'Lernziel {i + 1}',
                            'description': description
                        }
                        goals.append(goal)
            
            else:
                st.warning(f"⚠️ Learning goals file not found: {self.goals_file_path}")
        
        except Exception as e:
            st.error(f"❌ Error loading learning goals: {str(e)}")
        
        return goals
    
    def get_learning_goals(self) -> List[Dict[str, str]]:
        """Get all learning goals."""
        return self.learning_goals
    
    def get_user_progress(self, user_id: str) -> Dict[str, bool]:
        """Get user's progress on learning goals."""
        progress_key = f"learning_progress_{user_id}"
        
        if progress_key not in st.session_state:
            # Initialize progress for all goals as False
            st.session_state[progress_key] = {
                goal['id']: False for goal in self.learning_goals
            }
        
        return st.session_state[progress_key]
    
    def update_goal_progress(self, user_id: str, goal_id: str, completed: bool) -> None:
        """Update progress for a specific learning goal."""
        progress_key = f"learning_progress_{user_id}"
        
        if progress_key not in st.session_state:
            st.session_state[progress_key] = {}
        
        st.session_state[progress_key][goal_id] = completed
        
        # Log the progress update
        self._log_progress_update(user_id, goal_id, completed)
    
    def _log_progress_update(self, user_id: str, goal_id: str, completed: bool) -> None:
        """Log progress updates for analytics."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': 'learning_goal_update',
            'goal_id': goal_id,
            'completed': completed
        }
        
        # Store in session state for potential logging
        if 'learning_goal_logs' not in st.session_state:
            st.session_state['learning_goal_logs'] = []
        
        st.session_state['learning_goal_logs'].append(log_entry)
    
    def get_progress_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get progress statistics for a user."""
        progress = self.get_user_progress(user_id)
        total_goals = len(self.learning_goals)
        completed_goals = sum(1 for completed in progress.values() if completed)
        
        return {
            'total_goals': total_goals,
            'completed_goals': completed_goals,
            'completion_percentage': (completed_goals / total_goals * 100) if total_goals > 0 else 0,
            'remaining_goals': total_goals - completed_goals
        }
    
    def render_learning_goals_overview(self, user_id: str) -> None:
        """Render an overview of all learning goals with progress."""
        st.subheader("🎯 Ihre Lernziele")
        
        # Get progress statistics
        stats = self.get_progress_statistics(user_id)
        progress = self.get_user_progress(user_id)
        
        # Progress overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 Gesamt", stats['total_goals'])
        
        with col2:
            st.metric("✅ Erreicht", stats['completed_goals'])
        
        with col3:
            st.metric("📈 Fortschritt", f"{stats['completion_percentage']:.0f}%")
        
        # Progress bar
        progress_bar = st.progress(stats['completion_percentage'] / 100)
        
        st.divider()
        
        # Individual learning goals
        st.markdown("### 📋 Lernziele im Detail")
        
        for goal in self.learning_goals:
            goal_id = goal['id']
            is_completed = progress.get(goal_id, False)
            
            # Create expandable section for each goal
            with st.expander(
                f"{'✅' if is_completed else '⏳'} {goal['number']}. {goal['title']}", 
                expanded=not is_completed
            ):
                st.markdown(f"**Lernziel:** {goal['description']}")
                
                # Checkbox to mark as completed
                new_status = st.checkbox(
                    "Als erreicht markieren",
                    value=is_completed,
                    key=f"goal_checkbox_{goal_id}",
                    help=f"Markieren Sie dieses Lernziel als erreicht, wenn Sie es erfüllt haben."
                )
                
                # Update progress if changed
                if new_status != is_completed:
                    self.update_goal_progress(user_id, goal_id, new_status)
                    st.rerun()
                
                # Show completion status
                if new_status:
                    st.success("🎉 Lernziel erreicht!")
                else:
                    st.info("💪 Arbeiten Sie daran, dieses Lernziel zu erreichen.")
    
    def render_progress_summary(self, user_id: str) -> None:
        """Render a compact progress summary."""
        stats = self.get_progress_statistics(user_id)
        progress = self.get_user_progress(user_id)
        
        st.markdown("#### 🏆 Ihr Lernfortschritt")
        
        # Create visual progress indicator
        progress_text = f"{stats['completed_goals']}/{stats['total_goals']} Lernziele erreicht"
        st.markdown(f"**{progress_text}** ({stats['completion_percentage']:.0f}%)")
        
        # Progress bar
        st.progress(stats['completion_percentage'] / 100)
        
        # Show completed goals
        completed_goals = [goal for goal in self.learning_goals if progress.get(goal['id'], False)]
        
        if completed_goals:
            st.markdown("**✅ Erreichte Lernziele:**")
            for goal in completed_goals:
                st.markdown(f"- {goal['number']}. {goal['title']}")
        
        # Show remaining goals
        remaining_goals = [goal for goal in self.learning_goals if not progress.get(goal['id'], False)]
        
        if remaining_goals:
            st.markdown("**⏳ Noch zu erreichende Lernziele:**")
            for goal in remaining_goals:
                st.markdown(f"- {goal['number']}. {goal['title']}")
    
    def get_next_goal_suggestion(self, user_id: str) -> Optional[Dict[str, str]]:
        """Get the next learning goal the user should work on."""
        progress = self.get_user_progress(user_id)
        
        for goal in self.learning_goals:
            if not progress.get(goal['id'], False):
                return goal
        
        return None  # All goals completed
    
    def render_next_goal_suggestion(self, user_id: str) -> None:
        """Render suggestion for the next learning goal to work on."""
        next_goal = self.get_next_goal_suggestion(user_id)
        
        if next_goal:
            st.info(f"💡 **Nächstes Lernziel:** {next_goal['number']}. {next_goal['title']}")
            st.markdown(f"_{next_goal['description']}_")
        else:
            st.success("🎉 **Herzlichen Glückwunsch!** Sie haben alle Lernziele erreicht!")
    
    def export_progress(self, user_id: str) -> Dict[str, Any]:
        """Export user's learning progress for analytics."""
        progress = self.get_user_progress(user_id)
        stats = self.get_progress_statistics(user_id)
        
        return {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'learning_goals': self.learning_goals,
            'progress': progress,
            'statistics': stats,
            'logs': st.session_state.get('learning_goal_logs', [])
        }
