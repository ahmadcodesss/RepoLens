from mcp_server.utils.github_client import parse_repo_url, github_get


def get_open_issues_count(repo_url: str) -> dict:
    owner, repo = parse_repo_url(repo_url)

    data = github_get(f"/repos/{owner}/{repo}")

    return {
        "open_issues_and_prs_count": data["open_issues_count"]
    }