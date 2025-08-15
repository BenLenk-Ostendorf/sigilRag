"""
User Interface components for the quiz system.
Handles rendering of different question types and user interactions.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from .quiz_system import QuizSystem

class QuizUI:
    """User interface handler for the quiz system."""
    
    def __init__(self, quiz_system: QuizSystem):
        """Initialize the quiz UI with the quiz system."""
        self.quiz_system = quiz_system
    
    def render_quiz_interface(self, learning_goal: dict, goal_index: int, user_id: str):
        """Render the main quiz interface for a learning goal."""
        language = st.session_state.get("selected_language", "German")
        
        title_text = f"### 🧠 Quiz for Learning Goal {goal_index + 1}" if language == "English" else f"### 🧠 Quiz für Lernziel {goal_index + 1}"
        st.markdown(title_text)
        
        unknown_goal_text = "Unknown Learning Goal" if language == "English" else "Unbekanntes Lernziel"
        st.markdown(f"**{learning_goal.get('description', unknown_goal_text)}**")
        
        # Initialize session state for this quiz
        quiz_key = f"quiz_{goal_index}"
        if quiz_key not in st.session_state:
            st.session_state[quiz_key] = {
                "current_question": None,
                "answered": False,
                "feedback": None,
                "attempts": 0,
                "correct_answers": 0
            }
        
        quiz_state = st.session_state[quiz_key]
        
        # Generate new question if needed
        if quiz_state["current_question"] is None or not quiz_state["answered"]:
            if quiz_state["current_question"] is None:
                # Get selected language
                language = st.session_state.get("selected_language", "German")
                spinner_text = "Generating question based on learning material..." if language == "English" else "Generiere Frage basierend auf Lernmaterial..."
                with st.spinner(spinner_text):
                    quiz_state["current_question"] = self.quiz_system.generate_quiz_question(learning_goal, goal_index=goal_index, language=language)
        
        # Display current question
        if quiz_state["current_question"]:
            self._render_question(quiz_state["current_question"], quiz_key)
        
        # Show feedback if answered
        if quiz_state["answered"] and quiz_state["feedback"]:
            self._render_feedback(quiz_state["feedback"])
            
            # Show progress
            if quiz_state["attempts"] > 0:
                accuracy = (quiz_state["correct_answers"] / quiz_state["attempts"]) * 100
                language = st.session_state.get("selected_language", "German")
                progress_text = f"**Progress:** {quiz_state['correct_answers']}/{quiz_state['attempts']} correct ({accuracy:.0f}%)" if language == "English" else f"**Fortschritt:** {quiz_state['correct_answers']}/{quiz_state['attempts']} richtig ({accuracy:.0f}%)"
                st.markdown(progress_text)
            
            # Action buttons after feedback
            self._render_post_feedback_actions(quiz_key, goal_index)
    
    def _render_question(self, question_data: Dict[str, Any], quiz_key: str):
        """Render a question based on its type."""
        question_type = question_data.get("question_type", "multiple_choice")
        
        # Legacy automatic image display removed to increase quiz difficulty
        
        if question_type == "multiple_choice":
            self._render_multiple_choice(question_data, quiz_key)
        else:
            language = st.session_state.get("selected_language", "German")
            error_text = f"Unknown question type: {question_type}" if language == "English" else f"Unbekannter Fragetyp: {question_type}"
            st.error(error_text)
    
    def _render_multiple_choice(self, question_data: Dict[str, Any], quiz_key: str):
        """Render a multiple choice question."""
        language = st.session_state.get("selected_language", "German")
        
        header_text = "#### 🔘 Multiple Choice"
        st.markdown(header_text)
        
        no_question_text = "No question available" if language == "English" else "Keine Frage verfügbar"
        question_text = question_data.get("question", no_question_text)
        
        # Parse and render question with image placeholders
        self._render_question_with_placeholders(question_text)
        
        options = question_data.get("options", [])
        if not options:
            error_text = "No answer options available" if language == "English" else "Keine Antwortmöglichkeiten verfügbar"
            st.error(error_text)
            return
        
        # Radio button for answer selection
        answer_key = f"{quiz_key}_mc_answer"
        radio_label = "Choose an answer:" if language == "English" else "Wählen Sie eine Antwort:"
        selected_option = st.radio(
            radio_label,
            range(len(options)),
            format_func=lambda x: f"{chr(65+x)}. {options[x]}",
            key=answer_key
        )
        
        # Submit button
        submit_text = "Submit Answer" if language == "English" else "Antwort einreichen"
        if st.button(submit_text, key=f"{quiz_key}_submit"):
            self._submit_answer(quiz_key, selected_option)
    

    
    def _render_question_images(self, question_data: Dict[str, Any]):
        """Display relevant images for quiz questions based on question content."""
        import os
        
        # Get question text to analyze for relevant components
        question_text = question_data.get("question", "").lower()
        language = st.session_state.get("selected_language", "German")
        
        # Get project root for image paths
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Determine which images to show based on question content
        images_to_show = []
        
        # Check for population frame related content
        if any(keyword in question_text for keyword in ["population", "bevölkerung", "einwohner", "frame", "rahmen", "border", "rand"]):
            component_dir = os.path.join(project_root, "data", "sigil_components", "population_frame")
            if language == "English":
                images_to_show.extend([
                    (os.path.join(component_dir, "medium_city.png"), "Medium city (< 500k inhabitants)"),
                    (os.path.join(component_dir, "large_city.png"), "Large city (500k-1M inhabitants)"),
                    (os.path.join(component_dir, "mega_city.png"), "Mega city (> 1M inhabitants)")
                ])
            else:
                images_to_show.extend([
                    (os.path.join(component_dir, "medium_city.png"), "Mittelstadt (< 500k Einwohner)"),
                    (os.path.join(component_dir, "large_city.png"), "Großstadt (500k-1M Einwohner)"),
                    (os.path.join(component_dir, "mega_city.png"), "Megastadt (> 1M Einwohner)")
                ])
        
        # Check for capital crown related content
        if any(keyword in question_text for keyword in ["capital", "hauptstadt", "crown", "krone", "federal", "bundes", "state", "landes"]):
            component_dir = os.path.join(project_root, "data", "sigil_components", "capital_crown")
            if language == "English":
                images_to_show.extend([
                    (os.path.join(component_dir, "federal_capital.png"), "Federal capital crown"),
                    (os.path.join(component_dir, "state_capital.png"), "State capital crown"),
                    (os.path.join(component_dir, "former_federal_capital.png"), "Former federal capital (Bonn)")
                ])
            else:
                images_to_show.extend([
                    (os.path.join(component_dir, "federal_capital.png"), "Bundeshauptstadt-Krone"),
                    (os.path.join(component_dir, "state_capital.png"), "Landeshauptstadt-Krone"),
                    (os.path.join(component_dir, "former_federal_capital.png"), "Ehemalige Bundeshauptstadt (Bonn)")
                ])
        
        # Check for location/orientation circle related content
        if any(keyword in question_text for keyword in ["location", "lage", "orientation", "orientierung", "circle", "kreis", "direction", "richtung", "north", "nord", "south", "süd"]):
            component_dir = os.path.join(project_root, "data", "sigil_components", "orientation_location_circle")
            if language == "English":
                images_to_show.extend([
                    (os.path.join(component_dir, "north.png"), "Northern location"),
                    (os.path.join(component_dir, "central.png"), "Central location"),
                    (os.path.join(component_dir, "city_state.png"), "City-state location")
                ])
            else:
                images_to_show.extend([
                    (os.path.join(component_dir, "north.png"), "Nördliche Lage"),
                    (os.path.join(component_dir, "central.png"), "Zentrale Lage"),
                    (os.path.join(component_dir, "city_state.png"), "Stadtstaat-Lage")
                ])
        
        # Check for state background related content
        if any(keyword in question_text for keyword in ["state", "bundesland", "background", "hintergrund", "color", "farbe", "bavaria", "bayern", "berlin"]):
            component_dir = os.path.join(project_root, "data", "sigil_components", "state_background")
            if language == "English":
                images_to_show.extend([
                    (os.path.join(component_dir, "Bayern.png"), "Bavaria state background"),
                    (os.path.join(component_dir, "Berlin.png"), "Berlin state background"),
                    (os.path.join(component_dir, "Baden-Württemberg.png"), "Baden-Württemberg state background")
                ])
            else:
                images_to_show.extend([
                    (os.path.join(component_dir, "Bayern.png"), "Bayern Bundeslandshintergrund"),
                    (os.path.join(component_dir, "Berlin.png"), "Berlin Bundeslandshintergrund"),
                    (os.path.join(component_dir, "Baden-Württemberg.png"), "Baden-Württemberg Bundeslandshintergrund")
                ])
        
        # Display images if any were found
        if images_to_show:
            # Limit to maximum 3 images to avoid overwhelming the UI
            images_to_show = images_to_show[:3]
            
            if language == "English":
                st.markdown("**Reference Images:**")
            else:
                st.markdown("**Referenzbilder:**")
            
            cols = st.columns(len(images_to_show))
            for i, (image_path, caption) in enumerate(images_to_show):
                if os.path.exists(image_path):
                    with cols[i]:
                        st.image(image_path, caption=caption, use_container_width=True)
            
            st.markdown("---")
    
    def _render_question_with_placeholders(self, question_text: str):
        """Parse and render question text with image placeholders."""
        import re
        import os
        
        # Get project root for image paths
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Find all image placeholders in the format {{IMAGE:path/filename.png}}
        image_pattern = r'\{\{IMAGE:([^}]+)\}\}'
        matches = re.findall(image_pattern, question_text)
        
        # First, render any images found
        for image_path_relative in matches:
            image_path = os.path.join(project_root, "data", "sigil_components", image_path_relative)
            if os.path.exists(image_path):
                # Display image in a centered column without caption to increase difficulty
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(image_path, use_container_width=True)
            else:
                # Image not found, show placeholder
                language = st.session_state.get("selected_language", "German")
                error_text = f"⚠️ Image not found: {image_path_relative}" if language == "English" else f"⚠️ Bild nicht gefunden: {image_path_relative}"
                st.warning(error_text)
        
        # Then, render the question text with all image placeholders removed
        clean_text = re.sub(image_pattern, '', question_text)
        clean_text = clean_text.strip()
        
        if clean_text:
            st.markdown(clean_text)
    
    def _get_image_caption_from_path(self, component_type: str, filename: str) -> str:
        """Generate a caption for an image based on its component type and filename."""
        language = st.session_state.get("selected_language", "German")
        
        # Use the same descriptions as in prompts_config.py
        if language == "English":
            descriptions = {
                "population_frame": {
                    "medium_city.png": "Medium city population frame",
                    "large_city.png": "Large city population frame", 
                    "mega_city.png": "Mega city population frame"
                },
                "capital_crown": {
                    "federal_capital.png": "Federal capital crown",
                    "state_capital.png": "State capital crown",
                    "former_federal_capital.png": "Former federal capital crown"
                },
                "orientation_location_circle": {
                    "north.png": "Northern location circle",
                    "south.png": "Southern location circle",
                    "east.png": "Eastern location circle",
                    "west.png": "Western location circle",
                    "northeast.png": "Northeastern location circle",
                    "northwest.png": "Northwestern location circle",
                    "southeast.png": "Southeastern location circle",
                    "southwest.png": "Southwestern location circle",
                    "central.png": "Central location circle",
                    "city_state.png": "City-state location circle"
                },
                "state_background": {
                    "Bayern.png": "Bavaria state background",
                    "Berlin.png": "Berlin state background",
                    "Baden-Württemberg.png": "Baden-Württemberg state background"
                }
            }
        else:
            descriptions = {
                "population_frame": {
                    "medium_city.png": "Mittelstadt Bevölkerungsrahmen",
                    "large_city.png": "Großstadt Bevölkerungsrahmen", 
                    "mega_city.png": "Megastadt Bevölkerungsrahmen"
                },
                "capital_crown": {
                    "federal_capital.png": "Bundeshauptstadt Krone",
                    "state_capital.png": "Landeshauptstadt Krone",
                    "former_federal_capital.png": "Ehemalige Bundeshauptstadt Krone"
                },
                "orientation_location_circle": {
                    "north.png": "Nördlicher Lagekreis",
                    "south.png": "Südlicher Lagekreis",
                    "east.png": "Östlicher Lagekreis",
                    "west.png": "Westlicher Lagekreis",
                    "northeast.png": "Nordöstlicher Lagekreis",
                    "northwest.png": "Nordwestlicher Lagekreis",
                    "southeast.png": "Südöstlicher Lagekreis",
                    "southwest.png": "Südwestlicher Lagekreis",
                    "central.png": "Zentraler Lagekreis",
                    "city_state.png": "Stadtstaat Lagekreis"
                },
                "state_background": {
                    "Bayern.png": "Bayern Bundeslandshintergrund",
                    "Berlin.png": "Berlin Bundeslandshintergrund",
                    "Baden-Württemberg.png": "Baden-Württemberg Bundeslandshintergrund"
                }
            }
        
        return descriptions.get(component_type, {}).get(filename, f"{component_type} component")
    
    def _submit_answer(self, quiz_key: str, user_answer: Any):
        """Submit and evaluate an answer."""
        language = st.session_state.get("selected_language", "German")
        quiz_state = st.session_state[quiz_key]
        question_data = quiz_state["current_question"]
        
        if not question_data:
            error_text = "No question available for evaluation." if language == "English" else "Keine Frage zum Bewerten verfügbar."
            st.error(error_text)
            return
        
        # Evaluate the answer
        spinner_text = "Evaluating answer..." if language == "English" else "Bewerte Antwort..."
        with st.spinner(spinner_text):
            feedback = self.quiz_system.evaluate_answer(question_data, user_answer)
        
        # Update quiz state
        quiz_state["answered"] = True
        quiz_state["feedback"] = feedback
        quiz_state["attempts"] += 1
        
        if feedback.get("is_correct", False):
            quiz_state["correct_answers"] += 1
        
        # Rerun to show feedback
        st.rerun()
    
    def _render_feedback(self, feedback: Dict[str, Any]):
        """Render feedback for an answer."""
        is_correct = feedback.get("is_correct", False)
        feedback_text = feedback.get("feedback", "Keine Rückmeldung verfügbar.")
        
        if is_correct:
            st.success(feedback_text)
        else:
            st.error(feedback_text)
        
        # Show score for open-ended questions
        if "score" in feedback:
            score = feedback["score"]
            if score >= 80:
                st.success(f"**Bewertung:** {score}/100 Punkte")
            elif score >= 60:
                st.warning(f"**Bewertung:** {score}/100 Punkte")
            else:
                st.error(f"**Bewertung:** {score}/100 Punkte")
    
    def _render_post_feedback_actions(self, quiz_key: str, goal_index: int):
        """Render action buttons after showing feedback."""
        language = st.session_state.get("selected_language", "German")
        
        st.markdown("---")
        question_text = "### What would you like to do next?" if language == "English" else "### Was möchten Sie als nächstes tun?"
        st.markdown(question_text)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_question_text = "🔄 New Question" if language == "English" else "🔄 Neue Frage"
            if st.button(new_question_text, key=f"{quiz_key}_new_question", use_container_width=True):
                # Reset for new question
                quiz_state = st.session_state[quiz_key]
                quiz_state["current_question"] = None
                quiz_state["answered"] = False
                quiz_state["feedback"] = None
                st.rerun()
        
        with col2:
            reread_text = "📚 Read Again" if language == "English" else "📚 Nochmal lesen"
            if st.button(reread_text, key=f"{quiz_key}_reread", use_container_width=True):
                # Go back to information phase
                st.session_state.learning_phase = "information"
                st.rerun()
        
        with col3:
            # Check if this is the last goal
            from .learning_goals_manager import LearningGoalsManager
            goals_manager = LearningGoalsManager()
            goals = goals_manager.get_learning_goals()
            
            if goal_index + 1 < len(goals):
                next_goal_text = "➡️ Next Learning Goal" if language == "English" else "➡️ Nächstes Lernziel"
                if st.button(next_goal_text, key=f"{quiz_key}_next_goal", use_container_width=True):
                    st.session_state.current_goal_index += 1
                    st.session_state.learning_phase = "information"
                    st.rerun()
            else:
                complete_text = "🎉 Complete" if language == "English" else "🎉 Abschließen"
                if st.button(complete_text, key=f"{quiz_key}_complete", use_container_width=True):
                    st.session_state.page_mode = "checklist"
                    success_text = "🎉 Congratulations! You have completed all learning goals!" if language == "English" else "🎉 Herzlichen Glückwunsch! Sie haben alle Lernziele durchlaufen!"
                    st.success(success_text)
                    st.rerun()
    
    def render_quiz_statistics(self, user_id: str):
        """Render quiz statistics and progress."""
        st.markdown("### 📊 Quiz Statistiken")
        
        # Collect statistics from session state
        total_attempts = 0
        total_correct = 0
        goals_attempted = 0
        
        for key, value in st.session_state.items():
            if key.startswith("quiz_") and isinstance(value, dict):
                if value.get("attempts", 0) > 0:
                    goals_attempted += 1
                    total_attempts += value.get("attempts", 0)
                    total_correct += value.get("correct_answers", 0)
        
        if total_attempts > 0:
            accuracy = (total_correct / total_attempts) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Lernziele bearbeitet", goals_attempted)
            
            with col2:
                st.metric("Gesamte Versuche", total_attempts)
            
            with col3:
                st.metric("Richtige Antworten", total_correct)
            
            with col4:
                st.metric("Genauigkeit", f"{accuracy:.1f}%")
        else:
            st.info("Noch keine Quiz-Aktivität vorhanden.")
