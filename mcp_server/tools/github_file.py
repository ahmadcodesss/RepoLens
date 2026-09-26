from mcp_server.utils.github_client import parse_repo_url, github_get, decode_base64_content


def get_file_content(repo_url: str, path: str) -> dict:
    """
    Get the content of a specific file in a GitHub repository.

    Args:
        repo_url: The GitHub repository URL
        path: The file path within the repo, e.g. "package.json" or "src/index.js"
    """
    owner, repo = parse_repo_url(repo_url)

    data = github_get(f"/repos/{owner}/{repo}/contents/{path}")

   
    if isinstance(data, list):
        raise ValueError(f"'{path}' is a directory, not a file")

    content = decode_base64_content(data["content"])

    return {
        "file_name": data["name"],
        "path": data["path"],
        "content": content,
        "size": data["size"]
    }