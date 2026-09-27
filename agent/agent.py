import anyio
from google.genai import types

from mcp import Client, StdioServerParameters
from agent.llm_provider import convert_mcp_tools_to_gemini, call_llm

server = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"],
)


async def run_agent(user_message: str) -> str:
    async with Client(server) as mcp_client:

        mcp_tools_result = await mcp_client.list_tools()
        gemini_tools = convert_mcp_tools_to_gemini(mcp_tools_result.tools)

        contents = [
            types.Content(role="user", parts=[types.Part(text=user_message)])
        ]

        while True:
            response = call_llm(contents, gemini_tools)

            candidate_content = response.candidates[0].content
            contents.append(candidate_content)

            function_call_part = None
            text_parts = []

            for part in candidate_content.parts:
                if part.function_call and part.function_call.name:
                    function_call_part = part
                    break
                elif part.text:
                    text_parts.append(part.text)

            if function_call_part:
                tool_name = function_call_part.function_call.name
                tool_args = dict(function_call_part.function_call.args)

                print(f"  [Agent is calling tool: {tool_name}({tool_args})]")

                tool_result = await mcp_client.call_tool(tool_name, tool_args)
                result_text = tool_result.content[0].text

                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(
                            function_response=types.FunctionResponse(
                                name=tool_name,
                                response={"result": result_text}
                            )
                        )]
                    )
                )
            else:
                return " ".join(text_parts)


if __name__ == "__main__":
    print("=" * 50)
    print("  RepoLens — AI-Powered GitHub Repo Analyzer")
    print("=" * 50)
    print("Paste a GitHub repository URL and I'll break it down for you.")
    print("Type 'exit' to quit.\n")

    while True:
        repo_url = input("Repo URL: ").strip()

        if repo_url.lower() == "exit":
            print("Goodbye!")
            break

        print("\nAnalyzing repository, please wait...\n")

        answer = anyio.run(run_agent, f"Tell me about this GitHub repository: {repo_url}")

        print("-" * 50)
        print(answer)
        print("-" * 50)