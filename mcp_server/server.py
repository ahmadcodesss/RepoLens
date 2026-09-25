from mcp.server.mcpserver import MCPServer
import httpx

mcp = MCPServer("RepoLens")


@mcp.tool()
def get_repository(repo_url: str) -> dict:
    """
    Get basic information about a GitHub repository.
    """

    parts = repo_url.rstrip("/").split("/")

    if len(parts) < 2 or parts[-2] == "github.com":
        raise ValueError("Invalid GitHub repository URL")

    owner = parts[-2]
    repo = parts[-1].removesuffix(".git")

    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = httpx.get(
        url,
        headers={
            "Accept": "application/vnd.github+json"
        },
        timeout=10
    )

    response.raise_for_status()

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