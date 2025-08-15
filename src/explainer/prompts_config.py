"""
Centralized configuration for all AI prompts used in the quiz system.
This file contains all prompts in one place for easy editing and maintenance.
"""

class QuizPrompts:
    """Configuration class containing all quiz-related prompts."""
    
    # System prompts for different contexts
    SYSTEM_PROMPTS = {
        "question_generation": "You are an expert on seals and create learning questions based on specific learning content. Always respond in {language} and in JSON format.",
        "answer_evaluation": "You are a teacher and evaluate student answers constructively in {language}."
    }
    
    # Base prompt template for content-based question generation
    BASE_CONTENT_PROMPT = """
Create a learning question based on the following learning content:

Learning Goal: {goal_description}

LEARNING CONTENT:
{learning_content}

The question should test understanding of the specific learning content. Use concrete details, terms, and concepts from the provided text. The question should check whether the student has really read and understood the content.

Respond in {language}.
"""
    
    # Question type specific prompts
    QUESTION_TYPE_PROMPTS = {
        "multiple_choice": """

Create a multiple-choice question with 4 answer options.

Respond in the following JSON format:
{
    "question": "The question here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Explanation why this answer is correct"
}
""",
        
        "open_ended": """

Create an open-ended question that requires a detailed answer.

Respond in the following JSON format:
{
    "question": "The question here",
    "sample_answer": "A sample answer",
    "key_points": ["Important point 1", "Important point 2", "Important point 3"],
    "explanation": "What a good answer should contain"
}
""",
        
        "true_false": """

Create a true/false question.

Respond in the following JSON format:
{
    "question": "The statement here",
    "correct_answer": true,
    "explanation": "Explanation why this answer is correct/incorrect"
}
""",
        
        "fill_blank": """

Create a fill-in-the-blank question with 1-3 blanks.

Respond in the following JSON format:
{
    "question": "Text with _____ blanks here",
    "correct_answers": ["Answer for blank 1", "Answer for blank 2"],
    "explanation": "Explanation of the correct answers"
}
"""
    }
    
    # Legacy prompt template (for fallback)
    LEGACY_BASE_PROMPT = """
Create a learning question for the following learning goal:

Learning Goal: {goal_description}
Details: {goal_details}

The question should test understanding of the learning goal and relate to seals, their creation, components, or analysis.

Respond in {language}.
"""
    
    # Answer evaluation prompt template
    ANSWER_EVALUATION_PROMPT = """
Evaluate the following answer to a learning question:

Question: {question}
Sample Answer: {sample_answer}
Key Points: {key_points}

Student's Answer: {user_answer}

Rate the answer on a scale of 0-100 and provide constructive feedback.

Respond in JSON format in {language}:
{{
    "score": 85,
    "is_correct": true,
    "feedback": "Detailed feedback here",
    "missing_points": ["What is missing"],
    "good_points": ["What was good"]
}}
"""
    
    @classmethod
    def get_system_prompt(cls, context: str, language: str = "German") -> str:
        """Get a system prompt for a specific context."""
        prompt = cls.SYSTEM_PROMPTS.get(context, cls.SYSTEM_PROMPTS["question_generation"])
        return prompt.format(language=language)
    
    @classmethod
    def get_content_based_prompt(cls, goal_description: str, learning_content: str, question_type: str, language: str = "German") -> str:
        """Generate a complete prompt for content-based question generation."""
        base_prompt = cls.BASE_CONTENT_PROMPT.format(
            goal_description=goal_description,
            learning_content=learning_content,
            language=language
        )
        
        type_prompt = cls.QUESTION_TYPE_PROMPTS.get(question_type, cls.QUESTION_TYPE_PROMPTS["multiple_choice"])
        
        return base_prompt + type_prompt
    
    @classmethod
    def get_legacy_prompt(cls, goal_description: str, goal_details: str, question_type: str, language: str = "German") -> str:
        """Generate a complete prompt using legacy method (for fallback)."""
        base_prompt = cls.LEGACY_BASE_PROMPT.format(
            goal_description=goal_description,
            goal_details=goal_details,
            language=language
        )
        
        type_prompt = cls.QUESTION_TYPE_PROMPTS.get(question_type, cls.QUESTION_TYPE_PROMPTS["multiple_choice"])
        
        return base_prompt + type_prompt
    
    @classmethod
    def get_evaluation_prompt(cls, question: str, sample_answer: str, key_points: list, user_answer: str, language: str = "German") -> str:
        """Generate a prompt for evaluating open-ended answers."""
        key_points_str = ", ".join(key_points) if key_points else ("No specific points provided" if language == "English" else "Keine spezifischen Punkte angegeben")
        
        return cls.ANSWER_EVALUATION_PROMPT.format(
            question=question,
            sample_answer=sample_answer,
            key_points=key_points_str,
            user_answer=user_answer,
            language=language
        )


class FormalTestPrompts:
    """Configuration class for formal test prompts (future implementation)."""
    
    # Placeholder for formal test prompts
    SYSTEM_PROMPTS = {
        "formal_assessment": "Du bist ein strenger Prüfer und erstellst formale Bewertungsfragen für Siegel-Kenntnisse.",
        "final_evaluation": "Du bewertest finale Prüfungsantworten objektiv und fair."
    }
    
    # TODO: Add formal test prompt templates when implementing test phase
    FORMAL_TEST_PROMPT = """
Erstelle eine formale Prüfungsfrage für die Abschlussbewertung:

Lernziel: {goal_description}
Schwierigkeitsgrad: {difficulty_level}
Zeitlimit: {time_limit} Minuten

Die Frage soll eine eindeutige, objektiv bewertbare Antwort haben.
"""


# Configuration for prompt customization
PROMPT_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 800,
    "model": "gpt-4",
    "default_language": "German",
    "domain": "seal_creation",
    "supported_languages": ["German", "English"]
}

# Language configuration
LANGUAGE_CONFIG = {
    "German": {
        "name": "Deutsch",
        "code": "de",
        "flag": "🇩🇪",
        "country_code": "DE"  # ISO country code for Flags API
    },
    "English": {
        "name": "English", 
        "code": "en",
        "flag": "🇺🇸",
        "country_code": "US"  # ISO country code for Flags API
    }
}


# Utility functions for prompt management
def validate_prompt_template(template: str, required_vars: list) -> bool:
    """Validate that a prompt template contains all required variables."""
    for var in required_vars:
        if f"{{{var}}}" not in template:
            return False
    return True


def get_all_prompts() -> dict:
    """Get all prompts for inspection or debugging."""
    return {
        "quiz_prompts": {
            "system_prompts": QuizPrompts.SYSTEM_PROMPTS,
            "base_content_prompt": QuizPrompts.BASE_CONTENT_PROMPT,
            "question_type_prompts": QuizPrompts.QUESTION_TYPE_PROMPTS,
            "legacy_base_prompt": QuizPrompts.LEGACY_BASE_PROMPT,
            "evaluation_prompt": QuizPrompts.ANSWER_EVALUATION_PROMPT
        },
        "formal_test_prompts": {
            "system_prompts": FormalTestPrompts.SYSTEM_PROMPTS,
            "formal_test_prompt": FormalTestPrompts.FORMAL_TEST_PROMPT
        },
        "config": PROMPT_CONFIG
    }
