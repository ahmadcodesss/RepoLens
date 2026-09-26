from mcp_server.utils.github_client import parse_repo_url, github_get


def get_repo_tree(repo_url: str) -> dict:
    """
    Get the full file/folder structure of a GitHub repository.
    """
    owner, repo = parse_repo_url(repo_url)

    # First, get the repo's default branch
    repo_data = github_get(f"/repos/{owner}/{repo}")
    branch = repo_data["default_branch"]

    # Get the tree (recursive=1 fetches ALL nested files/folders in one call)
    tree_data = github_get(
        f"/repos/{owner}/{repo}/git/trees/{branch}",
        params={"recursive": "1"}
    )

    files = []
    folders = []

    for item in tree_data["tree"]:
        if item["type"] == "blob":  # blob = file
            files.append(item["path"])
        elif item["type"] == "tree":  # tree = folder
            folders.append(item["path"])

    return {
        "branch": branch,
        "total_files": len(files),
        "total_folders": len(folders),
        "files": files,
        "folders": folders,
        "truncated": tree_data.get("truncated", False)
    }