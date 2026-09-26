from mcp.server.mcpserver import MCPServer

from mcp_server.tools.repo_info import get_repository
from mcp_server.tools.repo_tree import get_repo_tree
from mcp_server.tools.repo_readme import get_readme

mcp = MCPServer("RepoLens")

mcp.tool()(get_repository)
mcp.tool()(get_repo_tree)
mcp.tool()(get_readme)

if __name__ == "__main__":
    mcp.run()