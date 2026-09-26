from mcp_server.utils.github_client import parse_repo_url, github_get, decode_base64_content


def get_readme(repo_url: str) -> dict:
    """
    Get the README content of a GitHub repository.
    """
    owner, repo = parse_repo_url(repo_url)

    data = github_get(f"/repos/{owner}/{repo}/readme")

    content = decode_base64_content(data["content"])

    return {
        "file_name": data["name"],
        "path": data["path"],
        "content": content,
        "size": data["size"]
    }