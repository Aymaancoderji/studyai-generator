import time
from typing import Dict, Tuple
from openai import OpenAI
from groq import Groq
from config.settings import (
    OPENAI_API_KEY, GROQ_API_KEY, OPENAI_MODEL, GROQ_MODEL,
    MAX_TOKENS, TEMPERATURE, PRICING
)

class AIProvider:
    """Base class for AI providers."""
    
    def __init__(self, provider_name: str, model: str):
        self.provider_name = provider_name
        self.model = model
        self.response_time = 0
        self.token_usage = 0
        self.cost = 0
    
    def generate(self, prompt: str, system_prompt: str = None) -> Tuple[str, Dict]:
        """Generate content and return response with metrics."""
        raise NotImplementedError
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage."""
        try:
            pricing = PRICING[self.provider_name][self.model]
            input_cost = (input_tokens / 1_000_000) * pricing['input']
            output_cost = (output_tokens / 1_000_000) * pricing['output']
            return input_cost + output_cost
        except KeyError:
            return 0.0

class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self, model: str = OPENAI_MODEL):
        super().__init__('openai', model)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def generate(self, prompt: str, system_prompt: str = None) -> Tuple[str, Dict]:
        """Generate content using OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            self.response_time = time.time() - start_time
            
            # Extract metrics
            usage = response.usage
            self.token_usage = usage.total_tokens
            self.cost = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)
            
            content = response.choices[0].message.content
            
            metrics = {
                'provider': self.provider_name,
                'model': self.model,
                'response_time': self.response_time,
                'token_usage': self.token_usage,
                'input_tokens': usage.prompt_tokens,
                'output_tokens': usage.completion_tokens,
                'cost': self.cost,
                'finish_reason': response.choices[0].finish_reason
            }
            
            return content, metrics
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class GroqProvider(AIProvider):
    """Groq API provider."""
    
    def __init__(self, model: str = GROQ_MODEL):
        super().__init__('groq', model)
        self.client = Groq(api_key=GROQ_API_KEY)
    
    def generate(self, prompt: str, system_prompt: str = None) -> Tuple[str, Dict]:
        """Generate content using Groq."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            self.response_time = time.time() - start_time
            
            # Extract metrics
            usage = response.usage
            self.token_usage = usage.total_tokens
            self.cost = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)
            
            content = response.choices[0].message.content
            
            metrics = {
                'provider': self.provider_name,
                'model': self.model,
                'response_time': self.response_time,
                'token_usage': self.token_usage,
                'input_tokens': usage.prompt_tokens,
                'output_tokens': usage.completion_tokens,
                'cost': self.cost,
                'finish_reason': response.choices[0].finish_reason
            }
            
            return content, metrics
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

def get_provider(provider_name: str, model: str = None) -> AIProvider:
    """Factory function to get the appropriate provider."""
    if provider_name.lower() == 'openai':
        return OpenAIProvider(model or OPENAI_MODEL)
    elif provider_name.lower() == 'groq':
        return GroqProvider(model or GROQ_MODEL)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

def get_all_providers() -> Dict[str, AIProvider]:
    """Get instances of all configured providers."""
    return {
        'openai': OpenAIProvider(),
        'groq': GroqProvider()
    }
