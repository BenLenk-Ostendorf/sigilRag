"""
Utility functions for the explAIner system.
Helper functions and common utilities specific to explAIner functionality.
"""

import streamlit as st
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

class ExplainerUtils:
    """Utility functions for the explAIner system."""
    
    @staticmethod
    def validate_topic_input(topic: str) -> Tuple[bool, str]:
        """
        Validate user input for topics.
        
        Args:
            topic: The topic string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not topic or not topic.strip():
            return False, "Bitte geben Sie ein Thema ein."
        
        if len(topic.strip()) < 3:
            return False, "Das Thema sollte mindestens 3 Zeichen lang sein."
        
        if len(topic.strip()) > 200:
            return False, "Das Thema sollte nicht länger als 200 Zeichen sein."
        
        # Check for potentially problematic content
        if re.search(r'[<>{}[\]\\]', topic):
            return False, "Das Thema enthält ungültige Zeichen."
        
        return True, ""
    
    @staticmethod
    def format_explanation_for_display(explanation: str) -> str:
        """
        Format explanation text for better display in Streamlit.
        
        Args:
            explanation: Raw explanation text
            
        Returns:
            Formatted explanation text
        """
        if not explanation:
            return ""
        
        # Ensure proper markdown formatting
        formatted = explanation.strip()
        
        # Add spacing around headers if missing
        formatted = re.sub(r'(\n|^)(#{1,6})\s*([^\n]+)', r'\1\2 \3\n', formatted)
        
        # Ensure proper list formatting
        formatted = re.sub(r'(\n|^)([*-])\s*([^\n]+)', r'\1\2 \3', formatted)
        
        return formatted
    
    @staticmethod
    def extract_key_concepts(explanation: str) -> List[str]:
        """
        Extract key concepts from an explanation for follow-up suggestions.
        
        Args:
            explanation: The explanation text
            
        Returns:
            List of key concepts found
        """
        if not explanation:
            return []
        
        # Simple keyword extraction (can be enhanced with NLP)
        concepts = []
        
        # Look for words in bold or headers
        bold_words = re.findall(r'\*\*(.*?)\*\*', explanation)
        header_words = re.findall(r'#{1,6}\s+(.*?)(?:\n|$)', explanation)
        
        concepts.extend(bold_words)
        concepts.extend(header_words)
        
        # Clean and deduplicate
        concepts = [c.strip() for c in concepts if c.strip()]
        concepts = list(set(concepts))
        
        return concepts[:10]  # Limit to top 10
    
    @staticmethod
    def create_complexity_badge(complexity_level: str) -> str:
        """
        Create a visual badge for complexity level.
        
        Args:
            complexity_level: The complexity level
            
        Returns:
            HTML badge string
        """
        badges = {
            "beginner": "🟢 Anfänger",
            "intermediate": "🟡 Fortgeschritten", 
            "advanced": "🔴 Experte"
        }
        
        return badges.get(complexity_level, "⚪ Unbekannt")
    
    @staticmethod
    def estimate_reading_time(text: str) -> int:
        """
        Estimate reading time for text in minutes.
        
        Args:
            text: The text to analyze
            
        Returns:
            Estimated reading time in minutes
        """
        if not text:
            return 0
        
        # Average reading speed: ~200 words per minute
        word_count = len(text.split())
        reading_time = max(1, round(word_count / 200))
        
        return reading_time
    
    @staticmethod
    def create_topic_suggestions(base_topic: str) -> List[str]:
        """
        Create related topic suggestions based on a base topic.
        
        Args:
            base_topic: The original topic
            
        Returns:
            List of suggested related topics
        """
        # Common AI/ML related expansions
        expansions = [
            f"{base_topic} Grundlagen",
            f"{base_topic} Anwendungen",
            f"{base_topic} vs. traditionelle Methoden",
            f"Praktische {base_topic} Beispiele",
            f"{base_topic} Tools und Frameworks",
            f"Zukunft von {base_topic}",
            f"{base_topic} Herausforderungen",
            f"Ethik in {base_topic}"
        ]
        
        return expansions[:5]  # Return top 5 suggestions
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename for safe file operations.
        
        Args:
            filename: The original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\s+', '_', sanitized)
        sanitized = sanitized.strip('._')
        
        return sanitized[:100]  # Limit length
    
    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """
        Format timestamp for display.
        
        Args:
            timestamp: ISO format timestamp
            
        Returns:
            Formatted timestamp string
        """
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return timestamp
    
    @staticmethod
    def calculate_session_stats(activities: List[Dict]) -> Dict[str, Any]:
        """
        Calculate session statistics from activities.
        
        Args:
            activities: List of activity records
            
        Returns:
            Dictionary with session statistics
        """
        if not activities:
            return {
                "total_activities": 0,
                "session_duration": 0,
                "most_common_type": "N/A",
                "topics_explored": 0
            }
        
        # Count activities by type
        type_counts = {}
        topics = set()
        
        for activity in activities:
            activity_type = activity.get("action", "unknown")
            type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
            
            if "topic" in activity:
                topics.add(activity["topic"])
        
        # Find most common activity type
        most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "N/A"
        
        # Estimate session duration (simplified)
        session_duration = len(activities) * 2  # 2 minutes per activity
        
        return {
            "total_activities": len(activities),
            "session_duration": session_duration,
            "most_common_type": most_common_type,
            "topics_explored": len(topics)
        }
    
    @staticmethod
    def create_progress_indicator(current: int, total: int) -> str:
        """
        Create a text-based progress indicator.
        
        Args:
            current: Current progress value
            total: Total/maximum value
            
        Returns:
            Progress indicator string
        """
        if total == 0:
            return "⚪⚪⚪⚪⚪ 0%"
        
        percentage = min(100, (current / total) * 100)
        filled_circles = int(percentage / 20)  # 5 circles total
        empty_circles = 5 - filled_circles
        
        progress_bar = "🔵" * filled_circles + "⚪" * empty_circles
        return f"{progress_bar} {percentage:.0f}%"
    
    @staticmethod
    def get_explanation_type_icon(explanation_type: str) -> str:
        """
        Get an icon for the explanation type.
        
        Args:
            explanation_type: The type of explanation
            
        Returns:
            Icon string
        """
        icons = {
            "concept": "💡",
            "process": "⚙️",
            "comparison": "⚖️",
            "example": "📝",
            "visualization": "📊"
        }
        
        return icons.get(explanation_type, "❓")
    
    @staticmethod
    def validate_api_response(response: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate API response structure.
        
        Args:
            response: API response dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["success"]
        
        for field in required_fields:
            if field not in response:
                return False, f"Fehlendes Feld in API-Antwort: {field}"
        
        if response.get("success") and "explanation" not in response:
            return False, "Erfolgreiche Antwort ohne Erklärung"
        
        if not response.get("success") and "error" not in response:
            return False, "Fehlerhafte Antwort ohne Fehlermeldung"
        
        return True, ""
