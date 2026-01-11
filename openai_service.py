from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_ai_response(text: str, is_premium: bool = False) -> str:
    try:
        # Premium users get GPT-4o, Standard gets GPT-3.5-Turbo
        model = "gpt-4o" if is_premium else "gpt-3.5-turbo"
        
        system_prompt = "You are a helpful assistant." 
        if is_premium:
            system_prompt += " You give detailed, high-quality answers."
        else:
            system_prompt += " Keep your answers concise."

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=1000 if is_premium else 200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"
