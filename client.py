import anyio

from mcp import Client, StdioServerParameters


server = StdioServerParameters(
    command="python",
    args=["mcp_server/server.py"],
)


async def main():
    async with Client(server) as client:

        # Ask the MCP server what tools it provides
        tools = await client.list_tools()

        print("Available tools:")

        for tool in tools.tools:
            print("-", tool.name)

        # Call our first real RepoLens tool
        result = await client.call_tool(
            "get_repository",
            {
                "repo_url": "https://github.com/facebook/react"
            }
        )

        print("\nRepository information:")
        print(result)


if __name__ == "__main__":
    anyio.run(main)