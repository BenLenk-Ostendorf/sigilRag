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
                "correct_answers": 0,
                # Adaptive quiz system state
                "asked_questions": [],  # Track all asked questions to avoid repetition
                "difficulty_level": "medium",  # Current difficulty level
                "medium_questions_asked": 0,  # Count of medium difficulty questions
                "medium_questions_correct": 0,  # Count of correct medium questions
                "advancement_phase": "initial",  # initial, second_round, ready_to_advance, recommend_training
                "question_subjects": [],  # Track subjects/topics covered
                "can_retry": False,  # Whether current question can be retried
                "session_complete": False  # Whether this quiz session is complete
            }
        
        quiz_state = st.session_state[quiz_key]
        
        # Check if quiz session is complete
        if quiz_state["session_complete"]:
            self._render_advancement_decision(quiz_state, quiz_key, goal_index)
            return
        
        # Generate new question if needed
        if quiz_state["current_question"] is None or not quiz_state["answered"]:
            if quiz_state["current_question"] is None:
                # Get selected language
                language = st.session_state.get("selected_language", "German")
                spinner_text = "Generating question based on learning material..." if language == "English" else "Generiere Frage basierend auf Lernmaterial..."
                with st.spinner(spinner_text):
                    # Generate adaptive question based on current state
                    quiz_state["current_question"] = self._generate_adaptive_question(
                        learning_goal, goal_index, quiz_state, language
                    )
        
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
        
        # Submit button with retry logic
        quiz_state = st.session_state[quiz_key]
        is_answered = quiz_state.get("answered", False)
        can_retry = quiz_state.get("can_retry", True)
        
        if is_answered and not can_retry:
            # Question was answered correctly, no retry allowed
            disabled_text = "Answer submitted (correct)" if language == "English" else "Antwort eingereicht (richtig)"
            st.button(disabled_text, key=f"{quiz_key}_submit", disabled=True)
        else:
            # First attempt or incorrect answer (retry allowed)
            submit_text = "Submit Answer" if language == "English" else "Antwort einreichen"
            if not is_answered:
                submit_text = "Submit Answer" if language == "English" else "Antwort einreichen"
            else:
                submit_text = "Try Again" if language == "English" else "Nochmal versuchen"
            
            if st.button(submit_text, key=f"{quiz_key}_submit"):
                # Reset answered state for retry
                if is_answered:
                    quiz_state["answered"] = False
                    quiz_state["feedback"] = None
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
    
    def _generate_adaptive_question(self, learning_goal: dict, goal_index: int, quiz_state: dict, language: str):
        """Generate an adaptive question based on current quiz state and progress."""
        # Determine what type of question to generate based on current state
        difficulty = quiz_state["difficulty_level"]
        asked_questions = quiz_state["asked_questions"]
        subjects_covered = quiz_state["question_subjects"]
        
        # Generate question with adaptive parameters
        question_data = self.quiz_system.generate_adaptive_quiz_question(
            learning_goal=learning_goal,
            goal_index=goal_index,
            difficulty_level=difficulty,
            asked_questions=asked_questions,
            subjects_covered=subjects_covered,
            language=language
        )
        
        # Track this question
        if question_data:
            question_hash = self._get_question_hash(question_data)
            quiz_state["asked_questions"].append(question_hash)
            
            # Extract and track subject/topic
            subject = self._extract_question_subject(question_data)
            if subject and subject not in quiz_state["question_subjects"]:
                quiz_state["question_subjects"].append(subject)
        
        return question_data
    
    def _get_question_hash(self, question_data: dict) -> str:
        """Generate a hash for a question to track uniqueness."""
        import hashlib
        question_text = question_data.get("question", "")
        options = str(question_data.get("options", []))
        combined = question_text + options
        return hashlib.md5(combined.encode()).hexdigest()[:8]
    
    def _extract_question_subject(self, question_data: dict) -> str:
        """Extract the main subject/topic from a question."""
        question_text = question_data.get("question", "").lower()
        
        # Define subject keywords for seal components
        subjects = {
            "population_frame": ["population", "bevölkerung", "frame", "rahmen", "einwohner"],
            "capital_crown": ["capital", "hauptstadt", "crown", "krone", "federal", "bundes"],
            "location_circle": ["location", "lage", "circle", "kreis", "orientation", "orientierung"],
            "state_background": ["state", "bundesland", "background", "hintergrund", "color", "farbe"]
        }
        
        for subject, keywords in subjects.items():
            if any(keyword in question_text for keyword in keywords):
                return subject
        
        return "general"
    
    def _render_advancement_decision(self, quiz_state: dict, quiz_key: str, goal_index: int):
        """Render the advancement decision interface based on quiz performance."""
        language = st.session_state.get("selected_language", "German")
        
        medium_correct = quiz_state["medium_questions_correct"]
        medium_asked = quiz_state["medium_questions_asked"]
        phase = quiz_state["advancement_phase"]
        
        if language == "English":
            st.markdown("### 🎯 Quiz Session Complete")
            
            if phase == "ready_to_advance":
                st.success(f"🎉 Excellent! You answered {medium_correct}/{medium_asked} questions correctly!")
                st.markdown("You have demonstrated good understanding of this learning goal.")
                if st.button("Continue to Next Learning Goal", key=f"{quiz_key}_advance"):
                    self._advance_to_next_goal(goal_index)
            
            elif phase == "recommend_training":
                st.warning(f"You answered {medium_correct}/{medium_asked} questions correctly.")
                st.markdown("We recommend reviewing the learning material before advancing.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Review Learning Material", key=f"{quiz_key}_review"):
                        st.session_state.learning_phase = "information"
                        st.rerun()
                with col2:
                    if st.button("Continue Anyway", key=f"{quiz_key}_continue"):
                        self._advance_to_next_goal(goal_index)
        
        else:  # German
            st.markdown("### 🎯 Quiz-Sitzung Abgeschlossen")
            
            if phase == "ready_to_advance":
                st.success(f"🎉 Ausgezeichnet! Sie haben {medium_correct}/{medium_asked} Fragen richtig beantwortet!")
                st.markdown("Sie haben ein gutes Verständnis für dieses Lernziel gezeigt.")
                if st.button("Weiter zum nächsten Lernziel", key=f"{quiz_key}_advance"):
                    self._advance_to_next_goal(goal_index)
            
            elif phase == "recommend_training":
                st.warning(f"Sie haben {medium_correct}/{medium_asked} Fragen richtig beantwortet.")
                st.markdown("Wir empfehlen, das Lernmaterial zu wiederholen, bevor Sie fortfahren.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Lernmaterial wiederholen", key=f"{quiz_key}_review"):
                        st.session_state.learning_phase = "information"
                        st.rerun()
                with col2:
                    if st.button("Trotzdem fortfahren", key=f"{quiz_key}_continue"):
                        self._advance_to_next_goal(goal_index)
    
    def _advance_to_next_goal(self, current_goal_index: int):
        """Advance to the next learning goal and mark current goal as complete."""
        # CRITICAL: Mark the current goal as complete when advancing
        self._mark_goal_as_complete(current_goal_index)
        
        goals = self.quiz_system.learning_goals_manager.get_learning_goals() if hasattr(self.quiz_system, 'learning_goals_manager') else []
        
        if current_goal_index + 1 < len(goals):
            st.session_state.current_goal_index += 1
            st.session_state.learning_phase = "information"
        else:
            st.session_state.page_mode = "checklist"
            language = st.session_state.get("selected_language", "German")
            success_text = "🎉 Congratulations! You have completed all learning goals!" if language == "English" else "🎉 Herzlichen Glückwunsch! Sie haben alle Lernziele durchlaufen!"
            st.success(success_text)
        
        st.rerun()
    
    def _mark_goal_as_complete(self, goal_index: int):
        """Mark a learning goal as complete in the learning goals manager."""
        # Goal IDs are 1-based, so goal_index + 1
        goal_id = goal_index + 1
        user_id = st.session_state.get("user_id", "default_user")
        
        # Get the learning goals manager from the explainer UI
        if hasattr(st.session_state, 'explainer_ui') and hasattr(st.session_state.explainer_ui, 'learning_goals_manager'):
            learning_goals_manager = st.session_state.explainer_ui.learning_goals_manager
        elif hasattr(self.quiz_system, 'learning_goals_manager'):
            learning_goals_manager = self.quiz_system.learning_goals_manager
        else:
            # Import and create if not available
            from .learning_goals_manager import LearningGoalsManager
            learning_goals_manager = LearningGoalsManager()
        
        # Mark the goal as complete in the progress system
        learning_goals_manager.update_goal_progress(user_id, goal_id, True)
        
        # Also update the checkbox state for immediate visual feedback
        checkbox_key = f"goal_checkbox_{goal_id}"
        st.session_state[checkbox_key] = True
    
    def _submit_answer(self, quiz_key: str, user_answer: Any):
        """Submit and evaluate an answer with adaptive quiz logic."""
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
        
        is_correct = feedback.get("is_correct", False)
        if is_correct:
            quiz_state["correct_answers"] += 1
        
        # Update adaptive quiz tracking
        if quiz_state["difficulty_level"] == "medium":
            quiz_state["medium_questions_asked"] += 1
            if is_correct:
                quiz_state["medium_questions_correct"] += 1
        
        # Set retry permission (only for incorrect answers)
        quiz_state["can_retry"] = not is_correct
        
        # Check advancement logic after answering
        self._check_advancement_logic(quiz_state)
        
        # Rerun to show feedback
        st.rerun()
    
    def _check_advancement_logic(self, quiz_state: dict):
        """Check if user should advance based on performance."""
        medium_asked = quiz_state["medium_questions_asked"]
        medium_correct = quiz_state["medium_questions_correct"]
        phase = quiz_state["advancement_phase"]
        
        # Initial phase: First 3 medium questions
        if phase == "initial" and medium_asked >= 3:
            success_rate = medium_correct / medium_asked
            if success_rate >= 0.66:  # 66% or more correct
                quiz_state["advancement_phase"] = "ready_to_advance"
                quiz_state["session_complete"] = True
            else:
                # Reset for second round
                quiz_state["advancement_phase"] = "second_round"
                quiz_state["medium_questions_asked"] = 0
                quiz_state["medium_questions_correct"] = 0
        
        # Second round: Another 3 medium questions
        elif phase == "second_round" and medium_asked >= 3:
            success_rate = medium_correct / medium_asked
            if success_rate >= 0.66:  # 66% or more correct in second round
                quiz_state["advancement_phase"] = "ready_to_advance"
            else:
                quiz_state["advancement_phase"] = "recommend_training"
            quiz_state["session_complete"] = True
    
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
