"""
Comprehensive logging system for the Siegel RAG application.
Logs all user interactions in structured JSON format.
"""

import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class SiegelLogger:
    """Handles all logging functionality for the Siegel RAG system."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Log file paths
        self.interactions_log = self.log_dir / "interactions.jsonl"
        self.sessions_log = self.log_dir / "sessions.jsonl"
        self.errors_log = self.log_dir / "errors.jsonl"
    
    def log_interaction(self, 
                       user_id: str,
                       pseudonym: str,
                       question: str,
                       answer: str,
                       session_duration: float,
                       timestamp: Optional[datetime] = None,
                       metadata: Optional[Dict] = None):
        """Log a user interaction."""
        if timestamp is None:
            timestamp = datetime.now()
        
        interaction_data = {
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "pseudonym": pseudonym,
            "question": question,
            "answer": answer,
            "session_duration_seconds": session_duration,
            "question_length": len(question),
            "answer_length": len(answer),
            "metadata": metadata or {}
        }
        
        self._write_log_entry(self.interactions_log, interaction_data)
    
    def log_session_start(self, user_id: str, pseudonym: str, timestamp: Optional[datetime] = None):
        """Log session start."""
        if timestamp is None:
            timestamp = datetime.now()
        
        session_data = {
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "pseudonym": pseudonym,
            "event": "session_start"
        }
        
        self._write_log_entry(self.sessions_log, session_data)
    
    def log_session_end(self, user_id: str, pseudonym: str, duration: float, timestamp: Optional[datetime] = None):
        """Log session end."""
        if timestamp is None:
            timestamp = datetime.now()
        
        session_data = {
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "pseudonym": pseudonym,
            "event": "session_end",
            "duration_seconds": duration
        }
        
        self._write_log_entry(self.sessions_log, session_data)
    
    def log_error(self, user_id: str, error_type: str, error_message: str, 
                  context: Optional[Dict] = None, timestamp: Optional[datetime] = None):
        """Log an error."""
        if timestamp is None:
            timestamp = datetime.now()
        
        error_data = {
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        self._write_log_entry(self.errors_log, error_data)
    
    def _write_log_entry(self, log_file: Path, data: Dict):
        """Write a log entry to the specified file."""
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Error writing to log file {log_file}: {e}")
    
    def get_interactions_df(self) -> pd.DataFrame:
        """Load interactions as a pandas DataFrame."""
        return self._load_jsonl_as_df(self.interactions_log)
    
    def get_sessions_df(self) -> pd.DataFrame:
        """Load sessions as a pandas DataFrame."""
        return self._load_jsonl_as_df(self.sessions_log)
    
    def get_errors_df(self) -> pd.DataFrame:
        """Load errors as a pandas DataFrame."""
        return self._load_jsonl_as_df(self.errors_log)
    
    def _load_jsonl_as_df(self, log_file: Path) -> pd.DataFrame:
        """Load a JSONL file as a pandas DataFrame."""
        if not log_file.exists():
            return pd.DataFrame()
        
        try:
            data = []
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            
            if data:
                df = pd.DataFrame(data)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"Error loading log file {log_file}: {e}")
            return pd.DataFrame()
    
    def export_to_csv(self, output_dir: str = "exports") -> Dict[str, str]:
        """Export all logs to CSV files."""
        export_dir = Path(output_dir)
        export_dir.mkdir(exist_ok=True)
        
        exported_files = {}
        
        # Export interactions
        interactions_df = self.get_interactions_df()
        if not interactions_df.empty:
            interactions_file = export_dir / f"interactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            interactions_df.to_csv(interactions_file, index=False)
            exported_files["interactions"] = str(interactions_file)
        
        # Export sessions
        sessions_df = self.get_sessions_df()
        if not sessions_df.empty:
            sessions_file = export_dir / f"sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            sessions_df.to_csv(sessions_file, index=False)
            exported_files["sessions"] = str(sessions_file)
        
        # Export errors
        errors_df = self.get_errors_df()
        if not errors_df.empty:
            errors_file = export_dir / f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            errors_df.to_csv(errors_file, index=False)
            exported_files["errors"] = str(errors_file)
        
        return exported_files
    
    def export_to_json(self, output_dir: str = "exports") -> Dict[str, str]:
        """Export all logs to JSON files."""
        export_dir = Path(output_dir)
        export_dir.mkdir(exist_ok=True)
        
        exported_files = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export interactions
        interactions_df = self.get_interactions_df()
        if not interactions_df.empty:
            interactions_file = export_dir / f"interactions_{timestamp}.json"
            interactions_df.to_json(interactions_file, orient="records", date_format="iso")
            exported_files["interactions"] = str(interactions_file)
        
        # Export sessions
        sessions_df = self.get_sessions_df()
        if not sessions_df.empty:
            sessions_file = export_dir / f"sessions_{timestamp}.json"
            sessions_df.to_json(sessions_file, orient="records", date_format="iso")
            exported_files["sessions"] = str(sessions_file)
        
        # Export errors
        errors_df = self.get_errors_df()
        if not errors_df.empty:
            errors_file = export_dir / f"errors_{timestamp}.json"
            errors_df.to_json(errors_file, orient="records", date_format="iso")
            exported_files["errors"] = str(errors_file)
        
        return exported_files
    
    def get_stats(self) -> Dict[str, Any]:
        """Get quick statistics about the logs."""
        interactions_df = self.get_interactions_df()
        sessions_df = self.get_sessions_df()
        errors_df = self.get_errors_df()
        
        stats = {
            "total_interactions": len(interactions_df),
            "unique_users": interactions_df['user_id'].nunique() if not interactions_df.empty else 0,
            "total_sessions": len(sessions_df[sessions_df['event'] == 'session_start']) if not sessions_df.empty else 0,
            "total_errors": len(errors_df),
            "avg_session_duration": 0,
            "avg_question_length": 0,
            "avg_answer_length": 0,
            "most_active_user": None,
            "last_interaction": None
        }
        
        if not interactions_df.empty:
            stats["avg_session_duration"] = interactions_df['session_duration_seconds'].mean()
            stats["avg_question_length"] = interactions_df['question_length'].mean()
            stats["avg_answer_length"] = interactions_df['answer_length'].mean()
            stats["most_active_user"] = interactions_df['pseudonym'].value_counts().index[0]
            stats["last_interaction"] = interactions_df['timestamp'].max().isoformat()
        
        return stats
