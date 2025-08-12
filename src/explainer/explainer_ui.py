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
        """Render the explAIner page - either checklist or learning flow."""
        # Check which page mode we're in
        page_mode = st.session_state.get("page_mode", "checklist")
        
        if page_mode == "learning_flow":
            self._render_learning_flow_page(user_id)
        else:
            self._render_checklist_page(user_id)
    
    def _render_checklist_page(self, user_id: str):
        """Render the main checklist page with learning goals."""
        st.title("📚 Learning to Sigil")
        
        # Motivational intro text
        st.markdown("""
        ### Das sind die Lernziele, die Sie für die Abschlussprüfung benötigen.
        
        🎯 **Um erfolgreich voranzukommen, müssen Sie alle Lernziele erreichen.**
        
        Markieren Sie jedes Lernziel als erreicht, sobald Sie es beherrschen:
        """)
        
        # Display learning goals checklist
        self._render_learning_goals_checklist(user_id)
        
        # Add learning experience button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "🚀 Lernerfahrung starten", 
                key="start_learning_experience",
                help="Beginnen Sie Ihre strukturierte Lernreise durch alle Lernziele",
                use_container_width=True
            ):
                st.session_state.page_mode = "learning_flow"
                st.session_state.current_goal_index = 0
                st.session_state.learning_phase = "information"  # information, train, test
                st.rerun()
    
    def _render_learning_flow_page(self, user_id: str):
        """Render the learning flow page with stepper and goal information."""
        # Get current state
        current_goal_index = st.session_state.get("current_goal_index", 0)
        learning_phase = st.session_state.get("learning_phase", "information")
        
        # Get learning goals
        goals = self.learning_goals_manager.get_learning_goals()
        if not goals or current_goal_index >= len(goals):
            st.error("⚠️ Fehler beim Laden der Lernziele.")
            return
        
        current_goal = goals[current_goal_index]
        
        # Header with back button
        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("← Zurück", key="back_to_checklist"):
                st.session_state.page_mode = "checklist"
                st.rerun()
        
        with col2:
            st.title(f"🎯 Lernziel {current_goal_index + 1}: {current_goal['description'][:50]}...")
        
        # Stepper UI
        self._render_stepper(learning_phase)
        
        # Current phase content
        if learning_phase == "information":
            self._render_information_phase(current_goal, current_goal_index)
        elif learning_phase == "train":
            self._render_training_phase(current_goal, current_goal_index)
        elif learning_phase == "test":
            self._render_test_phase(current_goal, current_goal_index)
    
    def _render_stepper(self, current_phase: str):
        """Render the stepper UI showing the learning phases."""
        phases = [
            ("information", "📚 Informationen sammeln"),
            ("train", "🏋️ Trainieren"),
            ("test", "📋 Testen")
        ]
        
        # Create stepper visualization
        cols = st.columns(len(phases))
        
        for i, (phase_key, phase_name) in enumerate(phases):
            with cols[i]:
                if phase_key == current_phase:
                    # Current phase - highlighted
                    st.markdown(f"""
                    <div style="
                        background-color: #1f77b4;
                        color: white;
                        padding: 10px;
                        border-radius: 5px;
                        text-align: center;
                        font-weight: bold;
                    ">
                        {phase_name}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Other phases - muted
                    st.markdown(f"""
                    <div style="
                        background-color: #f0f0f0;
                        color: #666;
                        padding: 10px;
                        border-radius: 5px;
                        text-align: center;
                    ">
                        {phase_name}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    def _render_information_phase(self, current_goal: dict, goal_index: int):
        """Render the information gathering phase."""
        st.markdown(f"### 📚 Informationen für Lernziel {goal_index + 1}")
        
        # Load and display goal-specific information
        info_content = self._load_goal_information(goal_index + 1)
        
        if info_content:
            st.markdown(info_content)
        else:
            st.warning("⚠️ Informationen für dieses Lernziel konnten nicht geladen werden.")
        
        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("➡️ Weiter zum Training", key="to_training", use_container_width=True):
                st.session_state.learning_phase = "train"
                st.rerun()
    
    def _render_training_phase(self, current_goal: dict, goal_index: int):
        """Render the training phase."""
        st.markdown(f"### 🏋️ Training für Lernziel {goal_index + 1}")
        st.info("🚧 Trainingsbereich wird in einer zukünftigen Version implementiert.")
        
        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Zurück zu Informationen", key="back_to_info", use_container_width=True):
                st.session_state.learning_phase = "information"
                st.rerun()
        
        with col3:
            if st.button("➡️ Weiter zum Test", key="to_test", use_container_width=True):
                st.session_state.learning_phase = "test"
                st.rerun()
    
    def _render_test_phase(self, current_goal: dict, goal_index: int):
        """Render the test phase."""
        st.markdown(f"### 📋 Test für Lernziel {goal_index + 1}")
        st.info("🚧 Testbereich wird in einer zukünftigen Version implementiert.")
        
        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Zurück zum Training", key="back_to_training", use_container_width=True):
                st.session_state.learning_phase = "train"
                st.rerun()
        
        with col3:
            goals = self.learning_goals_manager.get_learning_goals()
            if goal_index + 1 < len(goals):
                if st.button("➡️ Nächstes Lernziel", key="next_goal", use_container_width=True):
                    st.session_state.current_goal_index += 1
                    st.session_state.learning_phase = "information"
                    st.rerun()
            else:
                if st.button("🎉 Abschließen", key="complete_learning", use_container_width=True):
                    st.session_state.page_mode = "checklist"
                    st.success("🎉 Herzlichen Glückwunsch! Sie haben alle Lernziele durchlaufen!")
                    st.rerun()
    
    def _load_goal_information(self, goal_number: int) -> str:
        """Load goal-specific information from markdown files."""
        import os
        
        # Map goal numbers to file names
        goal_files = {
            1: "goal_1_components.md",
            2: "goal_2_functions.md", 
            3: "goal_3_assembly.md",
            4: "goal_4_analysis.md",
            5: "goal_5_evaluation.md"
        }
        
        if goal_number not in goal_files:
            return None
        
        # Construct file path
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        info_file_path = os.path.join(project_root, "data", "information", goal_files[goal_number])
        
        try:
            if os.path.exists(info_file_path):
                with open(info_file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"⚠️ Informationsdatei nicht gefunden: {info_file_path}"
        except Exception as e:
            return f"❌ Fehler beim Laden der Informationen: {str(e)}"
    
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
