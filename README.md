# RepoLens
[![M8ven Score](https://m8ven.ai/badge/mcp/ahmadcodesss/repolens)](https://m8ven.ai/mcp/ahmadcodesss/repolens?s=readme)
<br>
An AI agent that answers questions about any GitHub repository, straight from your terminal.

## Install

```bash
git clone https://github.com/ahmadcodesss/RepoLens.git
cd RepoLens

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root with your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com/keys).

**Requirements:** Python ≥ 3.10

## Usage

```bash
python -m agent.agent
```

You'll be prompted for a repo URL and a question. RepoLens decides which tools it needs to call to answer — nothing is hardcoded per question type.

### Available Tools

| Tool                    | Description                                               |
| ----------------------- | --------------------------------------------------------- |
| `get_repository`        | Basic repo metadata (stars, forks, language, description) |
| `get_repo_tree`         | Top-level folder structure                                |
| `get_readme`            | README content                                            |
| `get_file_content`      | Contents of a specific file                               |
| `get_languages`         | Language breakdown by percentage                          |
| `list_contributors`     | Top contributors by commit count                          |
| `get_commit_activity`   | Weekly commit activity for the past year                  |
| `get_open_issues_count` | Count of open issues and PRs                              |

## Examples

### Ask what a repository does

```text
Repo URL: https://github.com/facebook/react
Question: what does this project do?
```

### Check repository activity

```text
Repo URL: https://github.com/owner/repo
Question: how actively maintained is this repo?
```

### Get code statistics

```text
Repo URL: https://github.com/owner/repo
Question: what languages does this repository use?
```

Type `exit` at the Repo URL prompt to quit.

## Architecture

```text
RepoLens/
├── agent/          # Reasoning loop — talks to the LLM and orchestrates tool calls
├── mcp_server/     # MCP server exposing the GitHub tools
├── client.py       # MCP client connecting the agent ↔ server
└── requirements.txt
```

Built on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io).

The LLM, powered by [Groq](https://groq.com) using `openai/gpt-oss-120b`, reasons over the available tools and decides its own sequence of calls for each question, rather than following a fixed pipeline.

RepoLens uses the public GitHub API without authentication, so it is subject to GitHub's unauthenticated rate limit of approximately 60 requests per hour.


