"""
User Interface components for the explAIner system.
Handles all Streamlit UI elements and user interactions for explAIner.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from .explainer_core import ExplainerCore
from .explainer_logger import ExplainerLogger
from .learning_goals_manager import LearningGoalsManager

class ExplainerUI:
    """User interface handler for the explAIner system."""
    
    def __init__(self, core: ExplainerCore, logger: ExplainerLogger):
        """Initialize the explAIner UI with core system and logger."""
        self.core = core
        self.logger = logger
        self.learning_goals_manager = LearningGoalsManager()
        
    def render_main_page(self, user_id: str, user_group: int):
        """Render the simplified explAIner page with learning goals checklist."""
        st.title("📚 Learning to Sigil")
        
        # Motivational intro text
        st.markdown("""
        ### Das sind die Lernziele, die Sie für die Abschlussprüfung benötigen.
        
        🎯 **Um erfolgreich voranzukommen, müssen Sie alle Lernziele erreichen.**
        
        Markieren Sie jedes Lernziel als erreicht, sobald Sie es beherrschen:
        """)
        
        # Display learning goals checklist
        self._render_learning_goals_checklist(user_id)
    
    def _render_learning_goals_checklist(self, user_id: str):
        """Render the learning goals as an interactive checklist."""
        # Load learning goals from markdown file
        goals = self.learning_goals_manager.get_learning_goals()
        
        if not goals:
            st.warning("⚠️ Lernziele konnten nicht geladen werden.")
            return
        
        # Get current progress
        progress = self.learning_goals_manager.get_user_progress(user_id)
        
        # Display each learning goal as a checkbox
        st.markdown("---")
        
        completed_count = 0
        for goal in goals:
            goal_id = goal['id']
            is_completed = progress.get(goal_id, False)
            
            # Create checkbox for each goal
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                # Checkbox
                new_status = st.checkbox(
                    "", 
                    value=is_completed,
                    key=f"goal_checkbox_{goal_id}",
                    label_visibility="collapsed"
                )
                
                # Update progress if changed
                if new_status != is_completed:
                    self.learning_goals_manager.update_goal_progress(user_id, goal_id, new_status)
                    st.rerun()
            
            with col2:
                # Goal description with status indicator
                status_icon = "✅" if new_status else "⭕"
                st.markdown(f"{status_icon} **{goal['description']}**")
            
            if new_status:
                completed_count += 1
        
        st.markdown("---")
        
        # Progress summary and motivational message
        total_goals = len(goals)
        progress_percentage = (completed_count / total_goals) * 100 if total_goals > 0 else 0
        
        # Progress bar
        st.progress(progress_percentage / 100)
        st.markdown(f"**Fortschritt: {completed_count}/{total_goals} Lernziele erreicht ({progress_percentage:.0f}%)**")
        
        # Motivational messages based on progress
        if completed_count == 0:
            st.info("🚀 **Beginnen Sie mit dem ersten Lernziel!** Jeder Schritt bringt Sie näher zum Erfolg.")
        elif completed_count < total_goals:
            remaining = total_goals - completed_count
            st.info(f"💪 **Großartig! Noch {remaining} Lernziel{'e' if remaining > 1 else ''} bis zum Abschluss!** Sie sind auf dem richtigen Weg.")
        else:
            st.success("🎉 **Herzlichen Glückwunsch!** Sie haben alle Lernziele erreicht und können zur Prüfung antreten!")
            st.balloons()
        
    def _render_learning_goals_tab(self, user_id: str) -> None:
        """Render the learning goals tracking interface."""
        # Show next goal suggestion at the top
        self.learning_goals_manager.render_next_goal_suggestion(user_id)
        
        st.divider()
        
        # Main learning goals overview
        self.learning_goals_manager.render_learning_goals_overview(user_id)
        
        # Add some helpful tips
        st.divider()
        
        with st.expander("💡 Tipps zum Erreichen der Lernziele"):
            st.markdown("""
            **So erreichen Sie Ihre Lernziele effektiv:**
            
            1. **📖 Verstehen Sie das Ziel**: Lesen Sie die Beschreibung jedes Lernziels sorgfältig durch
            2. **🔍 Nutzen Sie die Erklärungen**: Verwenden Sie den "Erklärung anfordern" Tab für schwierige Konzepte
            3. **📚 Folgen Sie dem Lernpfad**: Der strukturierte Lernpfad hilft beim systematischen Lernen
            4. **💡 Probieren Sie Beispiele**: Praktische Beispiele vertiefen das Verständnis
            5. **✅ Markieren Sie erreichte Ziele**: Seien Sie ehrlich bei der Selbsteinschätzung
            
            **Tipp**: Arbeiten Sie die Lernziele der Reihe nach ab - sie bauen aufeinander auf!
            """)
    
    def _render_explanation_tab(self, user_id: str) -> None:
        """Render the explanation request interface."""
        st.subheader("🔍 AI-Konzept erklären lassen")
        
        # Input form
        with st.form("explanation_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                topic = st.text_input(
                    "Was möchten Sie erklärt bekommen?",
                    placeholder="z.B. Machine Learning, Neural Networks, RAG System..."
                )
            
            with col2:
                explanation_type = st.selectbox(
                    "Erklärungstyp:",
                    options=list(self.core.explanation_types.keys()),
                    format_func=lambda x: self.core.explanation_types[x]
                )
            
            complexity_level = st.select_slider(
                "Komplexitätslevel:",
                options=["beginner", "intermediate", "advanced"],
                value="intermediate",
                format_func=lambda x: {
                    "beginner": "🟢 Anfänger", 
                    "intermediate": "🟡 Fortgeschritten", 
                    "advanced": "🔴 Experte"
                }[x]
            )
            
            submitted = st.form_submit_button("✨ Erklärung generieren", type="primary")
        
        if submitted and topic:
            with st.spinner("🤖 Generiere Erklärung..."):
                result = self.core.generate_explanation(topic, explanation_type, complexity_level)
                
                # Log the request
                self.logger.log_explanation_request(
                    user_id=user_id,
                    topic=topic,
                    explanation_type=explanation_type,
                    complexity_level=complexity_level,
                    success=result["success"]
                )
                
                if result["success"]:
                    st.success("✅ Erklärung generiert!")
                    
                    # Display explanation
                    st.markdown("### 📖 Erklärung:")
                    st.markdown(result["explanation"])
                    
                    # Show metadata
                    with st.expander("ℹ️ Details zur Erklärung"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Typ", self.core.explanation_types[result["type"]])
                        with col2:
                            st.metric("Level", result["complexity"])
                        with col3:
                            st.metric("Tokens", result["tokens_used"])
                    
                    # Suggestions for follow-up
                    st.markdown("### 💡 Weiterführende Fragen:")
                    suggestions = self.core.get_explanation_suggestions(topic)
                    for i, suggestion in enumerate(suggestions[:3]):
                        if st.button(f"❓ {suggestion}", key=f"suggestion_{i}"):
                            st.session_state.suggested_topic = suggestion
                            st.rerun()
                            
                else:
                    st.error(f"❌ Fehler bei der Erklärungsgenerierung: {result['error']}")
    
    def _render_learning_path_tab(self, user_id: str) -> None:
        """Render the learning path interface."""
        st.subheader("📚 Strukturierter Lernpfad")
        
        topic = st.text_input(
            "Für welches Thema möchten Sie einen Lernpfad erstellen?",
            placeholder="z.B. Künstliche Intelligenz, Deep Learning..."
        )
        
        if st.button("🗺️ Lernpfad erstellen") and topic:
            learning_path = self.core.create_learning_path(topic)
            
            # Log learning path creation
            self.logger.log_learning_path_request(user_id, topic)
            
            st.markdown(f"### 🎯 Lernpfad für: {topic}")
            
            for level, topics in learning_path.items():
                with st.expander(f"📖 {level}", expanded=True):
                    for i, subtopic in enumerate(topics, 1):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"{i}. {subtopic}")
                        with col2:
                            if st.button("🔍", key=f"learn_{level}_{i}", help="Erklärung anfordern"):
                                # Set topic for explanation
                                st.session_state.explanation_topic = subtopic
                                st.switch_page("🔍 Erklärung anfordern")
    
    def _render_examples_tab(self) -> None:
        """Render the examples showcase."""
        st.subheader("💡 Beispiele und Anwendungsfälle")
        
        examples = {
            "Machine Learning": {
                "description": "Grundlagen des maschinellen Lernens",
                "complexity": "intermediate",
                "type": "concept"
            },
            "Neural Networks": {
                "description": "Wie neuronale Netzwerke funktionieren",
                "complexity": "advanced", 
                "type": "process"
            },
            "RAG vs. Fine-tuning": {
                "description": "Vergleich verschiedener AI-Ansätze",
                "complexity": "intermediate",
                "type": "comparison"
            },
            "Chatbot Implementierung": {
                "description": "Praktisches Beispiel eines Chatbots",
                "complexity": "beginner",
                "type": "example"
            }
        }
        
        st.markdown("Klicken Sie auf ein Beispiel, um eine Erklärung zu erhalten:")
        
        cols = st.columns(2)
        for i, (topic, details) in enumerate(examples.items()):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"**{topic}**")
                    st.markdown(f"_{details['description']}_")
                    
                    complexity_color = {
                        "beginner": "🟢",
                        "intermediate": "🟡", 
                        "advanced": "🔴"
                    }
                    
                    st.markdown(f"{complexity_color[details['complexity']]} {details['complexity'].title()}")
                    
                    if st.button(f"📖 Erklären", key=f"example_{i}"):
                        st.session_state.example_topic = topic
                        st.session_state.example_type = details['type']
                        st.session_state.example_complexity = details['complexity']
                        st.rerun()
        
        # Handle example selection
        if hasattr(st.session_state, 'example_topic'):
            with st.spinner("🤖 Generiere Beispiel-Erklärung..."):
                result = self.core.generate_explanation(
                    st.session_state.example_topic,
                    st.session_state.example_type,
                    st.session_state.example_complexity
                )
                
                if result["success"]:
                    st.markdown("---")
                    st.markdown(f"### 📖 Erklärung: {st.session_state.example_topic}")
                    st.markdown(result["explanation"])
                
                # Clear session state
                del st.session_state.example_topic
                del st.session_state.example_type
                del st.session_state.example_complexity
    
    def _render_activity_tab(self, user_id: str) -> None:
        """Render user activity and statistics."""
        st.subheader("📊 Ihre explAIner Aktivität")
        
        # Learning Goals Progress Summary
        st.markdown("### 🎯 Lernfortschritt")
        self.learning_goals_manager.render_progress_summary(user_id)
        
        st.divider()
        
        # Get user statistics from logger
        stats = self.logger.get_user_statistics(user_id)
        learning_stats = self.learning_goals_manager.get_progress_statistics(user_id)
        
        st.markdown("### 📊 Aktivitätsstatistiken")
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔍 Erklärungen", stats.get("total_explanations", 0))
            
            with col2:
                st.metric("📚 Lernpfade", stats.get("learning_paths", 0))
            
            with col3:
                st.metric("⏱️ Aktive Zeit", f"{stats.get('session_time', 0)} min")
            
            with col4:
                st.metric("🎯 Lernziele", f"{learning_stats['completed_goals']}/{learning_stats['total_goals']}")
            
            # Recent activity
            st.markdown("### 📝 Letzte Aktivitäten")
            recent_activities = self.logger.get_recent_activities(user_id, limit=5)
            
            if recent_activities:
                for activity in recent_activities:
                    with st.expander(f"🕐 {activity['timestamp']} - {activity['type']}"):
                        st.json(activity)
            else:
                st.info("Noch keine Aktivitäten aufgezeichnet.")
        else:
            st.info("Noch keine Statistiken verfügbar. Nutzen Sie das explAIner System, um Daten zu sammeln!")
