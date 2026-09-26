from mcp_server.utils.github_client import parse_repo_url, github_get


def get_repository(repo_url: str) -> dict:
    """Get basic information about a GitHub repository."""
    owner, repo = parse_repo_url(repo_url)
    data = github_get(f"/repos/{owner}/{repo}")

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