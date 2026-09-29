import json
import logging

import anyio

from agent.ui import console, print_banner, print_answer, print_error

from mcp import Client, StdioServerParameters
from agent.error import (
    ModelMisbehaviorError,
    PermanentError,
    ResourceLimitError,
    TransientError,
)
from agent.llm_provider import convert_mcp_tools_to_openai_format, call_llm, open_client

log = logging.getLogger("repolens.agent")

MAX_STEPS = 10
TOTAL_TIMEOUT_SECONDS = 180

SYSTEM_PROMPT = (
    "You are RepoLens, a terminal-based GitHub repository analyzer. "
    "When giving your final answer, write in plain text only. "
    "Do not use markdown formatting: no asterisks for bold, no pound signs for headers, "
    "no HTML tags like <br>, no markdown tables. "
    "Use plain paragraphs, and simple dashes (-) for lists. "
    "Keep it clean and readable in a plain terminal."
)

server = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server.server"],
)

import re

def clean_output(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\|", " ", text)
    return text.strip()


def setup_logging():
    handler = logging.FileHandler("repolens.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger = logging.getLogger("repolens")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False


def announce_wait(delay: float):
    console.print(f"  [dim]Model service busy, retrying in {int(delay)}s...[/]")


async def execute_tool_call(mcp_client, tool_call) -> str:
    name = tool_call.function.name

    try:
        args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        log.warning("Invalid arguments for %s: %r", name, tool_call.function.arguments)
        return "Error: the tool arguments were not valid JSON."

    print(f"  [Agent is calling tool: {name}({args})]")

    try:
        result = await mcp_client.call_tool(name, args)
    except Exception:
        log.exception("Tool call failed: %s", name)
        return "Error: the tool could not be executed."

    text = result.content[0].text if result.content else ""
    if result.is_error:
        log.warning("Tool %s reported an error: %s", name, text)
    return text


async def run_agent(user_message: str) -> str:
    async with open_client() as llm, Client(server) as mcp_client:

        mcp_tools_result = await mcp_client.list_tools()
        tools = convert_mcp_tools_to_openai_format(mcp_tools_result.tools)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        for _ in range(MAX_STEPS):
            response = await call_llm(llm, messages, tools, on_wait=announce_wait)
            message = response.choices[0].message

            messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                return clean_output(message.content or "")

            for tool_call in message.tool_calls:
                content = await execute_tool_call(mcp_client, tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": content
                })

        log.warning("Step limit reached after %d steps", MAX_STEPS)
        messages.append({
            "role": "user",
            "content": "Step limit reached. Answer now using only the information gathered so far."
        })
        response = await call_llm(llm, messages, tools, tool_choice="none", on_wait=announce_wait)
        return clean_output(response.choices[0].message.content or "No answer was produced.")


async def ask(user_message: str) -> str:
    with anyio.fail_after(TOTAL_TIMEOUT_SECONDS):
        return await run_agent(user_message)


def unwrap(exc: BaseException) -> BaseException:
    while hasattr(exc, "exceptions") and len(exc.exceptions) == 1:
        exc = exc.exceptions[0]
    return exc


def describe_error(exc: BaseException) -> str:
    exc = unwrap(exc)

    if isinstance(exc, (PermanentError, ResourceLimitError)):
        return str(exc)
    if isinstance(exc, (TransientError, ModelMisbehaviorError)):
        return f"{exc} Please try again in a minute."
    if isinstance(exc, TimeoutError):
        return "The request took too long and was cancelled. Try a more specific question."

    log.error("Unexpected error", exc_info=exc)
    return "Something unexpected went wrong. Details were written to repolens.log."


URL_PATTERN = re.compile(r"^https?://github\.com/[\w.-]+/[\w.-]+/?$")


def is_valid_repo_url(url: str) -> bool:
    return bool(URL_PATTERN.match(url.rstrip("/").removesuffix(".git")))




def main():
    setup_logging()
    print_banner()

    while True:
        repo_url = console.input("[bold cyan]Repo URL:[/] ").strip()

        if repo_url.lower() == "exit":
            console.print("[dim]Goodbye![/]")
            return

        while not is_valid_repo_url(repo_url):
            console.print("[yellow]That doesn't look like a GitHub repo URL. Example: https://github.com/owner/repo[/]")
            repo_url = console.input("[bold cyan]Repo URL:[/] ").strip()
            if repo_url.lower() == "exit":
                console.print("[dim]Goodbye![/]")
                return

        question = console.input("[bold cyan]Question:[/] ").strip()

        while not question:
            question = console.input("[yellow]Please enter a question:[/] ").strip()

        user_message = f"Repository: {repo_url}\n\nQuestion: {question}"

        console.print("\n[dim]Analyzing repository...[/]\n")

        try:
            answer = anyio.run(ask, user_message)
        except Exception as e:
            print_error(describe_error(e))
            continue

        print_answer(answer)


if __name__ == "__main__":
    main()