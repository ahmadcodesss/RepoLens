from mcp_server.utils.github_client import parse_repo_url, github_get


def get_languages(repo_url: str) -> dict:
    
    
    
    
    owner, repo = parse_repo_url(repo_url)

    data = github_get(f"/repos/{owner}/{repo}/languages")

    total_bytes = sum(data.values())

    if total_bytes == 0:
        return {"languages": {}}

    percentages = {
        lang: round((bytes_count / total_bytes) * 100, 1)
        for lang, bytes_count in data.items()
    }

    
    sorted_percentages = dict(
        sorted(percentages.items(), key=lambda item: item[1], reverse=True)
    )

    return {
        "languages": sorted_percentages
    }