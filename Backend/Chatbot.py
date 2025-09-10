# In Backend/Chatbot.py

from groq import Groq
from dotenv import dotenv_values
import json

# --- CHATBOT WITH PERSONALITY AND MEMORY ---

env_vars = dotenv_values(".env")
GroqApiKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqApiKey)

# IMPROVED: Personality prompt for a witty, Jarvis-like AI
SystemPrompt = [{
    "role": "system",
    "content": """
    You are Ezio, a witty and humorous AI assistant inspired by Jarvis from Iron Man.
    - Your personality is clever, slightly sarcastic, and exceptionally helpful.
    - Keep your responses concise and to the point, but with a touch of wit.
    - Never mention that you are an AI or a language model. You are Ezio.
    - Address the user by their name, which is Anshul.
    - Use humor and clever remarks, but always remain helpful and polite.
    """
}]

def ChatBot(query):
    # IMPROVED: Now includes conversational memory
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as f:
            chat_log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        chat_log = []

    # Keep the last 4 messages for context (2 user, 2 assistant)
    recent_history = chat_log[-4:]
    
    # Add the new query to the history
    recent_history.append({"role": "user", "content": query})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemPrompt + recent_history,
            max_tokens=2048,
        )
        answer = completion.choices[0].message.content

        # Save the new exchange to the chat log
        chat_log.append({"role": "user", "content": query})
        chat_log.append({"role": "assistant", "content": answer})
        with open(r'Data\ChatLog.json', 'w', encoding='utf-8') as f:
            json.dump(chat_log, f, indent=4)

        return answer
    except Exception as e:
        print(f"Error in ChatBot: {e}")
        return "I seem to be having trouble connecting. Please check my connection."
