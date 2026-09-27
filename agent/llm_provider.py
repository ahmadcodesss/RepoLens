import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"


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


def call_llm(contents: list, gemini_tools: list):
    """
    Sends the full conversation + available tools to Gemini.
    Returns Gemini's response object.
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            tools=gemini_tools
        )
    )

    return response