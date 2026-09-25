from urllib.parse import urlparse

import httpx
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError


mcp = MCPServer("RepoLens")


@mcp.tool()
def get_repository(repo_url: str) -> dict:
    """
    Get basic information about a GitHub repository.
    """

    # Parse the GitHub URL
    parsed_url = urlparse(repo_url)

    # Make sure the URL belongs to GitHub
    if parsed_url.netloc != "github.com":
        raise ToolError("Please provide a GitHub repository URL.")

    # Extract owner and repository name
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) != 2:
        raise ToolError(
            "Invalid repository URL. Use: https://github.com/owner/repository"
        )

    owner = path_parts[0]
    repo = path_parts[1].removesuffix(".git")

    # GitHub REST API endpoint
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = httpx.get(
            api_url,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
            },
            timeout=10,
            follow_redirects=True,
        )

        response.raise_for_status()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ToolError("Repository not found on GitHub.")

        raise ToolError(
            f"GitHub API returned status code {e.response.status_code}."
        )

    except httpx.RequestError:
        raise ToolError("Could not connect to the GitHub API.")

    data = response.json()

    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "description": data["description"],
        "language": data["language"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "default_branch": data["default_branch"],
        "is_private": data["private"],
        "html_url": data["html_url"],
    }


if __name__ == "__main__":
    mcp.run()