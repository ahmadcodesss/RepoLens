from mcp_server.utils.github_client import parse_repo_url, github_get, get_repo_tree_items


def get_repo_tree(repo_url: str) -> dict:
    owner, repo = parse_repo_url(repo_url)

    repo_data = github_get(f"/repos/{owner}/{repo}")
    branch = repo_data["default_branch"]

    files = get_repo_tree_items(owner, repo)

    folder_counts = {}
    for item in files:
        parts = item["path"].split("/")
        top_folder = parts[0] if len(parts) > 1 else "(root)"
        folder_counts[top_folder] = folder_counts.get(top_folder, 0) + 1

    return {
        "branch": branch,
        "total_files": len(files),
        "top_level_structure": folder_counts
    }