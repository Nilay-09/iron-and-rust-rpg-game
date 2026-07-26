from time import sleep

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text

console = Console()


def typewriter(text: str, style: str = "white", delay: float = 0.04):
    for ch in text:
        console.print(ch, end="", style=style)
        sleep(delay)
    console.print()


def loading_screen():
    with Progress(
        TextColumn("[bold yellow]{task.description}"),
        BarColumn(bar_width=40),
        "[progress.percentage]{task.percentage:>3.0f}%",
        console=console,
    ) as progress:

        task = progress.add_task("Preparing the Frontier...", total=100)

        for _ in range(100):
            sleep(0.015)
            progress.advance(task)


def game_intro():
    console.clear()

    banner = Text(
        "██╗██████╗  ██████╗ ███╗   ██╗\n"
        "██║██╔══██╗██╔═══██╗████╗  ██║\n"
        "██║██████╔╝██║   ██║██╔██╗ ██║\n"
        "██║██╔══██╗██║   ██║██║╚██╗██║\n"
        "██║██║  ██║╚██████╔╝██║ ╚████║\n"
        "╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝\n"
        "██████╗ ██╗   ██╗███████╗████████╗\n"
        "██╔══██╗██║   ██║██╔════╝╚══██╔══╝\n"
        "██████╔╝██║   ██║███████╗   ██║   \n"
        "██╔══██╗██║   ██║╚════██║   ██║   \n"
        "██║  ██║╚██████╔╝███████║   ██║   \n"
        "╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ",
        style="bold red",
    )

    console.print()
    console.print(Align.center(banner))
    console.print(Align.center(Text("A Terminal Western RPG", style="bold yellow")))
    console.print()

    sleep(1)

    loading_screen()

    sleep(0.5)

    console.print()

    typewriter("The year is 1887...", style="bold white", delay=0.06)

    sleep(0.6)

    console.print(Align.center("[dim]The frontier has no king.[/dim]"))
    console.print(Align.center("[dim]Only guns, grit, and survival.[/dim]"))

    sleep(0.8)

    console.print(Align.center("[red]Bandits roam the open plains.[/red]"))
    console.print(Align.center("[yellow]Sheriffs struggle to keep order.[/yellow]"))
    console.print(Align.center("[green]Fortunes wait for those brave enough to claim them.[/green]"))

    sleep(1)

    console.print()
    console.print(Align.center("[bold white]Every stranger has a story...[/bold white]"))

    sleep(0.8)
    console.print(Align.center("[bold white]Every legend starts somewhere...[/bold white]"))

    sleep(1)

    console.print()
    typewriter("Today...", style="bold cyan", delay=0.08)

    sleep(0.7)
    typewriter("YOUR STORY BEGINS.", style="bold yellow", delay=0.09)

    sleep(0.5)
    console.print()

    console.print(
        Align.center(
            Panel.fit(
                "[bold green]Press ENTER to begin your journey[/bold green]",
                border_style="green",
                padding=(1, 10),
            )
        )
    )

    try:
        input()
    except EOFError:
        pass
    console.clear()
