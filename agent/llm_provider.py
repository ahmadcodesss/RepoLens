import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.0-flash"


def call_llm(conversation: list, tools: list):
    """
    Sends the conversation + available tools to Gemini.
    Returns Gemini's response object (caller will inspect it for
    either a text answer or a function call request).
    """
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        tools=tools
    )

    chat = model.start_chat(history=conversation[:-1])
    response = chat.send_message(conversation[-1])

    return response