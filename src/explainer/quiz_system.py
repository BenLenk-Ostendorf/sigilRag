"""
Quiz system for the explAIner learning flow.
Generates and manages quiz questions for learning goals.
"""

import streamlit as st
from openai import OpenAI
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import os
from .prompts_config import QuizPrompts, PROMPT_CONFIG, LANGUAGE_CONFIG

class QuizSystem:
    """Manages quiz generation, evaluation, and feedback for learning goals."""
    
    def __init__(self):
        """Initialize the quiz system."""
        self.openai_client = None
        self._secrets_loaded = False
        
        # Quiz configuration
        self.quiz_model = "gpt-4"
        self.max_tokens = 800
        self.temperature = 0.7
        
        # Question types (restricted to multiple choice only for simplicity)
        self.question_types = [
            "multiple_choice"
        ]
        
    def _load_api_key(self):
        """Lazy load the OpenAI API key from secrets or environment."""
        if self._secrets_loaded:
            return
            
        try:
            api_key = st.secrets["explainer"]["OPENAI_API_KEY"]
        except KeyError:
            # Fallback to environment variable for development
            api_key = os.getenv("EXPLAINER_OPENAI_API_KEY")
            if not api_key:
                st.warning("⚠️ Quiz system OpenAI API key not found in secrets or environment variables.")
                self._secrets_loaded = True
                return
        
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        
        self._secrets_loaded = True
    
    def generate_quiz_question(self, learning_goal: dict, question_type: str = None, goal_index: int = 0, language: str = None) -> Dict[str, Any]:
        """Generate a quiz question for a specific learning goal based on its content."""
        self._load_api_key()
        
        if not self.openai_client:
            return self._get_fallback_question(learning_goal, language)
        
        # Get language from session state or use default
        if not language:
            language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        
        # Load the actual learning material content
        learning_content = self._load_learning_content(goal_index + 1, language)
        if not learning_content:
            warning_msg = "Could not load learning material for learning goal {}. Using fallback question." if language == "English" else "Konnte Lernmaterial für Lernziel {} nicht laden. Verwende Fallback-Frage."
            st.warning(warning_msg.format(goal_index + 1))
            return self._get_fallback_question(learning_goal, language)
        
        # Select random question type if not specified
        if not question_type:
            question_type = random.choice(self.question_types)
        
        # Get available images list for the LLM
        available_images = QuizPrompts.get_available_images_list()
        
        # Create prompt based on question type and actual content using centralized prompts
        prompt = QuizPrompts.get_content_based_prompt(
            goal_description=learning_goal.get("description", ""),
            learning_content=learning_content,
            question_type=question_type,
            language=language,
            available_images=available_images
        )
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.quiz_model,
                messages=[
                    {"role": "system", "content": QuizPrompts.get_system_prompt("question_generation", language)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse the response
            question_data = json.loads(response.choices[0].message.content)
            question_data["question_type"] = question_type
            question_data["generated_at"] = datetime.now().isoformat()
            question_data["based_on_content"] = True
            question_data["language"] = language
            
            return question_data
            
        except Exception as e:
            error_msg = f"Error generating question: {str(e)}" if language == "English" else f"Fehler beim Generieren der Frage: {str(e)}"
            st.error(error_msg)
            return self._get_fallback_question(learning_goal, language)
    
    def generate_adaptive_quiz_question(self, learning_goal: dict, goal_index: int, difficulty_level: str, 
                                      asked_questions: list, subjects_covered: list, language: str = None) -> Dict[str, Any]:
        """Generate an adaptive quiz question that avoids repetition and varies subjects."""
        self._load_api_key()
        
        if not self.openai_client:
            return self._get_fallback_question(learning_goal, language)
        
        # Get language from session state or use default
        if not language:
            language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        
        # Load the actual learning material content
        learning_content = self._load_learning_content(goal_index + 1, language)
        if not learning_content:
            warning_msg = "Could not load learning material for learning goal {}. Using fallback question." if language == "English" else "Konnte Lernmaterial für Lernziel {} nicht laden. Verwende Fallback-Frage."
            st.warning(warning_msg.format(goal_index + 1))
            return self._get_fallback_question(learning_goal, language)
        
        # Get available images list for the LLM
        available_images = QuizPrompts.get_available_images_list()
        
        # Create adaptive prompt with additional constraints
        adaptive_instructions = self._create_adaptive_instructions(
            difficulty_level, asked_questions, subjects_covered, language
        )
        
        # Create prompt based on question type and actual content using centralized prompts
        base_prompt = QuizPrompts.get_content_based_prompt(
            goal_description=learning_goal.get("description", ""),
            learning_content=learning_content,
            question_type="multiple_choice",  # Only multiple choice for now
            language=language,
            available_images=available_images
        )
        
        # Add adaptive instructions to the prompt
        full_prompt = f"{base_prompt}\n\n{adaptive_instructions}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.quiz_model,
                messages=[
                    {"role": "system", "content": QuizPrompts.get_system_prompt("question_generation", language)},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse the response
            question_data = json.loads(response.choices[0].message.content)
            question_data["question_type"] = "multiple_choice"
            question_data["generated_at"] = datetime.now().isoformat()
            question_data["based_on_content"] = True
            question_data["language"] = language
            question_data["difficulty_level"] = difficulty_level
            question_data["adaptive"] = True
            
            return question_data
            
        except Exception as e:
            error_msg = f"Error generating adaptive question: {str(e)}" if language == "English" else f"Fehler beim Generieren der adaptiven Frage: {str(e)}"
            st.error(error_msg)
            return self._get_fallback_question(learning_goal, language)
    
    def _create_adaptive_instructions(self, difficulty_level: str, asked_questions: list, 
                                    subjects_covered: list, language: str) -> str:
        """Create additional instructions for adaptive question generation."""
        instructions = []
        
        if language == "English":
            instructions.append("ADAPTIVE REQUIREMENTS:")
            
            # Difficulty level instructions
            if difficulty_level == "medium":
                instructions.append("- Generate a MEDIUM difficulty question")
                instructions.append("- Focus on clear identification and basic understanding")
            elif difficulty_level == "hard":
                instructions.append("- Generate a HARD difficulty question")
                instructions.append("- Include more complex scenarios or edge cases")
            
            # Subject variation instructions - be more specific
            if subjects_covered:
                covered_str = ", ".join(subjects_covered)
                instructions.append(f"- AVOID these already covered subjects: {covered_str}")
                instructions.append("- Focus on DIFFERENT components: population frame, capital crown, location circle, state background")
                instructions.append("- If all subjects covered, use different aspects (size, color, position, meaning)")
            else:
                instructions.append("- Vary the component type being tested")
            
            # Repetition avoidance - be more explicit
            if asked_questions:
                instructions.append(f"- CRITICAL: You have already asked {len(asked_questions)} questions")
                instructions.append("- Do NOT repeat similar question patterns or focus areas")
                instructions.append("- Use completely different components, images, or question angles")
                instructions.append("- If asking about the same component type, focus on different aspects")
        
        else:  # German
            instructions.append("ADAPTIVE ANFORDERUNGEN:")
            
            # Difficulty level instructions
            if difficulty_level == "medium":
                instructions.append("- Generiere eine MITTLERE Schwierigkeitsfrage")
                instructions.append("- Fokus auf klare Identifikation und Grundverständnis")
            elif difficulty_level == "hard":
                instructions.append("- Generiere eine SCHWERE Schwierigkeitsfrage")
                instructions.append("- Verwende komplexere Szenarien oder Grenzfälle")
            
            # Subject variation instructions - be more specific
            if subjects_covered:
                covered_str = ", ".join(subjects_covered)
                instructions.append(f"- VERMEIDE diese bereits behandelten Themen: {covered_str}")
                instructions.append("- Fokussiere auf ANDERE Komponenten: Bevölkerungsrahmen, Hauptstadtkrone, Lagekreis, Staatshintergrund")
                instructions.append("- Falls alle Themen behandelt, verwende andere Aspekte (Größe, Farbe, Position, Bedeutung)")
            else:
                instructions.append("- Variiere den Komponententyp, der getestet wird")
            
            # Repetition avoidance - be more explicit
            if asked_questions:
                instructions.append(f"- KRITISCH: Du hast bereits {len(asked_questions)} Fragen gestellt")
                instructions.append("- Wiederhole NICHT ähnliche Fragemuster oder Schwerpunkte")
                instructions.append("- Verwende völlig andere Komponenten, Bilder oder Fragewinkel")
                instructions.append("- Falls du über denselben Komponententyp fragst, fokussiere auf andere Aspekte")
        
        return "\n".join(instructions)
    
    def _create_question_prompt(self, learning_goal: dict, question_type: str) -> str:
        """Create a prompt for generating quiz questions (legacy method)."""
        goal_description = learning_goal.get("description", "")
        goal_details = learning_goal.get("details", "")
        
        return QuizPrompts.get_legacy_prompt(goal_description, goal_details, question_type)
    
    def _load_learning_content(self, goal_number: int, language: str = None) -> str:
        """Load the actual learning material content for a specific goal in the selected language."""
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
                return None
        except Exception as e:
            return None
    
    def _create_content_based_question_prompt(self, learning_goal: dict, learning_content: str, question_type: str) -> str:
        """Create a prompt for generating quiz questions based on actual learning content."""
        goal_description = learning_goal.get("description", "")
        
        return QuizPrompts.get_content_based_prompt(goal_description, learning_content, question_type)
    
    def _get_fallback_question(self, learning_goal: dict, language: str = None) -> Dict[str, Any]:
        """Provide a fallback question when AI generation fails."""
        if not language:
            language = st.session_state.get("selected_language", PROMPT_CONFIG["default_language"])
        
        if language == "English":
            return {
                "question_type": "multiple_choice",
                "question": f"What is the main goal of '{learning_goal.get('description', 'this learning objective')}'?",
                "options": [
                    "Understanding seal components",
                    "Practical application of seals",
                    "Theoretical analysis of seals",
                    "All of the above points"
                ],
                "correct_answer": 3,
                "explanation": "Learning objectives typically include both theoretical understanding and practical application.",
                "generated_at": datetime.now().isoformat(),
                "is_fallback": True,
                "language": language
            }
        else:
            return {
                "question_type": "multiple_choice",
                "question": f"Was ist das Hauptziel von '{learning_goal.get('description', 'diesem Lernziel')}'?",
                "options": [
                    "Das Verständnis der Siegelkomponenten",
                    "Die praktische Anwendung von Siegeln",
                    "Die theoretische Analyse von Siegeln",
                    "Alle oben genannten Punkte"
                ],
                "correct_answer": 3,
                "explanation": "Lernziele umfassen typischerweise sowohl theoretisches Verständnis als auch praktische Anwendung.",
                "generated_at": datetime.now().isoformat(),
                "is_fallback": True,
                "language": language
            }
    
    def evaluate_answer(self, question_data: Dict[str, Any], user_answer: Any) -> Dict[str, Any]:
        """Evaluate a user's answer and provide feedback."""
        question_type = question_data.get("question_type", "multiple_choice")
        
        if question_type == "multiple_choice":
            return self._evaluate_multiple_choice(question_data, user_answer)
        elif question_type == "open_ended":
            return self._evaluate_open_ended(question_data, user_answer)
        elif question_type == "true_false":
            return self._evaluate_true_false(question_data, user_answer)
        elif question_type == "fill_blank":
            return self._evaluate_fill_blank(question_data, user_answer)
        
        return {"is_correct": False, "feedback": "Unbekannter Fragetyp."}
    
    def _evaluate_multiple_choice(self, question_data: Dict[str, Any], user_answer: int) -> Dict[str, Any]:
        """Evaluate a multiple choice answer."""
        correct_answer = question_data.get("correct_answer", 0)
        is_correct = user_answer == correct_answer
        
        if is_correct:
            feedback = f"✅ **Richtig!** {question_data.get('explanation', '')}"
        else:
            correct_option = question_data.get("options", [])[correct_answer] if correct_answer < len(question_data.get("options", [])) else "Unbekannt"
            feedback = f"❌ **Falsch.** Die richtige Antwort ist: {correct_option}\n\n{question_data.get('explanation', '')}"
        
        return {
            "is_correct": is_correct,
            "feedback": feedback,
            "correct_answer": correct_answer
        }
    
    def _evaluate_open_ended(self, question_data: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
        """Evaluate an open-ended answer using AI."""
        self._load_api_key()
        
        if not self.openai_client or not user_answer.strip():
            return {
                "is_correct": False,
                "feedback": "Bitte geben Sie eine Antwort ein." if not user_answer.strip() else "Bewertung nicht verfügbar.",
                "score": 0
            }
        
        try:
            # Get language from question data or session state
            language = question_data.get('language', st.session_state.get("selected_language", PROMPT_CONFIG["default_language"]))
            
            evaluation_prompt = QuizPrompts.get_evaluation_prompt(
                question=question_data.get('question', ''),
                sample_answer=question_data.get('sample_answer', ''),
                key_points=question_data.get('key_points', []),
                user_answer=user_answer,
                language=language
            )
            
            response = self.openai_client.chat.completions.create(
                model=self.quiz_model,
                messages=[
                    {"role": "system", "content": QuizPrompts.get_system_prompt("answer_evaluation", language)},
                    {"role": "user", "content": evaluation_prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            return evaluation
            
        except Exception as e:
            return {
                "is_correct": True,  # Give benefit of doubt
                "feedback": f"Ihre Antwort wurde eingereicht. {question_data.get('explanation', '')}",
                "score": 75
            }
    
    def _evaluate_true_false(self, question_data: Dict[str, Any], user_answer: bool) -> Dict[str, Any]:
        """Evaluate a true/false answer."""
        correct_answer = question_data.get("correct_answer", True)
        is_correct = user_answer == correct_answer
        
        if is_correct:
            feedback = f"✅ **Richtig!** {question_data.get('explanation', '')}"
        else:
            feedback = f"❌ **Falsch.** Die richtige Antwort ist: {'Richtig' if correct_answer else 'Falsch'}\n\n{question_data.get('explanation', '')}"
        
        return {
            "is_correct": is_correct,
            "feedback": feedback,
            "correct_answer": correct_answer
        }
    
    def _evaluate_fill_blank(self, question_data: Dict[str, Any], user_answers: List[str]) -> Dict[str, Any]:
        """Evaluate fill-in-the-blank answers."""
        correct_answers = question_data.get("correct_answers", [])
        
        if len(user_answers) != len(correct_answers):
            return {
                "is_correct": False,
                "feedback": "Bitte füllen Sie alle Lücken aus.",
                "correct_answers": correct_answers
            }
        
        # Check each answer (case-insensitive, trimmed)
        correct_count = 0
        for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
            if user_ans.strip().lower() == correct_ans.strip().lower():
                correct_count += 1
        
        is_correct = correct_count == len(correct_answers)
        
        if is_correct:
            feedback = f"✅ **Richtig!** {question_data.get('explanation', '')}"
        else:
            feedback = f"❌ **Teilweise richtig ({correct_count}/{len(correct_answers)}).** Korrekte Antworten: {', '.join(correct_answers)}\n\n{question_data.get('explanation', '')}"
        
        return {
            "is_correct": is_correct,
            "feedback": feedback,
            "correct_answers": correct_answers,
            "score": (correct_count / len(correct_answers)) * 100
        }
