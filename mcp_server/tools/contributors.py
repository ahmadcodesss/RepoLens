from mcp_server.utils.github_client import parse_repo_url, github_get


def list_contributors(repo_url: str, top_n: int = 10) -> dict:
    """
    List the top contributors to a repository, ranked by number of commits.
    """
    owner, repo = parse_repo_url(repo_url)

    data = github_get(
        f"/repos/{owner}/{repo}/contributors",
        params={"per_page": top_n}
    )

    contributors = [
        {"username": c["login"], "contributions": c["contributions"]}
        for c in data
    ]

    return {
        "total_contributors_shown": len(contributors),
        "contributors": contributors
    }