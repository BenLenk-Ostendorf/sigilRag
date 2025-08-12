"""
Logging functionality for the explAIner system.
Separate from the main RAG logger to maintain clean separation.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st

class ExplainerLogger:
    """Logger specifically for explAIner system activities."""
    
    def __init__(self, log_dir: str = "logs/explainer"):
        """Initialize the explAIner logger."""
        self.log_dir = log_dir
        self.ensure_log_directory()
        
        # Log file paths
        self.explanation_log = os.path.join(log_dir, "explanations.jsonl")
        self.learning_path_log = os.path.join(log_dir, "learning_paths.jsonl")
        self.activity_log = os.path.join(log_dir, "activities.jsonl")
    
    def ensure_log_directory(self) -> None:
        """Ensure the log directory exists."""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def log_explanation_request(self, user_id: str, topic: str, explanation_type: str, 
                              complexity_level: str, success: bool, 
                              additional_data: Optional[Dict] = None) -> None:
        """Log an explanation request."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": "explanation_request",
            "topic": topic,
            "explanation_type": explanation_type,
            "complexity_level": complexity_level,
            "success": success,
            "session_id": st.session_state.get("user_session", "unknown")
        }
        
        if additional_data:
            log_entry.update(additional_data)
        
        self._write_log_entry(self.explanation_log, log_entry)
        self._write_log_entry(self.activity_log, log_entry)
    
    def log_learning_path_request(self, user_id: str, topic: str, 
                                additional_data: Optional[Dict] = None) -> None:
        """Log a learning path creation request."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": "learning_path_request",
            "topic": topic,
            "session_id": st.session_state.get("user_session", "unknown")
        }
        
        if additional_data:
            log_entry.update(additional_data)
        
        self._write_log_entry(self.learning_path_log, log_entry)
        self._write_log_entry(self.activity_log, log_entry)
    
    def log_user_interaction(self, user_id: str, interaction_type: str, 
                           details: Dict[str, Any]) -> None:
        """Log general user interactions."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": "user_interaction",
            "interaction_type": interaction_type,
            "details": details,
            "session_id": st.session_state.get("user_session", "unknown")
        }
        
        self._write_log_entry(self.activity_log, log_entry)
    
    def _write_log_entry(self, log_file: str, entry: Dict[str, Any]) -> None:
        """Write a log entry to the specified file."""
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            st.error(f"Fehler beim Schreiben des Logs: {e}")
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a specific user."""
        stats = {
            "total_explanations": 0,
            "learning_paths": 0,
            "session_time": 0,
            "favorite_topics": [],
            "complexity_preference": "intermediate"
        }
        
        try:
            # Count explanations
            if os.path.exists(self.explanation_log):
                with open(self.explanation_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if entry.get("user_id") == user_id:
                            stats["total_explanations"] += 1
            
            # Count learning paths
            if os.path.exists(self.learning_path_log):
                with open(self.learning_path_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if entry.get("user_id") == user_id:
                            stats["learning_paths"] += 1
            
            # Calculate session time (simplified)
            stats["session_time"] = self._calculate_session_time(user_id)
            
        except Exception as e:
            st.error(f"Fehler beim Laden der Statistiken: {e}")
        
        return stats
    
    def get_recent_activities(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activities for a user."""
        activities = []
        
        try:
            if os.path.exists(self.activity_log):
                with open(self.activity_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if entry.get("user_id") == user_id:
                            activities.append(entry)
                
                # Sort by timestamp (most recent first) and limit
                activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                return activities[:limit]
        
        except Exception as e:
            st.error(f"Fehler beim Laden der Aktivitäten: {e}")
        
        return activities
    
    def _calculate_session_time(self, user_id: str) -> int:
        """Calculate approximate session time for a user (in minutes)."""
        # Simplified calculation - count activities and estimate time
        activity_count = 0
        
        try:
            if os.path.exists(self.activity_log):
                with open(self.activity_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if entry.get("user_id") == user_id:
                            activity_count += 1
            
            # Rough estimate: 2 minutes per activity
            return activity_count * 2
        
        except Exception:
            return 0
    
    def export_user_data(self, user_id: str, format: str = "json") -> Optional[str]:
        """Export all data for a specific user."""
        user_data = {
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "statistics": self.get_user_statistics(user_id),
            "activities": self.get_recent_activities(user_id, limit=100)
        }
        
        try:
            if format.lower() == "json":
                return json.dumps(user_data, indent=2, ensure_ascii=False)
            elif format.lower() == "csv":
                # Convert to CSV format (simplified)
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write headers
                writer.writerow(["timestamp", "action", "topic", "type", "success"])
                
                # Write activities
                for activity in user_data["activities"]:
                    writer.writerow([
                        activity.get("timestamp", ""),
                        activity.get("action", ""),
                        activity.get("topic", ""),
                        activity.get("explanation_type", ""),
                        activity.get("success", "")
                    ])
                
                return output.getvalue()
        
        except Exception as e:
            st.error(f"Fehler beim Exportieren: {e}")
            return None
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics for explAIner."""
        stats = {
            "total_users": set(),
            "total_explanations": 0,
            "total_learning_paths": 0,
            "popular_topics": {},
            "complexity_distribution": {"beginner": 0, "intermediate": 0, "advanced": 0}
        }
        
        try:
            # Analyze explanation logs
            if os.path.exists(self.explanation_log):
                with open(self.explanation_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        stats["total_users"].add(entry.get("user_id"))
                        stats["total_explanations"] += 1
                        
                        # Track topics
                        topic = entry.get("topic", "")
                        if topic:
                            stats["popular_topics"][topic] = stats["popular_topics"].get(topic, 0) + 1
                        
                        # Track complexity
                        complexity = entry.get("complexity_level", "intermediate")
                        if complexity in stats["complexity_distribution"]:
                            stats["complexity_distribution"][complexity] += 1
            
            # Analyze learning path logs
            if os.path.exists(self.learning_path_log):
                with open(self.learning_path_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        stats["total_users"].add(entry.get("user_id"))
                        stats["total_learning_paths"] += 1
            
            # Convert set to count
            stats["total_users"] = len(stats["total_users"])
            
        except Exception as e:
            st.error(f"Fehler beim Laden der Systemstatistiken: {e}")
        
        return stats
