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

CRITICAL INSTRUCTION: Your question must STRICTLY match the learning goal's intent. Analyze the learning goal carefully:

Here are a few examples:
- If the goal mentions "name" or "identify" components → Ask ONLY for identification/naming (e.g., "What is this component called?")
- If the goal mentions "function" or "purpose" → Ask ONLY about what components do
- If the goal mentions "assembly" or "creation" → Ask ONLY about how to put things together
- If the goal mentions "analysis" or "evaluation" → Ask ONLY about analyzing or comparing
Ensure that you strictly follow the learning goal at hand.

DO NOT mix different types of questions. If the learning goal is about naming components, do NOT ask about function, usage, or selection. Only ask for the name/identification.

Use concrete details, terms, and concepts from the provided text. The question should check whether the student has really read and understood the content.

You can include images in your questions using the placeholder format: {{{{IMAGE:path/filename.png}}}}

AVAILABLE IMAGES:
{available_images}

When asking about component identification/naming, ALWAYS include an image of the component using {{{{IMAGE:path/filename.png}}}} and ask "What is this component called?" or similar identification questions.

Respond in {language}.
"""
    
    # Question type specific prompts
    QUESTION_TYPE_PROMPTS = {
        "multiple_choice": """

Create a multiple-choice question with 4 answer options.

STRICT REQUIREMENT: Your question type must match the learning goal exactly:
- For NAMING/IDENTIFICATION goals: Ask "What is this component called?" with an image
- For FUNCTION goals: Ask "What does this component do?"
- For ASSEMBLY goals: Ask "How is this assembled?"
- For ANALYSIS goals: Ask "How do you analyze this?"

You can include images in your question using: {{{{IMAGE:path/filename.png}}}}
For identification questions, ALWAYS include an image: "What is this component called? {{{{IMAGE:component_type/filename.png}}}}"

Respond in the following JSON format:
{
    "question": "The question here (with optional {{{{IMAGE:path}}}} placeholders)",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Explanation why this answer is correct"
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
    def get_content_based_prompt(cls, goal_description: str, learning_content: str, question_type: str, language: str = "German", available_images: str = "") -> str:
        """Generate a complete prompt for content-based question generation."""
        base_prompt = cls.BASE_CONTENT_PROMPT.format(
            goal_description=goal_description,
            learning_content=learning_content,
            language=language,
            available_images=available_images
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
    
    @classmethod
    def get_available_images_list(cls) -> str:
        """Generate a formatted list of available images for the LLM."""
        import os
        
        # Get project root
        current_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        components_dir = os.path.join(project_root, "data", "sigil_components")
        
        available_images = []
        
        if os.path.exists(components_dir):
            for component_type in os.listdir(components_dir):
                component_path = os.path.join(components_dir, component_type)
                if os.path.isdir(component_path):
                    for image_file in os.listdir(component_path):
                        if image_file.endswith('.png'):
                            relative_path = f"{component_type}/{image_file}"
                            # Create description based on component type and file name
                            description = cls._get_image_description(component_type, image_file)
                            available_images.append(f"- {relative_path}: {description}")
        
        return "\n".join(available_images)
    
    @classmethod
    def _get_image_description(cls, component_type: str, filename: str) -> str:
        """Generate a description for an image based on its type and filename."""
        descriptions = {
            "population_frame": {
                "medium_city.png": "Population frame for cities with less than 500,000 inhabitants",
                "large_city.png": "Population frame for cities with 500,000 to 1 million inhabitants", 
                "mega_city.png": "Population frame for cities with over 1 million inhabitants"
            },
            "capital_crown": {
                "federal_capital.png": "Crown for federal capitals",
                "state_capital.png": "Crown for state capitals",
                "former_federal_capital.png": "Crown for former federal capital (Bonn)"
            },
            "orientation_location_circle": {
                "north.png": "Location circle for northern position",
                "south.png": "Location circle for southern position",
                "east.png": "Location circle for eastern position",
                "west.png": "Location circle for western position",
                "northeast.png": "Location circle for northeastern position",
                "northwest.png": "Location circle for northwestern position",
                "southeast.png": "Location circle for southeastern position",
                "southwest.png": "Location circle for southwestern position",
                "central.png": "Location circle for central position",
                "city_state.png": "Location circle for city-states"
            },
            "state_background": {
                "Bayern.png": "State background for Bavaria",
                "Berlin.png": "State background for Berlin",
                "Baden-Württemberg.png": "State background for Baden-Württemberg",
                "Brandenburg.png": "State background for Brandenburg",
                "Bremen.png": "State background for Bremen",
                "Hamburg.png": "State background for Hamburg",
                "Hessen.png": "State background for Hesse",
                "Mecklenburg-Vorpommern.png": "State background for Mecklenburg-Vorpommern",
                "Niedersachsen.png": "State background for Lower Saxony",
                "Nordrhein-Westfalen.png": "State background for North Rhine-Westphalia",
                "Reinland-Pfalz.png": "State background for Rhineland-Palatinate",
                "Saarland.png": "State background for Saarland",
                "Sachsen.png": "State background for Saxony",
                "Sachsen-Anhalt.png": "State background for Saxony-Anhalt",
                "Schleswig-Holstein.png": "State background for Schleswig-Holstein",
                "Thüringen.png": "State background for Thuringia"
            }
        }
        
        return descriptions.get(component_type, {}).get(filename, f"{component_type} component")


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
