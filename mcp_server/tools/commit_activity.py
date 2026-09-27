from mcp_server.utils.github_client import parse_repo_url, github_get


def get_commit_activity(repo_url: str) -> dict:
    """
    Get weekly commit activity for the past year — shows whether
    the repo has been actively worked on recently or has gone quiet.
    """
    owner, repo = parse_repo_url(repo_url)

    data = github_get(f"/repos/{owner}/{repo}/stats/commit_activity")

    if not data:
        return {"weekly_commit_counts": [], "total_commits_last_year": 0}

    weekly_counts = [week["total"] for week in data]

    return {
        "weekly_commit_counts": weekly_counts,
        "total_commits_last_year": sum(weekly_counts)
    }