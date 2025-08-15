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
        
        if question_type == "multiple_choice":
            self._render_multiple_choice(question_data, quiz_key)
        elif question_type == "open_ended":
            self._render_open_ended(question_data, quiz_key)
        elif question_type == "true_false":
            self._render_true_false(question_data, quiz_key)
        elif question_type == "fill_blank":
            self._render_fill_blank(question_data, quiz_key)
        else:
            st.error(f"Unbekannter Fragetyp: {question_type}")
    
    def _render_multiple_choice(self, question_data: Dict[str, Any], quiz_key: str):
        """Render a multiple choice question."""
        language = st.session_state.get("selected_language", "German")
        
        header_text = "#### 🔘 Multiple Choice"
        st.markdown(header_text)
        
        no_question_text = "No question available" if language == "English" else "Keine Frage verfügbar"
        st.markdown(question_data.get("question", no_question_text))
        
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
    
    def _render_open_ended(self, question_data: Dict[str, Any], quiz_key: str):
        """Render an open-ended question."""
        language = st.session_state.get("selected_language", "German")
        
        header_text = "#### ✍️ Open Question" if language == "English" else "#### ✍️ Offene Frage"
        st.markdown(header_text)
        
        no_question_text = "No question available" if language == "English" else "Keine Frage verfügbar"
        st.markdown(question_data.get("question", no_question_text))
        
        # Text area for answer
        answer_key = f"{quiz_key}_open_answer"
        label_text = "Your answer:" if language == "English" else "Ihre Antwort:"
        placeholder_text = "Enter your detailed answer here..." if language == "English" else "Geben Sie hier Ihre ausführliche Antwort ein..."
        
        user_answer = st.text_area(
            label_text,
            height=150,
            key=answer_key,
            placeholder=placeholder_text
        )
        
        # Submit button
        submit_text = "Submit Answer" if language == "English" else "Antwort einreichen"
        if st.button(submit_text, key=f"{quiz_key}_submit"):
            if user_answer.strip():
                self._submit_answer(quiz_key, user_answer.strip())
            else:
                warning_text = "Please enter an answer." if language == "English" else "Bitte geben Sie eine Antwort ein."
                st.warning(warning_text)
    
    def _render_true_false(self, question_data: Dict[str, Any], quiz_key: str):
        """Render a true/false question."""
        language = st.session_state.get("selected_language", "German")
        
        header_text = "#### ✅❌ True or False" if language == "English" else "#### ✅❌ Richtig oder Falsch"
        st.markdown(header_text)
        
        no_statement_text = "No statement available" if language == "English" else "Keine Aussage verfügbar"
        st.markdown(question_data.get("question", no_statement_text))
        
        # Radio buttons for true/false
        answer_key = f"{quiz_key}_tf_answer"
        radio_label = "Is this statement true or false?" if language == "English" else "Ist diese Aussage richtig oder falsch?"
        
        if language == "English":
            format_func = lambda x: "True" if x else "False"
        else:
            format_func = lambda x: "Richtig" if x else "Falsch"
        
        selected_answer = st.radio(
            radio_label,
            [True, False],
            format_func=format_func,
            key=answer_key
        )
        
        # Submit button
        submit_text = "Submit Answer" if language == "English" else "Antwort einreichen"
        if st.button(submit_text, key=f"{quiz_key}_submit"):
            self._submit_answer(quiz_key, selected_answer)
    
    def _render_fill_blank(self, question_data: Dict[str, Any], quiz_key: str):
        """Render a fill-in-the-blank question."""
        language = st.session_state.get("selected_language", "German")
        
        header_text = "#### 📝 Fill in the Blanks" if language == "English" else "#### 📝 Lückentext"
        st.markdown(header_text)
        
        no_question_text = "No question available" if language == "English" else "Keine Frage verfügbar"
        question_text = question_data.get("question", no_question_text)
        blank_count = question_text.count("_____")
        
        st.markdown(question_text)
        
        # Input fields for each blank
        answers = []
        for i in range(blank_count):
            if language == "English":
                label = f"Blank {i+1}:"
                placeholder = f"Answer for blank {i+1}"
            else:
                label = f"Lücke {i+1}:"
                placeholder = f"Antwort für Lücke {i+1}"
            
            answer = st.text_input(
                label,
                key=f"{quiz_key}_blank_{i}",
                placeholder=placeholder
            )
            answers.append(answer)
        
        # Submit button
        submit_text = "Submit Answer" if language == "English" else "Antwort einreichen"
        if st.button(submit_text, key=f"{quiz_key}_submit"):
            if all(answer.strip() for answer in answers):
                self._submit_answer(quiz_key, answers)
            else:
                warning_text = "Please fill in all blanks." if language == "English" else "Bitte füllen Sie alle Lücken aus."
                st.warning(warning_text)
    
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
