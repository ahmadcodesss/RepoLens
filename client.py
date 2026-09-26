import anyio

from mcp import Client, StdioServerParameters


server = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"],
)

REPO_URL = "https://github.com/ahmadcodesss/Smart-Summarizer-Flask-app.git"


async def main():
    async with Client(server) as client:

        # Ask the MCP server what tools it provides
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools.tools:
            print("-", tool.name)

        # 1. Test get_repository
        print("\n--- get_repository ---")
        result = await client.call_tool(
            "get_repository",
            {"repo_url": REPO_URL}
        )
        print(result)

        # 2. Test get_repo_tree
        print("\n--- get_repo_tree ---")
        result = await client.call_tool(
            "get_repo_tree",
            {"repo_url": REPO_URL}
        )
        print(result)

        # 3. Test get_readme
        print("\n--- get_readme ---")
        result = await client.call_tool(
            "get_readme",
            {"repo_url": REPO_URL}
        )
        print(result)


                # 4. Test get_file_content
        print("\n--- get_file_content ---")
        result = await client.call_tool(
            "get_file_content",
            {"repo_url": REPO_URL, "path": "package.json"}
        )
        print(result)


if __name__ == "__main__":
    anyio.run(main)