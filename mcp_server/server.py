from mcp.server.mcpserver import MCPServer

from mcp_server.tools.repo_info import get_repository
from mcp_server.tools.repo_tree import get_repo_tree

mcp = MCPServer("RepoLens")

mcp.tool()(get_repository)
mcp.tool()(get_repo_tree)

if __name__ == "__main__":
    mcp.run()