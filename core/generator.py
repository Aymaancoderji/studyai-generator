import json
from typing import Dict, List
from core.ai_providers import AIProvider

class StudyMaterialGenerator:
    """Generate various study materials from content."""
    
    def __init__(self, provider: AIProvider):
        self.provider = provider
    
    def generate_flashcards(self, content: str, count: int = 20) -> Dict:
        """Generate flashcards from content."""
        system_prompt = """You are an expert educational content creator. 
Generate high-quality flashcards that test key concepts and understanding.
Return ONLY valid JSON format with no additional text."""
        
        prompt = f"""Based on the following content, generate exactly {count} flashcards.

Content:
{content}

Return a JSON object with this structure:
{{
    "flashcards": [
        {{
            "question": "Question text here",
            "answer": "Answer text here",
            "difficulty": "easy|medium|hard",
            "topic": "Main topic"
        }}
    ]
}}

Focus on key concepts, definitions, and important relationships. Make questions clear and answers concise."""
        
        response, metrics = self.provider.generate(prompt, system_prompt)
        
        try:
            # Try to extract JSON from response
            result = self._extract_json(response)
            result['metrics'] = metrics
            return result
        except json.JSONDecodeError as e:
            # Fallback: create a structured response
            return {
                'flashcards': [{'question': 'Error parsing response', 'answer': str(e), 'difficulty': 'error', 'topic': 'error'}],
                'metrics': metrics,
                'raw_response': response
            }
    
    def generate_quiz(self, content: str, count: int = 10) -> Dict:
        """Generate multiple choice quiz questions."""
        system_prompt = """You are an expert at creating educational assessments.
Generate challenging but fair multiple choice questions.
Return ONLY valid JSON format with no additional text."""
        
        prompt = f"""Based on the following content, generate exactly {count} multiple choice quiz questions.

Content:
{content}

Return a JSON object with this structure:
{{
    "quiz": [
        {{
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Why this is correct",
            "difficulty": "easy|medium|hard",
            "topic": "Main topic"
        }}
    ]
}}

Make distractors plausible but clearly wrong. Include explanations for correct answers."""
        
        response, metrics = self.provider.generate(prompt, system_prompt)
        
        try:
            result = self._extract_json(response)
            result['metrics'] = metrics
            return result
        except json.JSONDecodeError as e:
            return {
                'title': 'Error',
                'overview': 'Error parsing response',
                'sections': [],
                'learning_objectives': [str(e)],
                'review_questions': [],
                'metrics': metrics,
                'raw_response': response
            }
    
    def _extract_json(self, response: str) -> Dict:
        """Extract JSON from response, handling markdown code blocks."""
        # Remove markdown code blocks if present
        if '```json' in response:
            response = response.split('```json')[1].split('```')[0]
        elif '```' in response:
            response = response.split('```')[1].split('```')[0]
        
        # Clean up
        response = response.strip()
        
        # Parse JSON
        return json.loads(response)json(response)
            result['metrics'] = metrics
            return result
        except json.JSONDecodeError as e:
            return {
                'quiz': [{'question': 'Error parsing response', 'options': [], 'correct_answer': 0, 'explanation': str(e), 'difficulty': 'error', 'topic': 'error'}],
                'metrics': metrics,
                'raw_response': response
            }
    
    def generate_summary(self, content: str, length: str = 'medium') -> Dict:
        """Generate a summary of the content."""
        length_guide = {
            'short': '2-3 sentences',
            'medium': '1 paragraph (5-7 sentences)',
            'long': '2-3 paragraphs'
        }
        
        system_prompt = """You are an expert at creating clear, concise summaries.
Extract the most important information and present it coherently.
Return ONLY valid JSON format with no additional text."""
        
        prompt = f"""Summarize the following content in {length_guide.get(length, length_guide['medium'])}.

Content:
{content}

Return a JSON object with this structure:
{{
    "summary": "Your summary here",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "main_topics": ["Topic 1", "Topic 2"],
    "word_count": <number>
}}

Focus on main ideas and critical information."""
        
        response, metrics = self.provider.generate(prompt, system_prompt)
        
        try:
            result = self._extract_json(response)
            result['metrics'] = metrics
            return result
        except json.JSONDecodeError as e:
            return {
                'summary': 'Error parsing response',
                'key_points': [str(e)],
                'main_topics': ['error'],
                'word_count': 0,
                'metrics': metrics,
                'raw_response': response
            }
    
    def generate_study_guide(self, content: str) -> Dict:
        """Generate a comprehensive study guide."""
        system_prompt = """You are an expert educational content organizer.
Create structured study guides that help students learn effectively.
Return ONLY valid JSON format with no additional text."""
        
        prompt = f"""Create a comprehensive study guide based on this content:

Content:
{content}

Return a JSON object with this structure:
{{
    "title": "Study Guide Title",
    "overview": "Brief overview",
    "sections": [
        {{
            "heading": "Section name",
            "content": "Section content",
            "key_terms": ["term1", "term2"]
        }}
    ],
    "learning_objectives": ["Objective 1", "Objective 2"],
    "review_questions": ["Question 1", "Question 2"]
}}"""
        
        response, metrics = self.provider.generate(prompt, system_prompt)
        
        try:
            result = self._extract_
