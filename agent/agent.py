import json
import anyio

from mcp import Client, StdioServerParameters
from agent.llm_provider import convert_mcp_tools_to_openai_format, call_llm

SYSTEM_PROMPT = (
    "You are RepoLens, a terminal-based GitHub repository analyzer. "
    "When giving your final answer, write in plain text only. "
    "Do not use markdown formatting: no asterisks for bold, no pound signs for headers, "
    "no HTML tags like <br>, no markdown tables. "
    "Use plain paragraphs, and simple dashes (-) for lists. "
    "Keep it clean and readable in a plain terminal."
)




server = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"],
)

import re

def clean_output(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\|", " ", text)
    return text.strip()

async def run_agent(user_message: str) -> str:
    async with Client(server) as mcp_client:

        mcp_tools_result = await mcp_client.list_tools()
        tools = convert_mcp_tools_to_openai_format(mcp_tools_result.tools)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        while True:
            response = call_llm(messages, tools)
            choice = response.choices[0]
            message = choice.message

            messages.append(message.model_dump(exclude_none=True))

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"  [Agent is calling tool: {tool_name}({tool_args})]")

                    tool_result = await mcp_client.call_tool(tool_name, tool_args)
                    result_text = tool_result.content[0].text

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text
                    })
            else:
                return clean_output(message.content)


if __name__ == "__main__":
    print("=" * 50)
    print("  RepoLens — AI-Powered GitHub Repo Analyzer")
    print("=" * 50)
    print("Paste a GitHub repository URL, then tell me what you want to know.")
    print("Type 'exit' to quit.\n")

    while True:
        repo_url = input("Repo URL: ").strip()

        if repo_url.lower() == "exit":
            print("Goodbye!")
            break

        question = input("What do you want to know about it? ").strip()

        while not question:
            question = input("Please enter a question: ").strip()

        user_message = f"Repository: {repo_url}\n\nQuestion: {question}"

        print("\nAnalyzing repository, please wait...\n")

        answer = anyio.run(run_agent, user_message)

        print("-" * 50)
        print(answer)
        print("-" * 50 + "\n")