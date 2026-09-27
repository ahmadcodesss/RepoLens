import os
from groq import Groq
from dotenv import load_dotenv
import time
from groq import APIStatusError

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


def call_llm(messages: list, tools: list, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        except APIStatusError as e:
            if e.status_code in (429, 413) and attempt < max_retries - 1:
                print(f"  [Hit rate/size limit, waiting 20s before retry...]")
                time.sleep(20)
            else:
                raise