"""
AI Client Configuration - Works with GitHub Models or Groq
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "github")

def get_ai_client():
    """Returns configured AI client based on provider"""
    if AI_PROVIDER == "github":
        return OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=os.getenv("GITHUB_TOKEN")
        ), os.getenv("GITHUB_MODEL", "gpt-4o-mini")
    elif AI_PROVIDER == "groq":
        return Groq(api_key=os.getenv("GROQ_API_KEY")), "llama-3.1-70b-versatile"
    else:
        raise ValueError(f"Unknown AI provider: {AI_PROVIDER}")

def call_ai(system_prompt, user_prompt, temperature=0.7):
    """Simple AI call wrapper"""
    client, model = get_ai_client()
    
    try:
        if AI_PROVIDER == "github":
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
        else:  # groq
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling AI: {e}")
        return f"ERROR: {str(e)}"
