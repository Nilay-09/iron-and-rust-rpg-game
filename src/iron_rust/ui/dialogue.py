from time import sleep

from InquirerPy import inquirer
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.text import Text

console = Console()


class Dialogue:

    @staticmethod
    def clear():
        console.clear()

    @staticmethod
    def pause(seconds=0.6):
        sleep(seconds)

    @staticmethod
    def divider():
        console.rule(style="grey50")

    @staticmethod
    def narrator(text: str):
        console.print()
        console.print(Align.center(Text(text, style="italic dim")))
        sleep(0.8)

    @staticmethod
    def say(text: str, style="bold yellow", speed=0.025):
        console.print()

        for ch in text:
            console.print(ch, end="", style=style)
            sleep(speed)

        console.print("\n")

    @staticmethod
    def ask(question: str) -> str:
        Dialogue.say(question, "bold cyan")
        try:
            answer = Prompt.ask("[bold green]➜[/bold green]")
        except EOFError:                      # no input stream (piped/closed)
            return ""
        return (answer or "").strip()

    @staticmethod
    def ask_int(question: str) -> int:
        Dialogue.say(question, "bold cyan")
        # IntPrompt re-prompts on non-numbers; we guard the no-input case.
        try:
            return IntPrompt.ask("[bold green]➜[/bold green]")
        except EOFError:
            return 0

    @staticmethod
    def press_enter(prompt: str = ""):
        """A resilient 'press Enter to continue' that never crashes on EOF."""
        try:
            console.input(prompt)
        except EOFError:
            pass

    @staticmethod
    def choose(question, options, labels=None):
        choices = []

        for option in options:
            label = labels.get(option, option) if labels else option
            choices.append({"name": label, "value": option})

        try:
            return inquirer.select(
                message=question,
                choices=choices,
                pointer="❯",
                instruction="Use ↑ ↓ and ENTER",
                cycle=True,
                vi_mode=False,
            ).execute()
        except EOFError:                      # no interactive stream -> safe default
            return options[0] if options else None

    @staticmethod
    def success(text):
        console.print(f"[bold green]✓ {text}[/bold green]")
        sleep(.7)

    @staticmethod
    def panel(title, text):
        console.print()

        console.print(
            Panel.fit(
                text,
                title=f"[bold yellow]{title}[/bold yellow]",
                border_style="yellow",
                padding=(1, 4),
            )
        )

        console.print()
