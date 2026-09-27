from mcp.server.mcpserver import MCPServer

from mcp_server.tools.repo_info import get_repository
from mcp_server.tools.repo_tree import get_repo_tree
from mcp_server.tools.repo_readme import get_readme
from mcp_server.tools.github_file import get_file_content
from mcp_server.tools.languages import get_languages
from mcp_server.tools.contributors import list_contributors
from mcp_server.tools.commit_activity import get_commit_activity
from mcp_server.tools.open_issues import get_open_issues_count

mcp = MCPServer("RepoLens")

mcp.tool()(get_repository)
mcp.tool()(get_repo_tree)
mcp.tool()(get_readme)
mcp.tool()(get_file_content)
from mcp_server.tools.languages import get_languages
from mcp_server.tools.contributors import list_contributors
from mcp_server.tools.commit_activity import get_commit_activity

from mcp_server.tools.open_issues import get_open_issues_count
if __name__ == "__main__":
    mcp.run()