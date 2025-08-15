"""
User Interface components for the explAIner system.
Handles all Streamlit UI elements and user interactions for explAIner.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from .explainer_core import ExplainerCore
from .explainer_logger import ExplainerLogger
from .learning_goals_manager import LearningGoalsManager
from .quiz_system import QuizSystem
from .quiz_ui import QuizUI
from .prompts_config import LANGUAGE_CONFIG, PROMPT_CONFIG

class ExplainerUI:
    """User interface handler for the explAIner system."""
    
    def __init__(self, core: ExplainerCore, logger: ExplainerLogger):
        """Initialize the explAIner UI with core system and logger."""
        self.core = core
        self.logger = logger
        self.learning_goals_manager = LearningGoalsManager()
        self.quiz_system = QuizSystem()
        # Connect the learning goals manager to the quiz system
        self.quiz_system.learning_goals_manager = self.learning_goals_manager
        self.quiz_ui = QuizUI(self.quiz_system)
        
    def render_main_page(self, user_id: str, user_group: int):
        """Render the explAIner page - either checklist or learning flow."""
        # Render language selector at the top
        self._render_language_selector()
        
        # Check which page mode we're in
        page_mode = st.session_state.get("page_mode", "checklist")
        
        if page_mode == "learning_flow":
            self._render_learning_flow_page(user_id)
        else:
            self._render_checklist_page(user_id)
    
    def _render_checklist_page(self, user_id: str):
        """Render the main checklist page with learning goals."""
        language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        
        st.title("📚 Learning to Sigil")
        
        # Motivational intro text (multilingual)
        if language == "English":
            st.markdown("""
            ### These are the learning objectives you need for the final exam.
            
            🎯 **To successfully progress, you must achieve all learning objectives.**
            
            Mark each learning objective as completed once you have mastered it:
            """)
        else:
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
            button_text = "🚀 Start Learning Experience" if language == "English" else "🚀 Lernerfahrung starten"
            button_help = "Begin your structured learning journey through all learning objectives" if language == "English" else "Beginnen Sie Ihre strukturierte Lernreise durch alle Lernziele"
            
            if st.button(
                button_text, 
                key="start_learning_experience",
                help=button_help,
                use_container_width=True
            ):
                st.session_state.page_mode = "learning_flow"
                st.session_state.current_goal_index = 0
                st.session_state.learning_phase = "information"  # information, train, test
                # Scroll to top when navigating to learning flow
                st.session_state.scroll_to_top = True
                st.rerun()
    
    def _render_learning_flow_page(self, user_id: str):
        """Render the learning flow page with stepper and goal information."""
        # Scroll to top if requested
        if st.session_state.get("scroll_to_top", False):
            st.components.v1.html("""
                <script>
                    window.parent.document.querySelector('.main').scrollTo(0, 0);
                </script>
            """, height=0)
            st.session_state.scroll_to_top = False
        
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
        language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        col1, col2 = st.columns([1, 6])
        with col1:
            back_text = "← Back" if language == "English" else "← Zurück"
            if st.button(back_text, key="back_to_checklist"):
                st.session_state.page_mode = "checklist"
                st.rerun()
        
        with col2:
            title_text = f"🎯 Learning Goal {current_goal_index + 1}: {current_goal['description'][:50]}..." if language == "English" else f"🎯 Lernziel {current_goal_index + 1}: {current_goal['description'][:50]}..."
            st.title(title_text)
        
        # Stepper UI
        self._render_stepper(learning_phase)
        
        # Current phase content
        if learning_phase == "information":
            self._render_information_phase(current_goal, current_goal_index)
        elif learning_phase == "train":
            self._render_training_phase(current_goal, current_goal_index)
    
    def _render_stepper(self, current_phase: str):
        """Render the stepper UI showing the learning phases."""
        language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        
        if language == "English":
            phases = [
                ("information", "📚 Understand"),
                ("train", "🏋️ Training")
            ]
        else:
            phases = [
                ("information", "📚 Verstehen"),
                ("train", "🏋️ Training")
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
    
    def _render_language_selector(self):
        """Render language selector in the sidebar with professional flag images from Flags API."""
        with st.sidebar:
            st.markdown("### 🌐 Deutsch/ English")
            
            # Initialize selected language if not set
            if "selected_language" not in st.session_state:
                st.session_state.selected_language = PROMPT_CONFIG["default_language"]
            
            # Language selector with flag images from Flags API
            current_language = st.session_state.selected_language
            language_options = list(LANGUAGE_CONFIG.keys())
            
            # Create clickable language options with flag images
            for lang in language_options:
                config = LANGUAGE_CONFIG[lang]
                is_selected = lang == current_language
                flag_url = f"https://flagsapi.com/{config['country_code']}/flat/32.png"
                
                # Create clickable language option with flag image
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 5px;'>
                        <img src="{flag_url}" alt="{config['name']} flag" style="width: 32px; height: auto; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    button_style = "✓ " if is_selected else ""
                    if st.button(
                        f"{button_style}{config['name']}",
                        key=f"lang_btn_{lang}",
                        disabled=is_selected,
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.selected_language = lang
                        st.rerun()
            
            st.markdown("---")
    
    def _render_information_phase(self, current_goal: dict, goal_index: int):
        """Render the information gathering phase."""
        language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        
        title_text = f"### 📚 Information for Learning Goal {goal_index + 1}" if language == "English" else f"### 📚 Informationen für Lernziel {goal_index + 1}"
        st.markdown(title_text)
        
        # Load and display goal-specific information with images
        info_content = self._load_goal_information(goal_index + 1, language)
        
        if info_content:
            self._render_information_with_images(info_content, goal_index + 1, language)
        else:
            warning_text = "⚠️ Information for this learning goal could not be loaded." if language == "English" else "⚠️ Informationen für dieses Lernziel konnten nicht geladen werden."
            st.warning(warning_text)
        
        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            button_text = "➡️ Continue to Training" if language == "English" else "➡️ Weiter zum Training"
            if st.button(button_text, key="to_training", use_container_width=True):
                st.session_state.learning_phase = "train"
                st.rerun()
    
    def _render_training_phase(self, current_goal: dict, goal_index: int):
        """Render the training phase with interactive quiz for practice."""
        language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        
        # Get user ID from session state or generate one
        user_id = st.session_state.get("user_id", "anonymous")
        
        # Add training context
        title_text = f"### 🏋️ Training for Learning Goal {goal_index + 1}" if language == "English" else f"### 🏋️ Training für Lernziel {goal_index + 1}"
        st.markdown(title_text)
        
        info_text = "💡 **Training Mode:** Here you can practice and receive immediate feedback. Use this phase to deepen your understanding!" if language == "English" else "💡 **Trainingsmodus:** Hier können Sie üben und erhalten sofortiges Feedback. Nutzen Sie diese Phase, um Ihr Verständnis zu vertiefen!"
        st.info(info_text)
        
        # Render the quiz interface for training
        self.quiz_ui.render_quiz_interface(current_goal, goal_index, user_id)
        
        # Navigation buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            back_text = "← Back to Information" if language == "English" else "← Zurück zu Informationen"
            if st.button(back_text, key="back_to_info_from_training", use_container_width=True):
                st.session_state.learning_phase = "information"
                st.rerun()
        
        with col3:
            goals = self.learning_goals_manager.get_learning_goals()
            if goal_index + 1 < len(goals):
                next_goal_text = "➡️ Next Learning Goal" if language == "English" else "➡️ Nächstes Lernziel"
                if st.button(next_goal_text, key="next_goal_from_training", use_container_width=True):
                    st.session_state.current_goal_index += 1
                    st.session_state.learning_phase = "information"
                    st.rerun()
            else:
                complete_text = "🎉 Complete" if language == "English" else "🎉 Abschließen"
                if st.button(complete_text, key="complete_learning_from_training", use_container_width=True):
                    st.session_state.page_mode = "checklist"
                    success_text = "🎉 Congratulations! You have completed all learning goals!" if language == "English" else "🎉 Herzlichen Glückwunsch! Sie haben alle Lernziele durchlaufen!"
                    st.success(success_text)
                    st.rerun()
    

    
    def _load_goal_information(self, goal_number: int, language: str = None) -> str:
        """Load goal-specific information from markdown files in the selected language."""
        import os
        
        if not language:
            language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        
        # Map goal numbers to file names (with language suffix for English)
        if language == "English":
            goal_files = {
                1: "goal_1_components_en.md",
                2: "goal_2_functions_en.md", 
                3: "goal_3_assembly_en.md",
                4: "goal_4_analysis_en.md",
                5: "goal_5_evaluation_en.md"
            }
        else:
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
                # Fallback to German version if English doesn't exist
                if language == "English":
                    fallback_file = goal_files[goal_number].replace("_en.md", ".md")
                    fallback_path = os.path.join(project_root, "data", "information", fallback_file)
                    if os.path.exists(fallback_path):
                        with open(fallback_path, 'r', encoding='utf-8') as f:
                            return f.read()
                
                error_text = f"⚠️ Information file not found: {info_file_path}" if language == "English" else f"⚠️ Informationsdatei nicht gefunden: {info_file_path}"
                return error_text
        except Exception as e:
            error_text = f"❌ Error loading information: {str(e)}" if language == "English" else f"❌ Fehler beim Laden der Informationen: {str(e)}"
            return error_text
    
    def _render_information_with_images(self, content: str, goal_number: int, language: str):
        """Render information content with appropriate images inserted at relevant sections."""
        import os
        
        # Split content into sections
        lines = content.split('\n')
        current_section = []
        
        for line in lines:
            current_section.append(line)
            
            # Check if we should insert an image after this line
            if goal_number == 1:  # For goal 1 (components)
                if "## 2. Population Frame" in line or "## 2. Bevölkerungsrahmen" in line:
                    # Render current section
                    st.markdown('\n'.join(current_section))
                    current_section = []
                    
                    # Show population frame examples
                    self._show_component_images("population_frame", language)
                    
                elif "## 3. Capital Crown" in line or "## 3. Hauptstadtkrone" in line:
                    # Render current section
                    st.markdown('\n'.join(current_section))
                    current_section = []
                    
                    # Show capital crown examples
                    self._show_component_images("capital_crown", language)
                    
                elif "## 4. Orientation Circle" in line or "## 4. Orientierungskreis" in line:
                    # Render current section
                    st.markdown('\n'.join(current_section))
                    current_section = []
                    
                    # Show orientation circle examples
                    self._show_component_images("orientation_location_circle", language)
                    
                elif "## 1. State Background" in line or "## 1. Bundeslandshintergrund" in line:
                    # Render current section
                    st.markdown('\n'.join(current_section))
                    current_section = []
                    
                    # Show state background examples
                    self._show_component_images("state_background", language)
        
        # Render any remaining content
        if current_section:
            st.markdown('\n'.join(current_section))
    
    def _show_component_images(self, component_type: str, language: str):
        """Show relevant images for a specific component type."""
        import os
        
        # Get project root
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        component_dir = os.path.join(project_root, "data", "sigil_components", component_type)
        
        if not os.path.exists(component_dir):
            return
        
        # Define which images to show for each component type
        if component_type == "population_frame":
            if language == "English":
                st.markdown("**Examples of Population Frames:**")
                images_to_show = [
                    ("medium_city.png", "Cities with less than 500,000 inhabitants (single-colored border)"),
                    ("large_city.png", "Cities with 500,000 to 1 million inhabitants (two-colored border with elevations)"),
                    ("mega_city.png", "Cities with over 1 million inhabitants (two-colored border with green spikes)")
                ]
            else:
                st.markdown("**Beispiele für Bevölkerungsrahmen:**")
                images_to_show = [
                    ("medium_city.png", "Städte mit weniger als 500.000 Einwohnern (einfarbiger Rand)"),
                    ("large_city.png", "Städte mit 500.000 bis 1 Million Einwohnern (zweifarbiger Rand mit Erhebungen)"),
                    ("mega_city.png", "Städte mit über 1 Million Einwohnern (zweifarbiger Rand mit grünen Spitzen)")
                ]
        
        elif component_type == "capital_crown":
            if language == "English":
                st.markdown("**Examples of Capital Crowns:**")
                images_to_show = [
                    ("federal_capital.png", "Federal capitals: Crown with two underlines in inverted German flag colors"),
                    ("state_capital.png", "State capitals: Crown with red underline"),
                    ("former_federal_capital.png", "Former federal capital (Bonn): Crown only")
                ]
            else:
                st.markdown("**Beispiele für Hauptstadtkronen:**")
                images_to_show = [
                    ("federal_capital.png", "Bundeshauptstädte: Krone mit zwei Unterstrichen in umgekehrten deutschen Flaggenfarben"),
                    ("state_capital.png", "Landeshauptstädte: Krone mit rotem Unterstrich"),
                    ("former_federal_capital.png", "Ehemalige Bundeshauptstadt (Bonn): Ausschließlich die Krone")
                ]
        
        elif component_type == "orientation_location_circle":
            if language == "English":
                st.markdown("**Examples of Location Circles:**")
                images_to_show = [
                    ("north.png", "Northern location"),
                    ("central.png", "Central location"),
                    ("city_state.png", "City-state (completely yellow-filled circle)")
                ]
            else:
                st.markdown("**Beispiele für Lagekreise:**")
                images_to_show = [
                    ("north.png", "Nördliche Lage"),
                    ("central.png", "Zentrale Lage"),
                    ("city_state.png", "Stadtstaat (komplett gelb gefüllter Kreis)")
                ]
        
        elif component_type == "state_background":
            if language == "English":
                st.markdown("**Examples of State Backgrounds:**")
                images_to_show = [
                    ("Bayern.png", "Bavaria (blue-white)"),
                    ("Berlin.png", "Berlin (red-white)"),
                    ("Baden-Württemberg.png", "Baden-Württemberg (black-yellow)")
                ]
            else:
                st.markdown("**Beispiele für Bundeslandshintergründe:**")
                images_to_show = [
                    ("Bayern.png", "Bayern (blau-weiß)"),
                    ("Berlin.png", "Berlin (rot-weiß)"),
                    ("Baden-Württemberg.png", "Baden-Württemberg (schwarz-gelb)")
                ]
        
        # Display images in columns
        cols = st.columns(len(images_to_show))
        for i, (image_file, description) in enumerate(images_to_show):
            image_path = os.path.join(component_dir, image_file)
            if os.path.exists(image_path):
                with cols[i]:
                    st.image(image_path, caption=description, use_container_width=True)
        
        st.markdown("---")
    
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
                    f"Mark learning goal {goal_id} as completed", 
                    value=is_completed,
                    key=f"goal_checkbox_{goal_id}",
                    label_visibility="collapsed"
                )
                
                # Update progress if changed
                if new_status != is_completed:
                    self.learning_goals_manager.update_goal_progress(user_id, goal_id, new_status)
                    st.rerun()
            
            with col2:
                # Goal description with status indicator and strikethrough for completed
                if new_status:
                    status_icon = "✅"
                    # Use strikethrough for completed goals
                    st.markdown(f"{status_icon} ~~**{goal['description']}**~~")
                else:
                    status_icon = "⭕"
                    st.markdown(f"{status_icon} **{goal['description']}**")
            
            if new_status:
                completed_count += 1
        
        st.markdown("---")
        
        # Progress summary and motivational message
        total_goals = len(goals)
        progress_percentage = (completed_count / total_goals) * 100 if total_goals > 0 else 0
        
        # Progress bar
        language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        st.progress(progress_percentage / 100)
        
        if language == "English":
            st.markdown(f"**Progress: {completed_count}/{total_goals} Learning Goals achieved ({progress_percentage:.0f}%)**")
        else:
            st.markdown(f"**Fortschritt: {completed_count}/{total_goals} Lernziele erreicht ({progress_percentage:.0f}%)**")
        
        # Motivational messages based on progress
        if completed_count == 0:
            if language == "English":
                st.info("🚀 **Start with the first learning goal!** Every step brings you closer to success.")
            else:
                st.info("🚀 **Beginnen Sie mit dem ersten Lernziel!** Jeder Schritt bringt Sie näher zum Erfolg.")
        elif completed_count < total_goals:
            remaining = total_goals - completed_count
            if language == "English":
                plural = "s" if remaining > 1 else ""
                st.info(f"💪 **Great! {remaining} more learning goal{plural} to completion!** You're on the right track.")
            else:
                st.info(f"💪 **Großartig! Noch {remaining} Lernziel{'e' if remaining > 1 else ''} bis zum Abschluss!** Sie sind auf dem richtigen Weg.")
        else:
            if language == "English":
                st.success("🎉 **Congratulations!** You have achieved all learning goals and can take the exam!")
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
