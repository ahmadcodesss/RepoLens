import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "openai/gpt-oss-120b"


def convert_mcp_tools_to_openai_format(mcp_tools: list) -> list:
    """
    Converts MCP tool definitions into OpenAI/Groq's function-calling format.
    """
    tools = []

    for tool in mcp_tools:
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            }
        })

    return tools


def call_llm(messages: list, tools: list):
    """
    Sends the conversation + available tools to Groq.
    Returns the raw response object.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    return response