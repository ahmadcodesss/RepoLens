import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time
from google.genai import errors
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"


def convert_mcp_tools_to_gemini(mcp_tools: list):
    """
    Converts MCP tool definitions (from client.list_tools()) into
    Gemini's FunctionDeclaration format.
    """
    function_declarations = []

    for tool in mcp_tools:
        function_declarations.append(
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or "",
                parameters=tool.input_schema,
            )
        )

    return [types.Tool(function_declarations=function_declarations)]


def call_llm(contents: list, gemini_tools: list, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(tools=gemini_tools)
            )
            return response
        except errors.ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait_time = 30
                print(f"  [Rate limited, waiting {wait_time}s before retry...]")
                time.sleep(wait_time)
            else:
                raise