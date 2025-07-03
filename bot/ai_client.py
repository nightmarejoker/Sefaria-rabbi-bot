"""
OpenAI client for AI-powered Discord responses
"""
import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIClient:
    """Client for OpenAI API interactions"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        # Default system prompt - will be customizable
        self.system_prompt = """You are a helpful Discord bot assistant specializing in Jewish texts and wisdom. You are knowledgeable about Torah, Talmud, Jewish philosophy, and religious practices. 

When users ask questions:
- Provide thoughtful, respectful responses
- Reference relevant Jewish texts when appropriate
- Be concise but informative
- Maintain a warm, educational tone
- If unsure about religious rulings, recommend consulting a rabbi

Keep responses under 2000 characters to fit Discord's message limits."""
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt"""
        self.system_prompt = prompt
        logger.info("System prompt updated")
    
    async def generate_response(self, user_message: str, user_name: str = "") -> str:
        """Generate an AI response to a user message"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,  # Keep responses reasonable for Discord
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "I'm sorry, I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I'm sorry, I'm having trouble responding right now. Please try again later."
    
    async def generate_contextual_response(self, user_message: str, context: str = "", user_name: str = "") -> str:
        """Generate a response with additional context"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if context:
                messages.append({"role": "assistant", "content": f"Context: {context}"})
            
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating contextual AI response: {e}")
            return "I'm sorry, I'm having trouble responding right now. Please try again later."