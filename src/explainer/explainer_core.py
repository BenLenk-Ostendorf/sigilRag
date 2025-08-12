"""
Core functionality for the explAIner system.
Handles AI explanation logic, model interactions, and explanation generation.
"""

import streamlit as st
import openai
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

class ExplainerCore:
    """Core explAIner system for AI explanation and understanding."""
    
    def __init__(self):
        """Initialize the explAIner core system."""
        # Don't load secrets during init - use lazy loading
        self.openai_api_key = None
        self._secrets_loaded = False
        
        # explAIner-specific configuration
        self.explanation_model = "gpt-4"
        self.max_tokens = 1000
        self.temperature = 0.7
        
        # Explanation types
        self.explanation_types = {
            "concept": "Konzept Erklärung",
            "process": "Prozess Erklärung", 
            "comparison": "Vergleichende Analyse",
            "example": "Praktisches Beispiel",
            "visualization": "Visuelle Darstellung"
        }
        
    def _load_api_key(self):
        """Lazy load the OpenAI API key from secrets or environment."""
        if self._secrets_loaded:
            return
            
        try:
            self.openai_api_key = st.secrets["explainer"]["OPENAI_API_KEY"]
        except KeyError:
            # Fallback to environment variable for development
            self.openai_api_key = os.getenv("EXPLAINER_OPENAI_API_KEY")
            if not self.openai_api_key:
                st.warning("⚠️ explAIner OpenAI API key not found in secrets or environment variables.")
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            
        self._secrets_loaded = True
    
    def is_configured(self) -> bool:
        """Check if the explAIner system is properly configured."""
        self._load_api_key()
        return bool(self.openai_api_key)
    
    def generate_explanation(self, topic: str, explanation_type: str = "concept", 
                           complexity_level: str = "intermediate") -> Dict[str, Any]:
        """
        Generate an AI explanation for a given topic.
        
        Args:
            topic: The topic to explain
            explanation_type: Type of explanation (concept, process, comparison, etc.)
            complexity_level: beginner, intermediate, or advanced
            
        Returns:
            Dictionary containing the explanation and metadata
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "explanation": None
            }
        
        try:
            # Create explanation prompt based on type and complexity
            prompt = self._create_explanation_prompt(topic, explanation_type, complexity_level)
            
            response = openai.ChatCompletion.create(
                model=self.explanation_model,
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener AI-Erklärer, der komplexe Konzepte verständlich macht."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            explanation = response.choices[0].message.content
            
            return {
                "success": True,
                "explanation": explanation,
                "topic": topic,
                "type": explanation_type,
                "complexity": complexity_level,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "explanation": None
            }
    
    def _create_explanation_prompt(self, topic: str, explanation_type: str, 
                                 complexity_level: str) -> str:
        """Create a tailored prompt for explanation generation."""
        
        complexity_instructions = {
            "beginner": "Erkläre es sehr einfach, als würdest du es einem Anfänger erklären. Verwende alltägliche Beispiele.",
            "intermediate": "Erkläre es mit mittlerem Detailgrad für jemanden mit Grundkenntnissen.",
            "advanced": "Erkläre es detailliert und technisch für Experten."
        }
        
        type_instructions = {
            "concept": "Erkläre das Konzept klar und strukturiert.",
            "process": "Beschreibe den Prozess Schritt für Schritt.",
            "comparison": "Vergleiche verschiedene Aspekte und zeige Unterschiede auf.",
            "example": "Gib praktische, nachvollziehbare Beispiele.",
            "visualization": "Beschreibe, wie man das Thema visuell darstellen könnte."
        }
        
        prompt = f"""
Thema: {topic}

Erklärungstyp: {type_instructions.get(explanation_type, "Erkläre das Thema umfassend.")}

Komplexitätslevel: {complexity_instructions.get(complexity_level, "Erkläre es verständlich.")}

Bitte erstelle eine klare, strukturierte Erklärung auf Deutsch. Verwende Markdown-Formatierung für bessere Lesbarkeit.
Gliedere die Antwort in logische Abschnitte und verwende Beispiele wo angebracht.
"""
        
        return prompt
    
    def get_explanation_suggestions(self, topic: str) -> List[str]:
        """Get suggested follow-up topics or questions for deeper understanding."""
        suggestions = [
            f"Wie funktioniert {topic} in der Praxis?",
            f"Was sind die Vorteile von {topic}?",
            f"Welche Herausforderungen gibt es bei {topic}?",
            f"Wie unterscheidet sich {topic} von ähnlichen Konzepten?",
            f"Welche Tools oder Methoden nutzt man für {topic}?"
        ]
        return suggestions
    
    def create_learning_path(self, main_topic: str) -> Dict[str, List[str]]:
        """Create a structured learning path for a topic."""
        return {
            "Grundlagen": [
                f"Was ist {main_topic}?",
                f"Warum ist {main_topic} wichtig?",
                f"Grundlegende Konzepte von {main_topic}"
            ],
            "Vertiefung": [
                f"Wie funktioniert {main_topic} im Detail?",
                f"Praktische Anwendungen von {main_topic}",
                f"Tools und Technologien für {main_topic}"
            ],
            "Fortgeschritten": [
                f"Erweiterte Techniken in {main_topic}",
                f"Aktuelle Forschung zu {main_topic}",
                f"Zukunft von {main_topic}"
            ]
        }
