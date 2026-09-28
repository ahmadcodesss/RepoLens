from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

LOGO = """╦═╗╔═╗╔═╗╔═╗╦  ╔═╗╔╗╔╔═╗
╠╦╝║╣ ╠═╝║ ║║  ║╣ ║║║╚═╗
╩╚═╚═╝╩  ╚═╝╩═╝╚═╝╝╚╝╚═╝"""


def print_banner():
    console.print()
    console.print(Text(LOGO, style="bold cyan"))
    console.print("[white]Ask anything about a GitHub repository[/]  [dim]v0.1[/]")
    console.print("[dim]Paste a repo URL to begin · type 'exit' to quit[/]")
    console.print()


def print_answer(answer: str):
    console.print(
        Panel(Text(answer), title="RepoLens", border_style="cyan", padding=(1, 2))
    )
    console.print()

def print_error(message: str):
    console.print(Panel(Text(message), title="Error", border_style="red", padding=(0, 2)))
    console.print()

