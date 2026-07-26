"""
Gang Camp — the hero's home base between rides.

Shows funds, morale, and the roster; lets the player fund the gang (raising
morale), buy camp upgrades, and rest up. The Field Infirmary upgrade heals the
hero on arrival.
"""

from rich.panel import Panel
from rich.table import Table

from iron_rust.data.recruits import CAMP_UPGRADES
from iron_rust.entities.gang import Gang
from iron_rust.quests.companion_quests import available_arc
from iron_rust.ui.dialogue import Dialogue, console


def _morale_bar(morale):
    color = "green" if morale >= Gang.BACKUP_THRESHOLD else "yellow" if morale >= 30 else "red"
    filled = max(0, min(10, morale // 10))
    return f"[{color}]{'#' * filled}[/{color}][grey30]{'-' * (10 - filled)}[/grey30] [{color}]{morale}/100[/{color}]"


def _show_status(hero):
    gang = hero.gang

    grid = Table.grid(padding=(0, 2))
    grid.add_column(justify="right", style="bold khaki1")
    grid.add_column()
    grid.add_row("Funds", f"[gold1]${gang.funds}[/gold1]")
    grid.add_row("Morale", _morale_bar(gang.morale))

    backup = "ready" if gang.backup_ready else f"needs morale {Gang.BACKUP_THRESHOLD}+"
    backup_color = "green" if gang.backup_ready else "grey54"
    grid.add_row("Backup", f"[{backup_color}]{backup}[/{backup_color}]")
    grid.add_row("Your purse", f"[gold1]${getattr(hero, 'money', 0)}[/gold1]")

    if gang.members:
        roster = "\n".join(
            f"[cyan]{m.name}[/cyan]  [grey62]{m.role}[/grey62]  "
            f"[magenta]{getattr(m, 'special', '—')}[/magenta]  "
            f"[grey54](loyalty {getattr(m, 'loyalty', 0)})[/grey54]"
            for m in gang.members
        )
    else:
        roster = "[grey54]No one but you. Yet.[/grey54]"
    grid.add_row("Members", roster)

    if gang.upgrades:
        owned = ", ".join(CAMP_UPGRADES[u]["name"] for u in gang.upgrades if u in CAMP_UPGRADES)
        grid.add_row("Upgrades", f"[green]{owned}[/green]")

    console.print()
    console.print(
        Panel(grid, title=f"[bold]{gang.name} — Camp[/bold]", border_style="green", padding=(1, 3))
    )
    console.print()


def _buy_upgrades(hero, dialogue):
    """Knapsack-style: show what's left to buy and what you can afford."""
    gang = hero.gang
    available = [k for k in CAMP_UPGRADES if k not in gang.upgrades]
    if not available:
        dialogue.narrator("The camp wants for nothing more.")
        dialogue.pause(0.6)
        return

    labels = {}
    for k in available:
        up = CAMP_UPGRADES[k]
        affordable = gang.funds >= up["cost"]
        tag = "" if affordable else "  (can't afford)"
        labels[k] = f"${up['cost']:>4}  {up['name']} — {up['desc']}{tag}"
    BACK = "__back__"
    labels[BACK] = "Back"

    choice = dialogue.choose("Spend the war chest on...", available + [BACK], labels=labels)
    if choice == BACK:
        return

    up = CAMP_UPGRADES[choice]
    if gang.buy_upgrade(choice, up["cost"]):
        dialogue.success(f"Bought: {up['name']}.")
    else:
        dialogue.narrator("Not enough in the pot for that.")
    dialogue.pause(0.6)


def camp_menu(hero, dialogue=Dialogue):
    """Interactive camp screen. Returns when the player rides out."""
    gang = hero.gang

    # Field Infirmary heals on arrival.
    if gang.has_upgrade("infirmary") and hero.hp < hero.MAX_HP:
        healed = hero.heal(15)
        if healed:
            console.print(f"[green]The camp infirmary patches you up (+{healed} HP).[/green]", justify="center")

    CONTRIBUTE, UPGRADE, TALK, LEAVE = "contribute", "upgrade", "talk", "leave"

    while True:
        _show_status(hero)

        options = [CONTRIBUTE, UPGRADE]
        labels = {
            CONTRIBUTE: "Put money in the pot (raises morale)",
            UPGRADE: "Buy a camp upgrade (spends gang funds)",
        }
        # Task 10: a member with an un-told story to share around the fire.
        arc = available_arc(hero)
        if arc is not None:
            options.append(TALK)
            labels[TALK] = "Sit with the gang (a companion has a story)"
        options.append(LEAVE)
        labels[LEAVE] = "Ride out"

        choice = dialogue.choose("The camp is quiet. What do you do?", options, labels=labels)

        if choice == LEAVE:
            dialogue.narrator("You leave the fires burning and turn back to the road.")
            dialogue.pause(0.6)
            return

        if choice == UPGRADE:
            _buy_upgrades(hero, dialogue)
            continue

        if choice == TALK:
            _key, quest = arc
            quest.play(hero)
            dialogue.pause(0.4)
            continue

        purse = getattr(hero, "money", 0)
        if purse <= 0:
            dialogue.narrator("Your pockets are empty. Nothing to give.")
            dialogue.pause(0.6)
            continue

        amount = dialogue.ask_int(f"How much of your ${purse} goes to the gang?")
        amount = max(0, min(amount, purse))
        if amount == 0:
            continue

        hero.money -= amount
        gained = gang.contribute(amount)
        dialogue.success(f"${amount} into the pot.")
        if gained > 0:
            console.print(f"[green]Morale +{gained} — the camp feels it.[/green]", justify="center")
        else:
            console.print("[grey54]A drop in the bucket. Morale holds.[/grey54]", justify="center")
        dialogue.pause(0.7)
