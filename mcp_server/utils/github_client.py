import base64
import httpx

BASE_URL = "https://api.github.com"


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    parts = repo_url.rstrip("/").split("/")

    if len(parts) < 2 or parts[-2] == "github.com":
        raise ValueError("Invalid GitHub repository URL")

    owner = parts[-2]
    repo = parts[-1].removesuffix(".git")
    return owner, repo


def github_get(path: str, params: dict | None = None) -> dict | list:
    response = httpx.get(
        f"{BASE_URL}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "RepoLens-App"
        },
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json()

def get_repo_tree_items(owner: str, repo: str) -> list:
    repo_data = github_get(f"/repos/{owner}/{repo}")
    branch = repo_data["default_branch"]

    tree_data = github_get(
        f"/repos/{owner}/{repo}/git/trees/{branch}",
        params={"recursive": "1"}
    )

    return [item for item in tree_data["tree"] if item["type"] == "blob"]

def decode_base64_content(encoded_content: str) -> str:
    return base64.b64decode(encoded_content).decode("utf-8")